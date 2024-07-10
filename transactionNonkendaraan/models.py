from django.db import models

# Create your models here.
class nonVehicleTransaction(models.Model):
    id = models.BigAutoField(primary_key=True)  # bigint
    no_konsumen = models.CharField(max_length=50)  # nvarchar(50)
    nama = models.CharField(max_length=50)  # nvarchar(50)
    alamat = models.TextField()  # nvarchar(MAX)
    nik = models.CharField(max_length=50)  # nvarchar(50)
    sektor_konsumen = models.CharField(max_length=50, null=True, blank=True)  # nvarchar(50)
    vehicletype_id = models.IntegerField()  # int
    volume_quotaallocated = models.BigIntegerField()  # bigint
    volume_quotaavailable = models.BigIntegerField()  # bigint
    price = models.IntegerField()  # int
    frequency_quota = models.IntegerField()  # int
    site_registration = models.CharField(max_length=50)  # nvarchar(50)
    trnrec = models.BooleanField(default=False)  # bit (assuming it's a boolean)
    tgl_awal_rekom = models.DateField()  # date
    tgl_akhir_rekom = models.DateField()  # date
    nomor_surat = models.CharField(max_length=50)  # nvarchar(50)
    quota_reset_date = models.DateField()  # date

    class Meta:
        db_table = 'NONVEHICLETRANSACTION'
