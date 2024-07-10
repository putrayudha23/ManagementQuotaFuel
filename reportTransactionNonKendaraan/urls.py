from django.urls import path, include

from . import views

app_name = 'reportTransactionNonKendaraan'

urlpatterns = [
    path('', views.index, name='index'),
]