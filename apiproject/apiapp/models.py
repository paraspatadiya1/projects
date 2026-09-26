from django.db import models

# Create your models here.



class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_fees = models.IntegerField()
    course_duration = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f"{self.course_name} ({self.course_duration})"


class Studinfo(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    address = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='students')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Student Information'
        verbose_name_plural = 'Student Information'

    def __str__(self):
        return f"{self.full_name} ({self.email})"





    