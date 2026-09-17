from django import forms
from .models import *

class SignupForm(forms.ModelForm):
    class Meta:
        model=patientsignup
        fields='__all__'