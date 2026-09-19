from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from patientapp.forms import *
from .models import patientsignup


# Create your views here.



def home(request):

    user = None

    if 'userid' in request.session:
        user = patientsignup.objects.filter(id=request.session['userid']).first()
    return render(request, 'home.html', {'user': user})

def signup(request):
    if request.method=='POST':
        form=SignupForm(request.POST)
        if form.is_valid():
            form.save()
            print("Signup Successfully!")
            return redirect('login')
        else:
            print(form.errors)
    return render(request,'signup.html')



def login(request):
    if request.method == 'POST':
        unm = request.POST.get('email')
        pas = request.POST.get('password')

        user = patientsignup.objects.filter(email=unm).first()

        if user and check_password(pas, user.password):
            print("Login Successfully!")
            print("UserID:", user.id)

            request.session['user'] = user.email
            request.session['userid'] = user.id
            request.session['username'] = user.username

            return redirect('/')

        else:
            print("Error! Login failed....")

            return render(request, 'login.html', {
                'error': 'Invalid email or password'
            })

    return render(request, 'login.html')

def logout(request):
    request.session.flush()
    return redirect('/')


def profile(request):
    if 'userid' not in request.session:
        return redirect('login')

    user = patientsignup.objects.get(id=request.session['userid'])

    return render(request, 'profile.html', {'user': user})


def edit_profile(request):
    if 'userid' not in request.session:
        return redirect('login')

    user = patientsignup.objects.get(id=request.session['userid'])

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

            return redirect('profile')

    else:
        form = ProfileForm(instance=user)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': user
    })

def forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()

        # Check whether email is registered
        user = patientsignup.objects.filter(email=email).first()

        if not user:
            return render(request, 'forgot_password.html', {
                'error': 'This email is not registered. Please sign up first.'
            })

        # Create secure token
        signer = TimestampSigner()

        uid = urlsafe_base64_encode(
            force_bytes(user.id)
        )

        token = signer.sign(str(user.id))

        reset_link = request.build_absolute_uri(
            f'/reset-password/{uid}/{token}/'
        )

        subject = 'MediCare - Password Reset'

        message = f"""
Hello {user.username},

You requested to reset your MediCare password.

Click the link below to reset your password:

{reset_link}

This link will expire after 1 hour.

If you did not request this password reset, please ignore this email.

Regards,
MediCare
"""

        # Send ONLY to the registered email
        send_mail(
            subject,
            message,
            None,
            [user.email],
            fail_silently=False
        )

        return render(request, 'forgot_password.html', {
            'success': 'Password reset link has been sent to your registered email address.'
        })

    return render(request, 'forgot_password.html')

def reset_password(request, uidb64, token):

    try:
        # Decode user ID
        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        user = patientsignup.objects.get(id=uid)

        # Verify token and check expiration
        signer = TimestampSigner()

        signed_user_id = signer.unsign(
            token,
            max_age=3600
        )

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
            'error': 'This password reset link is invalid or has expired.'
        })

    if request.method == 'POST':

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or not confirm_password:

            return render(request, 'reset_password.html', {
                'error': 'Please enter both passwords.'
            })

        if password != confirm_password:

            return render(request, 'reset_password.html', {
                'error': 'Passwords do not match.'
            })

        if len(password) < 6:

            return render(request, 'reset_password.html', {
                'error': 'Password must be at least 6 characters.'
            })

        # Hash the new password
        user.password = make_password(password)

        user.save()

        return redirect('login')

    return render(request, 'reset_password.html')