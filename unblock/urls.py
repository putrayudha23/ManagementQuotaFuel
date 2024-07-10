from django.contrib import admin
from django.urls import path

from . import views

app_name = 'unblock'

urlpatterns = [
    path('unblock/<str:unblock_id>', views.unblock, name='unblock'),
    path('', views.index, name='index'),
]