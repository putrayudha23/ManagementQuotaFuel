from django.contrib import admin
from django.urls import path

from . import views

app_name = 'userSetting'

urlpatterns = [
    path('site_mapping', views.site_mapping, name='site_mapping'),
    path('delete/<int:delete_id>', views.delete, name='delete'),
    path('', views.index, name='index'),
]