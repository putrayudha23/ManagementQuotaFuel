from django.db import models

# Create your models here.
class UserSiteMapping(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    site_registration = models.CharField(max_length=255)

    class Meta:
        db_table = 'USERSITEMAPPING'