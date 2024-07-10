from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'myproject'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('kuotaMaster/', include('kuotaMaster.urls')),
    path('vehicleMaster/', include('vehicleMaster.urls')),
    path('importVehicleMaster/', include('importVehicleMaster.urls')),
    path('vehicleData/', include('vehicleData.urls')),
    path('vehicleTypeMaster/', include('vehicleTypeMaster.urls', namespace='vehicleTypeMaster')),
    path('siteMaster/', include('siteMaster.urls')),
    path('productMaster/', include('productMaster.urls')),
    path('quotaTransaction/', include('quotaTransaction.urls')),
    path('uploadExcelNonkendaraan/', include('uploadExcelNonkendaraan.urls')),
    path('inputDataDetailNonkendaraan/', include('inputDataDetailNonkendaraan.urls')),
    path('uploadSuratRekomNonkendaraan/', include('uploadSuratRekomNonkendaraan.urls')),
    path('dataDetailNonkendaraan/', include('dataDetailNonkendaraan.urls')),
    path('transactionNonkendaraan/', include('transactionNonkendaraan.urls')),
    path('generateScriptNonKendaraan/', include('generateScriptNonKendaraan.urls')),
    path('dataBph/', include('dataBph.urls')),
    path('dataOffline/', include('dataOffline.urls')),
    path('editExcelData/', include('editExcelData.urls')),
    path('unblock/', include('unblock.urls')),
    # path('reportTransactionNonKendaraan/', include('reportTransactionNonKendaraan.urls')),
    path('userSetting/', include('userSetting.urls')),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
]
