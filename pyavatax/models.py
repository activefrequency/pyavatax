from django.db import models


class SuccessRecordManager(models.Manager):

    def get_query_set(self):
        return super(SuccessRecordManager, self).get_query_set().filter(success_on__isnull=False)


class FailedRecordManager(models.Manager):

    def get_query_set(self):
        return super(FailedRecordManager, self).get_query_set().filter(success_on__isnull=True)
    

class AvaTaxRecord(models.Model):
    doc_code = models.CharField(max_length=255)
    failure_details = models.TextField()
    logged_on = models.DateTimeField(auto_now_add=True)
    success_on = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()
    successes = SuccessRecordManager()
    failures = FailedRecordManager()
