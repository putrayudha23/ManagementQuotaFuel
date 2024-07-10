from django.contrib import admin
from django.urls import path
from django.conf.urls import handler404

from . import views

app_name = 'vehicleMaster'

urlpatterns = [
    path('media/stnk_images/<str:filename>', views.view_file, name='view_file'),
    path('media/rekom_images/<str:filename>', views.view_file2, name='view_file2'),
    path('delete/<str:delete_id>', views.delete, name='delete'),
    path('block/<str:block_id>', views.block, name='block'),
    path('', views.index, name='index'),
]

handler404 = views.custom_404