from django.contrib import admin
from . import models


admin.site.register(models.Patient)
admin.site.register(models.PatientRecord)
admin.site.register(models.PatientSchedule)
admin.site.register(models.PatientExercises)
