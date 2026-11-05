from django.db import models


# Create your models here.
class patientsignup(models.Model):
    username = models.CharField(max_length=20)
    email = models.EmailField()
    mobile = models.BigIntegerField()
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

class Doctor(models.Model):

    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=150)
    experience = models.PositiveIntegerField()

    hospital = models.CharField(max_length=150)

    fee = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='doctors/',
        blank=True,
        null=True
    )

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)

    about = models.TextField()

    available_days = models.CharField(
        max_length=150,
        default='Monday - Saturday'
    )

    def __str__(self):
        return self.name