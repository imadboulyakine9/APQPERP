from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    departement = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    notification_email = models.BooleanField(default=True)

# Create your models here.
