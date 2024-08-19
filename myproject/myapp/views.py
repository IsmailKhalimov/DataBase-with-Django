from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
import os
import pandas as pd
from .forms import ActionChoiceForm
from django.db import connection, transaction
from django.conf import settings


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


def handle_uploaded_file(file, table_name, is_new_table=False):
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
                values = "', '".join(str(value) for value in row)
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


def upload_file(request):
    if request.method == 'POST':
        form = ActionChoiceForm(request.POST, request.FILES)
        print(request.POST)
        print()
        print(request.FILES)
        if form.is_valid():
            print('lol2')
            action = form.cleaned_data['action']
            file = request.FILES['file']
            if action == 'add':
                table_name = form.cleaned_data['table']
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

                return render(request, 'upload.html', {
                    'form': form,
                    'db_columns': db_columns,
                    'file_columns': file_columns,
                    'table_name': table_name
                })
            else:
                # Логика для создания новой таблицы
                table_name = file.name.split('.')[0]
                handle_uploaded_file(file, table_name, is_new_table=True)
                return render(request, 'upload_success.html', {'table_name': table_name})
        else:
            print(form.errors)
    else:
        form = ActionChoiceForm()
    return render(request, 'upload.html', {'form': form})
