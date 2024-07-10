from django.contrib import admin
from django.urls import path

from . import views

app_name = 'dataOffline'

urlpatterns = [
    path('update_uuid/<int:row_id>/', views.update_uuid, name='update_uuid'),
    path('', views.index, name='index'),
]