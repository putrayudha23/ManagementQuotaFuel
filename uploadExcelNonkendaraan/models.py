from django.db import models

# Create your models here.
class NonVehicleMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_konsumen = models.CharField(max_length=50, null=True, blank=True)
    site_registration = models.CharField(max_length=50, null=True, blank=True)
    nama = models.CharField(max_length=50, null=True, blank=True)
    nik = models.CharField(max_length=50, null=True, blank=True)
    alamat = models.TextField(null=True, blank=True)
    sektor_konsumen = models.IntegerField(null=True, blank=True)
    nama_kapal = models.CharField(max_length=255, null=True, blank=True)
    jenis_mesin = models.CharField(max_length=50, null=True, blank=True)
    jumlah_mesin = models.IntegerField(null=True, blank=True)
    jumlah_dayaMesin = models.FloatField(null=True, blank=True)
    jam_penggunaan = models.IntegerField(null=True, blank=True)
    klasifikasi_gt = models.IntegerField(null=True, blank=True)
    lama_operasi = models.IntegerField(null=True, blank=True)
    konsumsi_jbt = models.BigIntegerField(null=True, blank=True)
    alokasi_volume = models.FloatField(null=True, blank=True)
    tgl_awal_rekom = models.DateField(null=True, blank=True)
    tgl_akhir_rekom = models.DateField(null=True, blank=True)
    nomor_surat = models.TextField(null=True, blank=True)
    vehicletype_id = models.IntegerField(null=True, blank=True)
    id_product = models.IntegerField(null=True, blank=True)
    dokumen_status = models.BooleanField(null=True, blank=True)
    approved_status = models.BooleanField(null=True, blank=True)
    disapproved_status = models.BooleanField(null=True, blank=True)
    inactive_status = models.BooleanField(null=True, blank=True)
    UploadedBy = models.CharField(max_length=100, null=True, blank=True)
    UploadedDate = models.DateTimeField(null=True, blank=True)
    ChangedBy = models.CharField(max_length=100, null=True, blank=True)
    ChangedDate = models.DateTimeField(null=True, blank=True)
    dokumen_name = models.CharField(max_length=50, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    uuid_kapal = models.CharField(max_length=255, null=True, blank=True)
    badan_usaha = models.CharField(max_length=255, null=True, blank=True)
    nama_usaha = models.CharField(max_length=255, null=True, blank=True)
    jenis_bbm = models.IntegerField(null=True, blank=True)
    jenis_usaha = models.IntegerField(null=True, blank=True)
    kode_provinsi = models.CharField(max_length=50, null=True, blank=True)
    kode_kabkota = models.CharField(max_length=50, null=True, blank=True)
    kode_kecamatan = models.CharField(max_length=50, null=True, blank=True)
    kode_keldesa = models.CharField(max_length=50, null=True, blank=True)
    penerbit = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    url_file = models.CharField(max_length=100, null=True, blank=True)
    flag_status = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'NONVEHICLEMASTER'

# CREATE VIEW View_NONVEHICLEMASTER AS
# SELECT
#     NV.*,
#     JB.jenis_bbm AS jenis_bbm_desc,
#     SK.sektor_konsumen AS sektor_konsumen_desc,
#     JU.jenis_usaha AS jenis_usaha_desc
# FROM
#     NONVEHICLEMASTER NV
# LEFT JOIN
#     JENISBBMMASTER JB ON NV.jenis_bbm = JB.id
# LEFT JOIN
#     SEKTORKONSUMENMASTER SK ON NV.sektor_konsumen = SK.id
# LEFT JOIN
#     JENISUSAHAMASTER JU ON NV.jenis_usaha = JU.id;
        
class ViewNonVehicleMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_konsumen = models.CharField(max_length=50, null=True, blank=True)
    site_registration = models.CharField(max_length=50, null=True, blank=True)
    nama = models.CharField(max_length=50, null=True, blank=True)
    nik = models.CharField(max_length=50, null=True, blank=True)
    alamat = models.TextField(null=True, blank=True)
    sektor_konsumen = models.IntegerField(null=True, blank=True)
    nama_kapal = models.CharField(max_length=255, null=True, blank=True)
    jenis_mesin = models.CharField(max_length=50, null=True, blank=True)
    jumlah_mesin = models.IntegerField(null=True, blank=True)
    jumlah_dayaMesin = models.FloatField(null=True, blank=True)
    jam_penggunaan = models.IntegerField(null=True, blank=True)
    klasifikasi_gt = models.IntegerField(null=True, blank=True)
    lama_operasi = models.IntegerField(null=True, blank=True)
    konsumsi_jbt = models.BigIntegerField(null=True, blank=True)
    alokasi_volume = models.FloatField(null=True, blank=True)
    tgl_awal_rekom = models.DateField(null=True, blank=True)
    tgl_akhir_rekom = models.DateField(null=True, blank=True)
    nomor_surat = models.TextField(null=True, blank=True)
    vehicletype_id = models.IntegerField(null=True, blank=True)
    id_product = models.IntegerField(null=True, blank=True)
    dokumen_status = models.BooleanField(null=True, blank=True)
    approved_status = models.BooleanField(null=True, blank=True)
    disapproved_status = models.BooleanField(null=True, blank=True)
    inactive_status = models.BooleanField(null=True, blank=True)
    UploadedBy = models.CharField(max_length=100, null=True, blank=True)
    UploadedDate = models.DateTimeField(null=True, blank=True)
    ChangedBy = models.CharField(max_length=100, null=True, blank=True)
    ChangedDate = models.DateTimeField(null=True, blank=True)
    dokumen_name = models.CharField(max_length=50, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    uuid_kapal = models.CharField(max_length=255, null=True, blank=True)
    badan_usaha = models.CharField(max_length=255, null=True, blank=True)
    nama_usaha = models.CharField(max_length=255, null=True, blank=True)
    jenis_bbm = models.IntegerField(null=True, blank=True)
    jenis_usaha = models.IntegerField(null=True, blank=True)
    kode_provinsi = models.CharField(max_length=50, null=True, blank=True)
    kode_kabkota = models.CharField(max_length=50, null=True, blank=True)
    kode_kecamatan = models.CharField(max_length=50, null=True, blank=True)
    kode_keldesa = models.CharField(max_length=50, null=True, blank=True)
    penerbit = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    url_file = models.CharField(max_length=100, null=True, blank=True)
    flag_status = models.IntegerField(null=True, blank=True)

    # Add fields for the descriptions from joined tables
    jenis_bbm_desc = models.CharField(max_length=50, null=True)
    sektor_konsumen_desc = models.CharField(max_length=255, null=True)
    jenis_usaha_desc = models.TextField(null=True)

    class Meta:
        db_table = 'View_NONVEHICLEMASTER'