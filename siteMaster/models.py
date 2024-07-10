from django.db import models

# Create your models here.
class SiteMaster(models.Model):
    id = models.AutoField(primary_key=True)
    provinsi = models.CharField(max_length=100)
    site_registration = models.CharField(max_length=100)
    site_name = models.CharField(max_length=100)
    typeSpb = models.CharField(max_length=50)
    deleted = models.BooleanField()

    class Meta:
        db_table = 'SITEMASTER'