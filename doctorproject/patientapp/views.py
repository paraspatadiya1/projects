from django.core.serializers import python
from django.http import request
from django.shortcuts import render,redirect
from .models import *
from .forms import *

# Create your views here.



def home(request):
    return render(request, 'home.html')


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

        user = patientsignup.objects.filter(email=unm,password=pas).first()

        if user:
            print("Login Successfully!")
            print("UserID:", user.id)

            request.session['user'] = user.email
            request.session['userid'] = user.id
            request.session['username'] = user.name

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



