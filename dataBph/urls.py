from django.contrib import admin
from django.urls import path

from . import views

app_name = 'dataBph'

urlpatterns = [
    path('download_data/', views.download_data, name='download_data'),
    path('', views.index, name='index'),
]