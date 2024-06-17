from django.db import models

# Create your models here.

class Notifcation(models.Model):
    title = models.CharField(max_length=255)
    body = models.CharField(max_length=555)
    phone = models.CharField(max_length=55, null=True)
    type = models.CharField(max_length=255)
