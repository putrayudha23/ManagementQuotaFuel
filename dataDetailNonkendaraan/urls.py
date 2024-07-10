from django.contrib import admin
from django.urls import path

from . import views

app_name = 'dataDetailNonkendaraan'

urlpatterns = [
    path('update-approved-status/', views.update_approved_status, name='update_approved_status'),
    path('update-disapproved-status/', views.update_disapproved_status, name='update_disapproved_status'),
    path('export-excel/', views.export_data_to_excel, name='export_excel'),
    path('update_non_vehicle/<int:row_id>/', views.update_non_vehicle, name='update_non_vehicle'),
    path('media/RekomDokumen_Nontransportasi/<str:filename>', views.view_file, name='view_file'),
    path('delete/<int:delete_id>', views.delete, name='delete'),
    path('', views.index, name='index'),
]