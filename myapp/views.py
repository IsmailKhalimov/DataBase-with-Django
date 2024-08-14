from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, Http404
import pandas as pd
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Person


def index(requests):
    return HttpResponse("Cтраница приложения Myapp.")


def page_not_fount(requests, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def handle_uploaded_file(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return HttpResponse("Unsupported file format", status=400)

    for _, row in df.iterrows():
        Person.objects.create(name=row['ФИО'], left_near=row['ЛБ'], left_far=row['ЛК'],
                              right_near=row['ПБ'], right_far=row['ПК'], free_throw=row['ШТ'])


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponse("File uploaded and data imported successfully")
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


# Create your views here.
