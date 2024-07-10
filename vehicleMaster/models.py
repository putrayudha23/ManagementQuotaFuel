from django.db import models

# Create your models here.
from django.db import models

class VehicleTypeMaster(models.Model):
    RowID = models.CharField(max_length=50, primary_key=True)
    number_plat = models.CharField(max_length=20)
    MerkKendaraan = models.CharField(max_length=200, null=True)
    TypeKendaraan = models.CharField(max_length=200, null=True)
    JenisKendaraan = models.CharField(max_length=200, null=True)
    Warna = models.CharField(max_length=20, null=True)
    NamaPemilik = models.CharField(max_length=20, null=True)
    AlamatPemilik = models.TextField(null=True)
    JumlahRoda = models.CharField(max_length=20, null=True)
    TahunPembuatan = models.IntegerField(null=True)
    KapasitasCylinder = models.IntegerField(null=True)
    STNKReady = models.BooleanField()
    vehicletype_kf = models.CharField(max_length=100, null=True)
    vehicletype_id = models.IntegerField(null=True)
    SettingSystem = models.IntegerField()
    Deleted = models.BooleanField()
    UploadedBy = models.CharField(max_length=100)
    UploadedDate = models.DateTimeField(auto_now_add=True)
    ChangedBy = models.CharField(max_length=100, null=True)
    ChangedDate = models.DateTimeField(null=True, auto_now_add=True)
    RekomReady = models.BooleanField(null=True)
    DateValidSTNK = models.DateTimeField()
    block = models.BooleanField(null=True)

    class Meta:
        db_table = 'VEHICLETYPEMASTER'

class LogVehicleTypeMaster(models.Model):
    RowID = models.CharField(max_length=50)
    number_plat = models.CharField(max_length=20)
    MerkKendaraan = models.CharField(max_length=200, null=True)
    TypeKendaraan = models.CharField(max_length=200, null=True)
    JenisKendaraan = models.CharField(max_length=200, null=True)
    Warna = models.CharField(max_length=20, null=True)
    NamaPemilik = models.CharField(max_length=200, null=True)
    AlamatPemilik = models.TextField(null=True)
    JumlahRoda = models.CharField(max_length=20, null=True)
    TahunPembuatan = models.IntegerField(null=True)
    KapasitasCylinder = models.IntegerField(null=True)
    STNKReady = models.BooleanField(default=False)
    vehicletype_kf = models.CharField(max_length=100, null=True)
    vehicletype_id = models.IntegerField(null=True)
    SettingSystem = models.IntegerField()
    Deleted = models.BooleanField(default=False)
    ChangedBy = models.CharField(max_length=100)
    ChangedDate = models.DateTimeField()
    RekomReady = models.BooleanField(null=True)
    DateValidSTNK = models.DateTimeField()
    block = models.BooleanField(null=True)

    class Meta:
        db_table = 'LOGVEHICLETYPEMASTER'

class VehicleMasterView(models.Model):
    RowID = models.CharField(max_length=50, primary_key=True)
    number_plat = models.CharField(max_length=255)
    MerkKendaraan = models.CharField(max_length=255)
    TypeKendaraan = models.CharField(max_length=255)
    JenisKendaraan = models.CharField(max_length=255)
    Warna = models.CharField(max_length=255)
    NamaPemilik = models.CharField(max_length=255)
    AlamatPemilik = models.CharField(max_length=255)
    JumlahRoda = models.CharField(max_length=255)
    TahunPembuatan = models.IntegerField()
    KapasitasCylinder = models.IntegerField()
    STNKReady = models.BooleanField()
    vehicletype_id = models.IntegerField()
    SettingSystem = models.CharField(max_length=255)
    Deleted = models.BooleanField()
    UploadedBy = models.CharField(max_length=255)
    UploadedDate = models.DateTimeField()
    ChangedBy = models.CharField(max_length=255)
    ChangedDate = models.DateTimeField()
    description = models.CharField(max_length=255)
    RekomReady = models.BooleanField()
    DateValidSTNK = models.DateTimeField()
    block = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = 'VehicleMasterView'

