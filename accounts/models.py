from django.db import models
from QuiverDatabase.settings import MAX_USERNAME_LENGTH, MAX_PASSWORD_LENGTH

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, blank=False)
    email = models.EmailField(blank=False)
    password = models.CharField(max_length=MAX_PASSWORD_LENGTH, blank=False)
    password_confirm = models.CharField(max_length=MAX_PASSWORD_LENGTH, blank=False)  # Confirmation password
    
    
    