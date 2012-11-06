from django.contrib import admin
from pyavatax import models


class AvaTaxRecordAdmin(admin.ModelAdmin):
    list_display = ['doc_code', 'logged_on', 'success_on']
    ordering = ['logged_on']
    search_fields = ['doc_code']

admin.site.register(models.AvaTaxRecord, AvaTaxRecordAdmin)
