from django.contrib import admin
from django.urls import path

from . import views

app_name = 'vehicleData'

urlpatterns = [
    path('media/stnk_images/<str:filename>', views.view_file, name='view_file'),
    path('media/rekom_images/<str:filename>', views.view_file2, name='view_file2'),
    path('export_to_excel/', views.export_to_excel, name='export_to_excel'),  # Add this line
    path('', views.index, name='index'),
]