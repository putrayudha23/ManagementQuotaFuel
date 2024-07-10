from django.db import models

# Create your models here.
class EditExcelData(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_konsumen = models.CharField(max_length=50, null=True, blank=True)
    site_registration = models.CharField(max_length=50, null=True, blank=True)
    nama = models.CharField(max_length=50, null=True, blank=True)
    nik = models.CharField(max_length=50, null=True, blank=True)
    tgl_akhir_rekom = models.DateField(null=True, blank=True)
    tgl_efektif = models.DateField(null=True, blank=True)
    status = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'EDITEXCELDATA'