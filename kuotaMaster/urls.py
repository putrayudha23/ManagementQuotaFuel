from django.contrib import admin
from django.urls import path

from . import views

app_name = 'kuotaMaster'

urlpatterns = [
    path('get_site_data/<str:site_name>/', views.get_site_data, name='get_site_data'),
    path('delete/<int:delete_id>', views.delete, name='delete'),
    path('', views.index, name='index'),
]
