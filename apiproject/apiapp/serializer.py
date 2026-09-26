from rest_framework import serializers
from .models import Course, Studinfo


class CourseSerial(serializers.ModelSerializer):
    student_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_fees', 'course_duration', 'student_count']

    def validate_course_fees(self, value):
        if value < 0:
            raise serializers.ValidationError("Course fees cannot be negative.")
        return value


class StudSerial(serializers.ModelSerializer):
    course_details = CourseSerial(source='course', read_only=True)

    class Meta:
        model = Studinfo
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'age',
            'gender',
            'city',
            'address',
            'course',
            'course_details'
        ]

    def validate_age(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError("Age must be between 1 and 120.")
        return value
