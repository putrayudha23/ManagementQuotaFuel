from django.contrib import admin
from django.urls import path

from . import views

app_name = 'vehicleTypeMaster'

urlpatterns = [
    path('delete/<int:delete_id>', views.delete, name='delete'),
    path('', views.index, name='index'),
]