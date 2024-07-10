from django.db import models

# Create your models here.
class NonTransportasiBPHMigas(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=255)
    uuid_kapal = models.CharField(max_length=255)
    badan_usaha = models.CharField(max_length=255)
    no_surat_rekomendasi = models.CharField(max_length=255)
    nik = models.CharField(max_length=255)
    nama = models.CharField(max_length=255)
    nama_usaha = models.CharField(max_length=255)
    jenis_bbm = models.IntegerField()
    sektor_konsumen = models.IntegerField()
    jenis_usaha = models.IntegerField()
    nama_kapal = models.CharField(max_length=255)
    alokasi_volume = models.FloatField()
    no_penyalur = models.CharField(max_length=10)
    tanggal_terbit = models.DateField()
    tanggal_berakhir = models.DateField()
    kode_provinsi = models.CharField(max_length=50)
    kode_kabkota = models.CharField(max_length=50)
    kode_kecamatan = models.CharField(max_length=50)
    kode_keldesa = models.CharField(max_length=50)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    status = models.IntegerField()
    penerbit = models.CharField(max_length=255)
    url_file = models.CharField(max_length=500)
    data_release = models.BooleanField(null=True)
    arrived_date = models.DateTimeField()
    site_registration = models.CharField(max_length=255)
    email_release = models.BooleanField(null=True)

    class Meta:
        db_table = 'NONTRANSPORTASIBPHMIGAS'

class ViewNonTransportasi(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=255)
    uuid_kapal = models.CharField(max_length=255)
    badan_usaha = models.CharField(max_length=255)
    no_surat_rekomendasi = models.CharField(max_length=255)
    nik = models.CharField(max_length=255)
    nama = models.CharField(max_length=255)
    nama_usaha = models.CharField(max_length=255)
    jenis_bbm = models.IntegerField()
    sektor_konsumen = models.IntegerField()
    jenis_usaha = models.IntegerField()
    nama_kapal = models.CharField(max_length=255)
    alokasi_volume = models.FloatField()
    no_penyalur = models.CharField(max_length=10)
    tanggal_terbit = models.DateField()
    tanggal_berakhir = models.DateField()
    kode_provinsi = models.CharField(max_length=50)
    kode_kabkota = models.CharField(max_length=50)
    kode_kecamatan = models.CharField(max_length=50)
    kode_keldesa = models.CharField(max_length=50)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    status = models.IntegerField()
    penerbit = models.CharField(max_length=255)
    url_file = models.CharField(max_length=500)
    data_release = models.BooleanField(null=True)
    site_registration = models.CharField(max_length=255)

    # Add fields for the descriptions from joined tables
    jenis_bbm_desc = models.CharField(max_length=50, null=True)
    sektor_konsumen_desc = models.CharField(max_length=255, null=True)
    jenis_usaha_desc = models.TextField(null=True)  # Assuming jenis_usaha is of type nvarchar(MAX)

    class Meta:
        db_table = 'View_NONTRANSPORTASIBPHMIGAS'


# CREATE VIEW View_NONTRANSPORTASIBPHMIGAS AS
# SELECT
#     NT.*,
#     JB.jenis_bbm AS jenis_bbm_desc,
#     SK.sektor_konsumen AS sektor_konsumen_desc,
#     JU.jenis_usaha AS jenis_usaha_desc
# FROM
#     NONTRANSPORTASIBPHMIGAS NT
# LEFT JOIN
#     JENISBBMMASTER JB ON NT.jenis_bbm = JB.id
# LEFT JOIN
#     SEKTORKONSUMENMASTER SK ON NT.sektor_konsumen = SK.id
# LEFT JOIN
#     JENISUSAHAMASTER JU ON NT.jenis_usaha = JU.id;

class JenisBbmMaster(models.Model):
    id = models.IntegerField(primary_key=True)
    jenis_bbm = models.CharField(max_length=50)

    class Meta:
        db_table = 'JENISBBMMASTER'

class JenisUsahaMaster(models.Model):
    id = models.IntegerField(primary_key=True)
    jenis_usaha = models.CharField(max_length=500)

    class Meta:
        db_table = 'JENISUSAHAMASTER'

class SektorKonsumenMaster(models.Model):
    id = models.IntegerField(primary_key=True)
    sektor_konsumen = models.CharField(max_length=500)

    class Meta:
        db_table = 'SEKTORKONSUMENMASTER'