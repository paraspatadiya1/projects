from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, Q
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

from .models import Course, Studinfo
from .serializer import CourseSerial, StudSerial


def wants_json(request):
    """
    Determine whether the incoming request is expecting a JSON API response
    versus an HTML webpage.
    Web browsers always include 'text/html' in their Accept header.
    API clients, test runners, and curl send 'application/json' or '*/*'.
    """
    if request.GET.get('format') == 'json':
        return True
    accept = request.headers.get('Accept', '')
    if 'text/html' in accept:
        return False
    return True



def get_dashboard_metrics():
    students = Studinfo.objects.select_related('course').all()
    courses = Course.objects.annotate(enrolled_count=Count('students')).all()

    total_students = students.count()
    total_courses = courses.count()

    avg_age_val = students.aggregate(avg=Avg('age'))['avg']
    avg_age = round(avg_age_val, 1) if avg_age_val is not None else 0

    total_revenue = sum(c.course_fees * c.enrolled_count for c in courses)

    # Chart data: enrollment per course
    course_labels = [c.course_name for c in courses]
    course_counts = [c.enrolled_count for c in courses]

    # Chart data: gender distribution
    gender_map = {'Male': 0, 'Female': 0, 'Other': 0}
    for s in students:
        g = (s.gender or '').strip().capitalize()
        if g in gender_map:
            gender_map[g] += 1
        elif g:
            gender_map['Other'] += 1

    return {
        'total_students': total_students,
        'total_courses': total_courses,
        'avg_age': avg_age,
        'total_revenue': total_revenue,
        'course_labels_json': json.dumps(course_labels),
        'course_counts_json': json.dumps(course_counts),
        'gender_labels_json': json.dumps(list(gender_map.keys())),
        'gender_counts_json': json.dumps(list(gender_map.values())),
        'recent_students': students.order_by('-id')[:6],
    }


def index(request):
    """
    Main Executive Dashboard Web Page.
    """
    students = Studinfo.objects.select_related('course').all()
    courses = Course.objects.annotate(enrolled_count=Count('students')).all()
    metrics = get_dashboard_metrics()

    context = {
        'data': students,
        'cdata': courses,
        'active_page': 'dashboard',
        **metrics,
    }
    return render(request, 'index.html', context)


# ==========================================
# Student Views & REST Endpoints
# ==========================================

@api_view(['GET'])
def getall(request):
    """
    Web Page & REST API: List all students with search & course filtering.
    """
    queryset = Studinfo.objects.select_related('course').all()

    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    course_filter = request.GET.get('course', '').strip()
    if course_filter:
        queryset = queryset.filter(course_id=course_filter)

    if wants_json(request):
        serial = StudSerial(queryset, many=True)
        return Response(serial.data)

    courses = Course.objects.all()
    context = {
        'data': queryset,
        'courses': courses,
        'search_query': search_query,
        'selected_course': course_filter,
        'active_page': 'students',
    }
    return render(request, 'students_list.html', context)


@api_view(['GET'])
def getid(request, id):
    """
    Web Page & REST API: View individual student details dossier.
    """
    try:
        student = Studinfo.objects.select_related('course').get(id=id)
    except Studinfo.DoesNotExist:
        if wants_json(request):
            return Response({'error': f'Student with id {id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages.error(request, f'Student #{id} not found.')
        return redirect('/getall/')

    if wants_json(request):
        serial = StudSerial(student)
        return Response(serial.data)

    context = {
        'student': student,
        'active_page': 'students',
    }
    return render(request, 'student_detail.html', context)


@api_view(['GET', 'POST'])
def addstudent(request):
    """
    Web Page & REST API: Enroll new student.
    GET: renders enrollment form.
    POST: creates student and redirects to /getall/ (or returns JSON).
    """
    if request.method == 'POST':
        if wants_json(request) or request.content_type == 'application/json':
            serial = StudSerial(data=request.data)
            if serial.is_valid():
                student = serial.save()
                return Response(StudSerial(student).data, status=status.HTTP_201_CREATED)
            return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

        # Standard HTML Form Submission
        course_id = request.POST.get('course')
        course = Course.objects.filter(id=course_id).first() if course_id else None
        try:
            student = Studinfo.objects.create(
                full_name=request.POST.get('full_name', '').strip(),
                email=request.POST.get('email', '').strip(),
                phone=request.POST.get('phone', '').strip(),
                age=int(request.POST.get('age', 21)),
                gender=request.POST.get('gender', 'Male'),
                city=request.POST.get('city', '').strip(),
                address=request.POST.get('address', '').strip(),
                course=course,
            )
            messages.success(request, f'Student "{student.full_name}" enrolled successfully!')
            return redirect('/getall/')
        except Exception as e:
            messages.error(request, f'Failed to enroll student: {str(e)}')

    courses = Course.objects.all()
    context = {
        'courses': courses,
        'active_page': 'addstudent',
    }
    return render(request, 'student_form.html', context)


@api_view(['GET', 'POST', 'PUT', 'PATCH'])
def updateid(request, id):
    """
    Web Page & REST API: Update existing student.
    GET: renders pre-populated form.
    POST: updates student and redirects to /getall/.
    PUT/PATCH: updates student and returns JSON.
    """
    try:
        student = Studinfo.objects.get(id=id)
    except Studinfo.DoesNotExist:
        if wants_json(request):
            return Response({'error': f'Student with id {id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages.error(request, f'Student #{id} not found.')
        return redirect('/getall/')

    if request.method in ['PUT', 'PATCH'] or (request.method == 'POST' and (wants_json(request) or request.content_type == 'application/json')):
        partial = request.method == 'PATCH' or request.data.get('_partial', False)
        serial = StudSerial(student, data=request.data, partial=partial)
        if serial.is_valid():
            updated = serial.save()
            return Response(StudSerial(updated).data, status=status.HTTP_200_OK)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        course_id = request.POST.get('course')
        course = Course.objects.filter(id=course_id).first() if course_id else None
        try:
            student.full_name = request.POST.get('full_name', student.full_name).strip()
            student.email = request.POST.get('email', student.email).strip()
            student.phone = request.POST.get('phone', student.phone).strip()
            student.age = int(request.POST.get('age', student.age))
            student.gender = request.POST.get('gender', student.gender)
            student.city = request.POST.get('city', student.city).strip()
            student.address = request.POST.get('address', student.address).strip()
            student.course = course
            student.save()
            messages.success(request, f'Student "{student.full_name}" updated successfully!')
            return redirect('/getall/')
        except Exception as e:
            messages.error(request, f'Failed to update student: {str(e)}')

    if wants_json(request):
        return Response(StudSerial(student).data)

    courses = Course.objects.all()
    context = {
        'student': student,
        'courses': courses,
        'active_page': 'students',
    }
    return render(request, 'student_form.html', context)


@api_view(['GET', 'POST', 'DELETE'])
def deleteid(request, id):
    """
    Web Page & REST API: Delete student.
    GET: renders confirmation page.
    POST: deletes student and redirects to /getall/.
    DELETE: deletes student and returns JSON.
    """
    try:
        student = Studinfo.objects.get(id=id)
    except Studinfo.DoesNotExist:
        if wants_json(request):
            return Response({'error': f'Student with id {id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages.error(request, f'Student #{id} not found.')
        return redirect('/getall/')

    if request.method == 'DELETE' or (request.method == 'POST' and (wants_json(request) or request.content_type == 'application/json')):
        student.delete()
        return Response(
            {'success': True, 'message': f'Student with ID {id} was deleted successfully.'},
            status=status.HTTP_200_OK
        )

    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.success(request, f'Student "{name}" was removed successfully.')
        return redirect('/getall/')

    if wants_json(request):
        return Response(StudSerial(student).data)

    context = {
        'student': student,
        'active_page': 'students',
    }
    return render(request, 'student_confirm_delete.html', context)


# ==========================================
# Course Views & REST Endpoints
# ==========================================

@api_view(['GET'])
def getcourse(request):
    """
    Web Page & REST API: List all courses with enrollment counts.
    """
    courses = Course.objects.annotate(enrolled_count=Count('students')).all()

    if wants_json(request):
        serial = CourseSerial(courses, many=True)
        return Response(serial.data)

    context = {
        'courses': courses,
        'active_page': 'courses',
    }
    return render(request, 'courses_list.html', context)


@api_view(['GET'])
def getcourseid(request, id):
    """
    Web Page & REST API: View individual course and enrolled students.
    """
    try:
        course = Course.objects.get(id=id)
    except Course.DoesNotExist:
        if wants_json(request):
            return Response({'error': f'Course with id {id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages.error(request, f'Course #{id} not found.')
        return redirect('/getcourse/')

    if wants_json(request):
        serial = CourseSerial(course)
        return Response(serial.data)

    enrolled_students = course.students.all()
    context = {
        'course': course,
        'enrolled_students': enrolled_students,
        'active_page': 'courses',
    }
    return render(request, 'course_detail.html', context)


@api_view(['GET', 'POST'])
def addcourse(request):
    """
    Web Page & REST API: Add new course curriculum track.
    GET: renders course form.
    POST: creates course and redirects to /getcourse/ (or returns JSON).
    """
    if request.method == 'POST':
        if wants_json(request) or request.content_type == 'application/json':
            serial = CourseSerial(data=request.data)
            if serial.is_valid():
                course = serial.save()
                return Response(CourseSerial(course).data, status=status.HTTP_201_CREATED)
            return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.create(
                course_name=request.POST.get('course_name', '').strip(),
                course_fees=int(request.POST.get('course_fees', 0)),
                course_duration=request.POST.get('course_duration', '').strip(),
            )
            messages.success(request, f'Course Track "{course.course_name}" created successfully!')
            return redirect('/getcourse/')
        except Exception as e:
            messages.error(request, f'Failed to create course track: {str(e)}')

    context = {
        'active_page': 'addcourse',
    }
    return render(request, 'course_form.html', context)


@api_view(['GET', 'POST', 'PUT', 'PATCH'])
def updatecourse(request, id):
    """
    Web Page & REST API: Update course details.
    GET: renders pre-populated form.
    POST: updates course and redirects to /getcourse/.
    PUT/PATCH: updates course and returns JSON.
    """
    try:
        course = Course.objects.get(id=id)
    except Course.DoesNotExist:
        if wants_json(request):
            return Response({'error': f'Course with id {id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages.error(request, f'Course #{id} not found.')
        return redirect('/getcourse/')

    if request.method in ['PUT', 'PATCH'] or (request.method == 'POST' and (wants_json(request) or request.content_type == 'application/json')):
        partial = request.method == 'PATCH'
        serial = CourseSerial(course, data=request.data, partial=partial)
        if serial.is_valid():
            course = serial.save()
            return Response(CourseSerial(course).data, status=status.HTTP_200_OK)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        try:
            course.course_name = request.POST.get('course_name', course.course_name).strip()
            course.course_fees = int(request.POST.get('course_fees', course.course_fees))
            course.course_duration = request.POST.get('course_duration', course.course_duration).strip()
            course.save()
            messages.success(request, f'Course Track "{course.course_name}" updated successfully!')
            return redirect('/getcourse/')
        except Exception as e:
            messages.error(request, f'Failed to update course track: {str(e)}')

    if wants_json(request):
        return Response(CourseSerial(course).data)

    context = {
        'course': course,
        'active_page': 'courses',
    }
    return render(request, 'course_form.html', context)


@api_view(['GET', 'POST', 'DELETE'])
def deletecourse(request, id):
    """
    Web Page & REST API: Delete course track.
    GET: renders confirmation page.
    POST: deletes course and redirects to /getcourse/.
    DELETE: deletes course and returns JSON.
    """
    try:
        course = Course.objects.get(id=id)
    except Course.DoesNotExist:
        if wants_json(request):
            return Response({'error': f'Course with id {id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages.error(request, f'Course #{id} not found.')
        return redirect('/getcourse/')

    if request.method == 'DELETE' or (request.method == 'POST' and (wants_json(request) or request.content_type == 'application/json')):
        course.delete()
        return Response(
            {'success': True, 'message': f'Course with ID {id} was deleted successfully.'},
            status=status.HTTP_200_OK
        )

    if request.method == 'POST':
        name = course.course_name
        course.delete()
        messages.success(request, f'Course Track "{name}" was deleted successfully.')
        return redirect('/getcourse/')

    if wants_json(request):
        return Response(CourseSerial(course).data)

    context = {
        'course': course,
        'active_page': 'courses',
    }
    return render(request, 'course_confirm_delete.html', context)


# ==========================================
# Realtime Analytics & Developer Documentation
# ==========================================

@api_view(['GET'])
def api_stats(request):
    """
    Live dashboard metrics endpoint.
    """
    metrics = get_dashboard_metrics()
    return Response({
        'total_students': metrics['total_students'],
        'total_courses': metrics['total_courses'],
        'avg_age': metrics['avg_age'],
        'total_revenue': metrics['total_revenue'],
        'course_labels': json.loads(metrics['course_labels_json']),
        'course_counts': json.loads(metrics['course_counts_json']),
        'gender_labels': json.loads(metrics['gender_labels_json']),
        'gender_counts': json.loads(metrics['gender_counts_json']),
    })


def api_docs_view(request):
    """
    Dedicated REST Gateway & SDK Generator Web Page.
    """
    return render(request, 'api_docs.html', {'active_page': 'api_docs'})
