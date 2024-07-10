from django.db import models

# Create your models here.
class VehicleType(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=256)
    SettingSystem = models.IntegerField(null=True)
    deleted = models.BooleanField()

    class Meta:
        db_table = 'VEHICLETYPE'