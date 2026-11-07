from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect, get_object_or_404
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib import messages
from patientapp.forms import SignupForm, ProfileForm
from .models import patientsignup, Doctor


def home(request):
    user = None
    if 'userid' in request.session:
        user = patientsignup.objects.filter(
            id=request.session['userid']
        ).first()

    search_query = request.GET.get('q', '').strip()
    specialization = request.GET.get('specialization', '').strip()

    doctors = Doctor.objects.all().order_by('name')

    if search_query:
        doctors = doctors.filter(
            name__icontains=search_query
        ) | doctors.filter(
            specialization__icontains=search_query
        ) | doctors.filter(
            hospital__icontains=search_query
        )

    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    # Get distinct specializations for quick filters
    all_specializations = [
        "Cardiology", "Neurology", "Orthopedics", "Dermatology",
        "Pediatrics", "Dentistry", "Ophthalmology", "General Medicine"
    ]

    return render(request, 'home.html', {
        'user': user,
        'doctors': doctors,
        'specializations': all_specializations,
        'current_search': search_query,
        'current_specialization': specialization,
    })


def doctor_detail(request, id):
    doctor = get_object_or_404(Doctor, id=id)

    user = None
    if 'userid' in request.session:
        user = patientsignup.objects.filter(
            id=request.session['userid']
        ).first()

    # Appointment booking action
    booking_success = None
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip() or (user.username if user else 'Patient')
        appointment_date = request.POST.get('appointment_date', '')
        time_slot = request.POST.get('time_slot', '10:00 AM')
        contact_phone = request.POST.get('phone', '') or (str(user.mobile) if user else '')
        notes = request.POST.get('notes', '')

        booking_success = {
            'doctor_name': doctor.name,
            'hospital': doctor.hospital,
            'fee': doctor.fee,
            'date': appointment_date,
            'time': time_slot,
            'patient_name': patient_name,
            'phone': contact_phone
        }
        messages.success(request, f"Appointment booked successfully with Dr. {doctor.name} for {appointment_date} at {time_slot}!")

    return render(request, 'doctor_detail.html', {
        'doctor': doctor,
        'user': user,
        'booking_success': booking_success
    })


def signup(request):
    if 'userid' in request.session:
        return redirect('profile')

    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome {user.username}! Your account has been registered successfully. Please sign in.")
            return redirect('login')
        else:
            return render(request, 'signup.html', {
                'form': form,
                'errors': form.errors
            })

    form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login(request):
    if 'userid' in request.session:
        return redirect('profile')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            return render(request, 'login.html', {
                'error': 'Please enter both your email address and password.',
                'email': email
            })

        user = patientsignup.objects.filter(email__iexact=email).first()

        if user and check_password(password, user.password):
            request.session['user'] = user.email
            request.session['userid'] = user.id
            request.session['username'] = user.username
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid email address or password. Please verify and try again.',
                'email': email
            })

    return render(request, 'login.html')


def logout(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


def profile(request):
    if 'userid' not in request.session:
        messages.info(request, "Please log in to access your profile.")
        return redirect('login')

    user = patientsignup.objects.filter(id=request.session['userid']).first()
    if not user:
        request.session.flush()
        messages.error(request, "Your session has expired. Please log in again.")
        return redirect('login')

    return render(request, 'profile.html', {'user': user})


def edit_profile(request):
    if 'userid' not in request.session:
        messages.info(request, "Please log in to edit your profile.")
        return redirect('login')

    user = patientsignup.objects.filter(id=request.session['userid']).first()
    if not user:
        request.session.flush()
        return redirect('login')

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=user
        )
        if form.is_valid():
            form.save()
            request.session['username'] = user.username
            request.session['user'] = user.email
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please review the errors highlighted below.")
    else:
        form = ProfileForm(instance=user)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': user
    })


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            return render(request, 'forgot_password.html', {
                'error': 'Please enter your registered email address.'
            })

        user = patientsignup.objects.filter(email__iexact=email).first()

        if not user:
            return render(request, 'forgot_password.html', {
                'error': 'No account was found with this email. Please check the spelling or sign up.'
            })

        signer = TimestampSigner(salt='patient-password-reset')
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = signer.sign(str(user.id))

        reset_link = request.build_absolute_uri(
            f'/reset-password/{uid}/{token}/'
        )

        subject = 'MediCare - Password Reset Request'
        message = f"""Hello {user.username},

You requested to reset your password on the MediCare Portal.

Click the secure link below to set a new password:
{reset_link}

This link is valid for 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
MediCare Medical Team
"""

        email_sent = False
        try:
            send_mail(
                subject,
                message,
                None,
                [user.email],
                fail_silently=False
            )
            email_sent = True
        except Exception as e:
            print(f"Password reset mail attempt notice: {e}")
            email_sent = False

        if email_sent:
            return render(request, 'forgot_password.html', {
                'success': 'A password reset link has been sent to your registered email address.'
            })
        else:
            # Resilient fallback so users can always test and reset even without live SMTP
            return render(request, 'forgot_password.html', {
                'success': 'Password reset link generated! In this environment, you can use the direct link below:',
                'direct_reset_link': reset_link
            })

    return render(request, 'forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = patientsignup.objects.get(id=uid)
        signer = TimestampSigner(salt='patient-password-reset')
        signed_user_id = signer.unsign(token, max_age=3600)

        if str(user.id) != str(signed_user_id):
            raise BadSignature

    except (
        TypeError,
        ValueError,
        OverflowError,
        patientsignup.DoesNotExist,
        BadSignature,
        SignatureExpired
    ):
        return render(request, 'reset_password.html', {
            'error': 'This password reset link is invalid or has expired. Please request a new link.'
        })

    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not password or not confirm_password:
            return render(request, 'reset_password.html', {
                'error': 'Please provide both password fields.'
            })

        if password != confirm_password:
            return render(request, 'reset_password.html', {
                'error': 'Passwords do not match. Please re-enter matching passwords.'
            })

        if len(password) < 6:
            return render(request, 'reset_password.html', {
                'error': 'Password must be at least 6 characters in length.'
            })

        user.password = make_password(password)
        user.save()

        messages.success(request, "Password has been reset successfully! You can now sign in with your new password.")
        return redirect('login')

    return render(request, 'reset_password.html')
