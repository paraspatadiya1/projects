from django import forms
from .models import patientsignup
from django.contrib.auth.hashers import make_password


class SignupForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        max_length=100
    )

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
            'password',
            'profile_pic'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        # Hash the password before saving
        user.password = make_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


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