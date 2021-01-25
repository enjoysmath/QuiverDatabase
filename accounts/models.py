from django.db import models
from QuiverDatabase.settings import MAX_USERNAME_LENGTH, MAX_PASSWORD_LENGTH

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=MAX_USERNAME_LENGTH)
    email = models.EmailField() #blank=True)
    password = models.CharField(max_length=MAX_PASSWORD_LENGTH)
    password_confirm = models.CharField(max_length=MAX_PASSWORD_LENGTH)
    