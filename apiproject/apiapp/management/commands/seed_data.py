from django.core.management.base import BaseCommand
from apiapp.models import Course, Studinfo


class Command(BaseCommand):
    help = 'Seeds realistic sample courses and students for portfolio showcase.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing records before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing students and courses...'))
            Studinfo.objects.all().delete()
            Course.objects.all().delete()

        courses_data = [
            {'course_name': 'Full Stack Python & Django', 'course_fees': 45000, 'course_duration': '6 Months'},
            {'course_name': 'Cloud Computing & DevOps', 'course_fees': 55000, 'course_duration': '4 Months'},
            {'course_name': 'Data Science & Machine Learning', 'course_fees': 60000, 'course_duration': '6 Months'},
            {'course_name': 'React & Frontend Architecture', 'course_fees': 38000, 'course_duration': '3 Months'},
            {'course_name': 'Cyber Security & Ethical Hacking', 'course_fees': 50000, 'course_duration': '5 Months'},
        ]

        course_map = {}
        for c in courses_data:
            course, created = Course.objects.get_or_create(
                course_name=c['course_name'],
                defaults={
                    'course_fees': c['course_fees'],
                    'course_duration': c['course_duration'],
                }
            )
            course_map[c['course_name']] = course
            status = 'Created' if created else 'Existing'
            self.stdout.write(f"  [{status}] Course: {course.course_name}")

        students_data = [
            {
                'full_name': 'Aarav Sharma',
                'email': 'aarav.sharma@example.com',
                'phone': '+91 98234 11223',
                'age': 22,
                'gender': 'Male',
                'city': 'Mumbai',
                'address': '402, High Street, Bandra West',
                'course': course_map['Full Stack Python & Django']
            },
            {
                'full_name': 'Priya Patel',
                'email': 'priya.patel@example.com',
                'phone': '+91 97123 45678',
                'age': 24,
                'gender': 'Female',
                'city': 'Ahmedabad',
                'address': '12, Shivalik Avenue, SG Highway',
                'course': course_map['Data Science & Machine Learning']
            },
            {
                'full_name': 'Rohan Mehta',
                'email': 'rohan.mehta@example.com',
                'phone': '+91 98980 12345',
                'age': 23,
                'gender': 'Male',
                'city': 'Pune',
                'address': '78, Tech Park Road, Hinjewadi',
                'course': course_map['Cloud Computing & DevOps']
            },
            {
                'full_name': 'Sneha Reddy',
                'email': 'sneha.reddy@example.com',
                'phone': '+91 99887 66554',
                'age': 21,
                'gender': 'Female',
                'city': 'Hyderabad',
                'address': 'Plot 15, Madhapur Cyber Towers',
                'course': course_map['React & Frontend Architecture']
            },
            {
                'full_name': 'Vikram Malhotra',
                'email': 'vikram.m@example.com',
                'phone': '+91 91234 56789',
                'age': 25,
                'gender': 'Male',
                'city': 'Bengaluru',
                'address': 'Suite 3B, Indiranagar 100ft Rd',
                'course': course_map['Cyber Security & Ethical Hacking']
            },
            {
                'full_name': 'Ananya Joshi',
                'email': 'ananya.j@example.com',
                'phone': '+91 98450 78901',
                'age': 23,
                'gender': 'Female',
                'city': 'Delhi',
                'address': '88, Connaught Place Outer Circle',
                'course': course_map['Data Science & Machine Learning']
            },
            {
                'full_name': 'Kabir Singh',
                'email': 'kabir.singh@example.com',
                'phone': '+91 97654 32109',
                'age': 26,
                'gender': 'Male',
                'city': 'Chandigarh',
                'address': 'Sector 17 Market Complex',
                'course': course_map['Full Stack Python & Django']
            },
            {
                'full_name': 'Isha Nair',
                'email': 'isha.nair@example.com',
                'phone': '+91 98112 33445',
                'age': 22,
                'gender': 'Female',
                'city': 'Kochi',
                'address': 'Marine Drive Tower B',
                'course': course_map['React & Frontend Architecture']
            },
            {
                'full_name': 'Aditya Verma',
                'email': 'aditya.v@example.com',
                'phone': '+91 98223 44556',
                'age': 24,
                'gender': 'Male',
                'city': 'Jaipur',
                'address': 'Civil Lines, Raj Bhavan Road',
                'course': course_map['Cloud Computing & DevOps']
            },
            {
                'full_name': 'Divya Sundaram',
                'email': 'divya.s@example.com',
                'phone': '+91 98334 55667',
                'age': 25,
                'gender': 'Female',
                'city': 'Chennai',
                'address': 'OMR IT Expressway Phase 2',
                'course': course_map['Data Science & Machine Learning']
            }
        ]

        added = 0
        for s in students_data:
            course = s.pop('course')
            obj, created = Studinfo.objects.get_or_create(
                email=s['email'],
                defaults={'course': course, **s}
            )
            if created:
                added += 1
                self.stdout.write(f"  [Created] Student: {obj.full_name} -> {course.course_name}")
            else:
                self.stdout.write(f"  [Existing] Student: {obj.full_name}")

        self.stdout.write(self.style.SUCCESS(
            f"\nSuccess! Total Courses: {Course.objects.count()} | Total Students: {Studinfo.objects.count()} ({added} new students added)."
        ))

