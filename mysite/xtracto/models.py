from django.db import models

# Create your models here.
class Users(models.Model):
	email = models.EmailField()
	password =	models.CharField(max_length=100)