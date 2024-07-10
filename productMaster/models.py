from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=256)
    price = models.IntegerField()
    idquota = models.IntegerField()
    datetimestart = models.DateTimeField()
    datetimeend = models.DateTimeField()
    deleted = models.BooleanField()

    class Meta:
        db_table = 'PRODUCT'