from django.db import models

# Create your models here.
class Quota(models.Model):
    id = models.AutoField(primary_key=True)
    provinsi = models.CharField(max_length=100)
    site_registration = models.CharField(max_length=100)
    site_name = models.CharField(max_length=100)
    vehicletype_id = models.IntegerField()
    volume_quota = models.BigIntegerField()
    frequency_quota = models.IntegerField()
    id_product = models.IntegerField(null=True)
    deleted = models.BooleanField()

    class Meta:
        db_table = 'QUOTAMASTER'