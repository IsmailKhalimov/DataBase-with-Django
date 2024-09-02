from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
import os
import pandas as pd
from .forms import ActionChoiceForm
from django.db import connection, transaction
from django.conf import settings
import json
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from .models import CustomTable, TableAccess


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def index(request):
    return render(request, 'index.html')


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


@transaction.atomic
def create_table_from_file(df, table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT EXISTS (SELECT FROM pg_tables WHERE "
                       f"schemaname = 'public' AND tablename = '{table_name}');")
        exists = cursor.fetchone()[0]

        if not exists:
            columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
            cursor.execute(f'CREATE TABLE "{table_name}" ({columns});')
            print(f"Таблица {table_name} успешно создана.")

        for _, row in df.iterrows():
            values = "', '".join(str(value) for value in row)
            cursor.execute(f"INSERT INTO \"{table_name}\" VALUES ('{values}');")
        print(f"Данные успешно добавлены в таблицу {table_name}.")


def handle_uploaded_file(file, table_name, is_new_table=False, selected_columns=None):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return HttpResponse("Unsupported file format", status=400)
    if is_new_table:
        create_table_from_file(df, table_name)
    else:
        with connection.cursor() as cursor:
            for _, row in df.iterrows():
                tmp = []
                for i in selected_columns:
                    tmp.append(row[i])
                values = "', '".join(str(value) for value in tmp)
                cursor.execute(f"INSERT INTO \"{table_name}\" VALUES ('{values}');")
        print(f"Данные успешно добавлены в таблицу {table_name}.")


def get_table_columns(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        columns = [row[0] for row in cursor.fetchall()]
    return columns


def upload_success(request):
    return render(request, 'upload_success.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = ActionChoiceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            print('lol2')
            action = form.cleaned_data['action']
            file = request.FILES['file']
            selected_columns_json = request.POST.get('selected_columns')
            selected_columns = json.loads(selected_columns_json) if selected_columns_json else {}

            if action == 'add':
                print('V if')
                table_name = form.cleaned_data['table']
                table = get_object_or_404(CustomTable, name=table_name)

                # Проверка прав доступа пользователя к таблице
                if not request.user.is_superuser:
                    access = TableAccess.objects.filter(user=request.user, table=table, can_access=True).exists()
                    for i in TableAccess.objects.filter(user=request.user):
                        print(str(i).split()[-1])
                    if not access:
                        messages.error(request, "You do not have permission to access this table.")
                        return redirect('upload_file')

                # Загружаем файл
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    return HttpResponse("Unsupported file format", status=400)

                # Получаем список колонок из таблицы базы данных
                db_columns = get_table_columns(table_name)

                # Получаем список колонок из загруженного файла
                file_columns = df.columns.tolist()

                html = '<h2>Match Columns</h2><table><tr><th>DataBase Column</th><th>File Column</th></tr>'
                for db_col in db_columns:
                    html += f'<tr><td>{db_col}</td><td><select name="mapping_{db_col}">'
                    html += '<option value="">-- Select --</option>'
                    for file_col in file_columns:
                        html += f'<option value="{file_col}">{file_col}</option>'
                    html += '</select></td></tr>'
                html += '</table>'
                if selected_columns:
                    handle_uploaded_file(file, table_name, selected_columns=selected_columns)
                    return redirect('upload_success')
                return HttpResponse(html)
            elif action == 'create':
                print('Зашёл в else')
                table_name = file.name.split('.')[0]
                table = CustomTable(name=table_name, created_by=request.user)
                table.save()
                TableAccess.objects.create(user=request.user, table=table, can_access=True)
                handle_uploaded_file(file, table_name, is_new_table=True)
                return redirect('upload_success')
        else:
            print(form.errors)
    else:
        form = ActionChoiceForm(user=request.user)
    return render(request, 'upload.html', {'form': form})
