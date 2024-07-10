from django.contrib import admin
from django.urls import path

from . import views

app_name = 'uploadExcelNonkendaraan'

urlpatterns = [
    path('download-template/', views.download_template, name='download-template'),
    path('nonVehicleMaster.xlsx', views.download_template, name='download-excel'),
    path('import-excel/', views.import_excel, name='import-excel'),
    path('add-data/', views.add_data, name='add-data'),
    path('', views.index, name='index'),
]