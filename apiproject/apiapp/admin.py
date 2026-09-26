from django.contrib import admin
from .models import *

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name', 'course_fees', 'course_duration', 'student_count')
    search_fields = ('course_name', 'course_duration')
    ordering = ('id',)

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Enrolled Students'


@admin.register(Studinfo)
class StudinfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'age', 'gender', 'city', 'course')
    list_filter = ('gender', 'course', 'city')
    search_fields = ('full_name', 'email', 'phone', 'city')
    ordering = ('-id',)
