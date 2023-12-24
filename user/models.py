from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    last_request_time = models.DateTimeField(null=True, blank=True)
