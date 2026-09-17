from django.db import models

# Create your models here.
class patientsignup(models.Model):
    username=models.CharField(max_length=20)
    email=models.EmailField()
    mobile=models.BigIntegerField()
    dob=models.DateField()
    gender=models.CharField(max_length=10)
    city=models.CharField(max_length=20)
    state=models.CharField(max_length=20)
    password=models.CharField(max_length=15)


