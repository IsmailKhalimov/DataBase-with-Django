from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, Http404
import pandas as pd
from django.shortcuts import render
from .forms import TableChoiceForm
from .models import Person, Team


def index(request):
    return render(request, 'index.html')


def page_not_fount(requests, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def handle_uploaded_file(file, table_name):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return HttpResponse("Unsupported file format", status=400)

    if table_name == 'Person':
        for _, row in df.iterrows():
            Person.objects.create(
                name=row['ФИО'], left_near=row['ЛБ'], left_far=row['ЛК'],
                right_near=row['ПБ'], right_far=row['ПК'], free_throw=row['ШТ']
            )
    elif table_name == 'Team':
        for _, row in df.iterrows():
            Team.objects.create(
                name=row['Название'], city=row['Город'], championships_won=row['Чемпионства']
            )


def upload_file(request):
    if request.method == 'POST':
        form = TableChoiceForm(request.POST, request.FILES)
        if form.is_valid():
            table_name = form.cleaned_data['table']
            handle_uploaded_file(request.FILES['file'], table_name)
            return render(request, 'upload_success.html', {'table_name': table_name})
    else:
        form = TableChoiceForm()
    return render(request, 'upload.html', {'form': form})


# Create your views here.
