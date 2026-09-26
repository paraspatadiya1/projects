from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apiapp.models import Course, Studinfo


class StudentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.course = Course.objects.create(
            course_name="Test Python Mastery",
            course_fees=30000,
            course_duration="3 Months"
        )
        self.student = Studinfo.objects.create(
            full_name="John Doe",
            email="john.doe@test.com",
            phone="9876543210",
            age=22,
            gender="Male",
            city="New York",
            address="123 Test Street",
            course=self.course
        )

    def test_model_str_representations(self):
        self.assertEqual(str(self.course), "Test Python Mastery (3 Months)")
        self.assertEqual(str(self.student), "John Doe (john.doe@test.com)")

    def test_get_all_students(self):
        response = self.client.get('/getall/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Check nested course details in serialized output
        self.assertIn('course_details', response.data[0])
        self.assertEqual(response.data[0]['course_details']['course_name'], "Test Python Mastery")

    def test_search_students(self):
        response = self.client.get('/getall/?search=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_nomatch = self.client.get('/getall/?search=NonExistentPerson')
        self.assertEqual(response_nomatch.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_nomatch.data), 0)

    def test_filter_students_by_course(self):
        response = self.client.get(f'/getall/?course={self.course.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_student_by_id(self):
        response = self.client.get(f'/getid/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], "John Doe")

        # Test non-existent student
        response_404 = self.client.get('/getid/99999/')
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_student(self):
        payload = {
            "full_name": "Jane Smith",
            "email": "jane.smith@test.com",
            "phone": "9123456780",
            "age": 24,
            "gender": "Female",
            "city": "London",
            "address": "456 Oxford St",
            "course": self.course.id
        }
        response = self.client.post('/addstudent/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], "Jane Smith")
        self.assertEqual(response.data['course_details']['course_name'], "Test Python Mastery")

    def test_add_student_invalid_age(self):
        payload = {
            "full_name": "Invalid Age",
            "email": "invalid@test.com",
            "phone": "9123456780",
            "age": 150,  # Invalid
            "gender": "Male",
            "city": "London",
            "address": "456 Oxford St",
            "course": self.course.id
        }
        response = self.client.post('/addstudent/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data)

    def test_update_student(self):
        payload = {
            "full_name": "John Doe Updated",
            "email": "john.updated@test.com",
            "phone": "9876543210",
            "age": 23,
            "gender": "Male",
            "city": "San Francisco",
            "address": "123 New St",
            "course": self.course.id
        }
        response = self.client.put(f'/updateid/{self.student.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.full_name, "John Doe Updated")

    def test_delete_student(self):
        response = self.client.delete(f'/deleteid/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Studinfo.objects.filter(id=self.student.id).exists())

    def test_course_crud(self):
        # Create course
        create_res = self.client.post('/addcourse/', {
            "course_name": "DevOps Architect",
            "course_fees": 40000,
            "course_duration": "4 Months"
        }, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        new_course_id = create_res.data['id']

        # Get courses
        list_res = self.client.get('/getcourse/')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)

        # Update course
        update_res = self.client.put(f'/updatecourse/{new_course_id}/', {
            "course_name": "DevOps & Cloud Master",
            "course_fees": 42000,
            "course_duration": "5 Months"
        }, format='json')
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)

        # Delete course
        delete_res = self.client.delete(f'/deletecourse/{new_course_id}/')
        self.assertEqual(delete_res.status_code, status.HTTP_200_OK)
        self.assertFalse(Course.objects.filter(id=new_course_id).exists())

    def test_api_stats(self):
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_students', response.data)
        self.assertIn('total_courses', response.data)
        self.assertIn('avg_age', response.data)
        self.assertIn('total_revenue', response.data)
