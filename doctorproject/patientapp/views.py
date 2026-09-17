from django.shortcuts import render,redirect
from .models import *
from .forms import *

# Create your views here.


def home(request):
    return render(request,'home.html')

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
    if request.method=='POST':
        unm=request.POST['username']
        pas=request.POST['password']

        user=patientsignup.objects.filter(email=unm,password=pas)
        userid=patientsignup.objects.get(email=unm)
        print("UserID:",userid.id)
        if user:
            print("Login Successfully!")
            request.session['user']=unm
            request.session['userid']=userid.id
            return redirect('/')
        else:
            print("Error!Login faild....")
    return render(request,'login.html')

