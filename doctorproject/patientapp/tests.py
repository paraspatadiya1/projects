from django.test import TestCase, Client
from patientapp.models import patientsignup, Doctor
from django.contrib.auth.hashers import check_password
from django.core.signing import TimestampSigner
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class MediCareFeatureTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.doctor = Doctor.objects.create(
            name="Dr. Aarav Mehta",
            specialization="Cardiology",
            qualification="MBBS, MD, DM",
            experience=14,
            hospital="Apollo Heart Institute",
            fee=1200.00,
            email="dr.aarav@apollo.com",
            phone="+91 98201 12345",
            about="Expert cardiologist with over 14 years clinical experience.",
            available_days="Monday - Friday"
        )
        self.patient = patientsignup.objects.create(
            username="test_patient",
            email="patient@medicare.com",
            mobile=9876543210,
            dob="1995-06-15",
            gender="Male",
            city="Mumbai",
            state="Maharashtra",
            password="pbkdf2_sha256$870000$dummy$hash"
        )

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Aarav Mehta")

    def test_doctor_detail_and_appointment(self):
        response = self.client.get(f'/doctor/{self.doctor.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.doctor.name)

        post_res = self.client.post(f'/doctor/{self.doctor.id}/', {
            'patient_name': 'Test Patient',
            'phone': '9876543210',
            'appointment_date': '2026-11-15',
            'time_slot': '10:00 AM'
        }, follow=True)
        self.assertEqual(post_res.status_code, 200)
        self.assertContains(post_res, "Appointment booked successfully")

    def test_signup_validation_and_success(self):
        # Invalid signup
        res_fail = self.client.post('/signup/', {
            'username': 'ab',
            'email': 'bad_email',
            'mobile': '123',
            'dob': '2000-01-01',
            'gender': 'Male',
            'city': 'Mumbai',
            'state': 'MH',
            'password': '12'
        })
        self.assertEqual(res_fail.status_code, 200)
        self.assertContains(res_fail, "Please correct the following")

        # Valid signup
        res_ok = self.client.post('/signup/', {
            'username': 'new_patient_user',
            'email': 'newpatient@medicare.com',
            'mobile': '9898989898',
            'dob': '1998-04-10',
            'gender': 'Female',
            'city': 'Delhi',
            'state': 'Delhi',
            'password': 'StrongPassword123'
        }, follow=True)
        self.assertEqual(res_ok.status_code, 200)
        new_user = patientsignup.objects.filter(email='newpatient@medicare.com').first()
        self.assertIsNotNone(new_user)
        self.assertTrue(check_password('StrongPassword123', new_user.password))

    def test_login_logout_flow(self):
        # Register a user
        self.client.post('/signup/', {
            'username': 'login_tester',
            'email': 'logintester@medicare.com',
            'mobile': '9123456789',
            'dob': '1992-01-01',
            'gender': 'Male',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'password': 'MyPassword123'
        })

        # Correct login
        res_login = self.client.post('/login/', {
            'email': 'logintester@medicare.com',
            'password': 'MyPassword123'
        }, follow=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertEqual(self.client.session.get('user'), 'logintester@medicare.com')

        # Access profile while logged in
        res_profile = self.client.get('/profile/')
        self.assertEqual(res_profile.status_code, 200)
        self.assertContains(res_profile, "login_tester")

        # Logout
        res_logout = self.client.get('/logout/', follow=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertNotIn('userid', self.client.session)

    def test_profile_update(self):
        # Login
        session = self.client.session
        session['userid'] = self.patient.id
        session['username'] = self.patient.username
        session['user'] = self.patient.email
        session.save()

        res = self.client.post('/edit-profile/', {
            'username': 'updated_username',
            'email': self.patient.email,
            'mobile': '9876543210',
            'dob': '1995-06-15',
            'gender': 'Male',
            'city': 'Hyderabad',
            'state': 'Telangana'
        }, follow=True)
        self.assertEqual(res.status_code, 200)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.username, 'updated_username')
        self.assertEqual(self.patient.city, 'Hyderabad')
