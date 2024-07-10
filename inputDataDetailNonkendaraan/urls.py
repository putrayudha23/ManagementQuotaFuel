from django.contrib import admin
from django.urls import path

from . import views

app_name = 'inputDataDetailNonkendaraan'

urlpatterns = [
    path('', views.index, name='index'),
    path('save_non_vehicle_data/', views.save_non_vehicle_data, name='save_non_vehicle_data'),
]
