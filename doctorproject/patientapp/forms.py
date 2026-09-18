from django import forms
from .models import *

class SignupForm(forms.ModelForm):
    class Meta:
        model=patientsignup
        fields='__all__'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = patientsignup
        fields = [
            'username',
            'email',
            'mobile',
            'dob',
            'gender',
            'city',
            'state',
            'profile_pic'
        ]

