from django.db import models

# Create your models here.
class Registered(models.Model):
    email = models.EmailField()
    password =	models.CharField(max_length=100)
    # def __str__(self):
    #     return self.headline