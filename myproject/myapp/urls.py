from django.urls import path, re_path, register_converter
from . import views


urlpatterns = [
    path('', views.index, name='index'),  # http://127.0.0.1:8000
    path('upload/', views.upload_file, name='upload_file'),
]
