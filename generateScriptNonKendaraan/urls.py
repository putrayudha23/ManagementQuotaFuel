from django.urls import path, include

from . import views

app_name = 'generateScriptNonKendaraan'

urlpatterns = [
    path('generate_script/', views.generate_script, name='generate_script'),
    path('encrypt_script_endpoint/', views.encrypt_script_endpoint, name='encrypt_script_endpoint'),
    path('', views.index, name='index'),
]
