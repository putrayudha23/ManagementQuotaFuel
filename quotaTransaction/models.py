from django.db import models

class QuotaTransaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    number_plat = models.CharField(max_length=50)
    vehicletype_id = models.IntegerField()
    volume_quotaallocated = models.BigIntegerField()
    volume_quotaavailable = models.BigIntegerField()
    price = models.IntegerField()
    frequency_quota = models.IntegerField()
    site_registration = models.CharField(max_length=50, null=True)
    trn_id = models.IntegerField(null=True)
    trnrec = models.BooleanField(null=True)
    quota_time = models.DateTimeField()
    transaction_time = models.DateTimeField(null=True)
    volume_quotaallocated_before = models.BigIntegerField(null=True)
    volume_quotaavailable_before = models.BigIntegerField(null=True)
    site_registration_before = models.CharField(max_length=50, null=True)
    
    class Meta:
        db_table = 'QUOTATRANSACTION'

class LogQuotaTransaction(models.Model):
    number_plat = models.CharField(max_length=50)
    volume_quotaavailable_before = models.BigIntegerField()
    volume_quotaavailable_new = models.BigIntegerField()
    frequency_quota_before = models.IntegerField()
    frequency_quota_new = models.IntegerField()
    trnrec_before = models.BooleanField()
    trnrec_new = models.BooleanField()
    ChangedBy = models.CharField(max_length=100)
    ChangedDate = models.DateTimeField()

    class Meta:
        db_table = 'LOGQUOTATRANSACTION'
