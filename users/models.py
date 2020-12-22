from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    country = models.CharField(verbose_name='country', max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email
