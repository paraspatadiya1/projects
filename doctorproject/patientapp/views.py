from django.core.serializers import python
from django.http import request
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.contrib.auth.hashers import check_password

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

        email = request.POST.get('email')

        user = patientsignup.objects.filter(email=email).first()

        if user:
            return render(request, 'forgot_password.html', {
                'success': 'Email address found. We can now send the reset link.'
            })

        else:
            return render(request, 'forgot_password.html', {
                'error': 'No account found with this email address.'
            })

    return render(request, 'forgot_password.html')