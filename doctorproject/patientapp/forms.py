from django import forms
from .models import patientsignup
from django.contrib.auth.hashers import make_password


class SignupForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control glass-input',
            'placeholder': 'Create a password (min 6 chars)',
            'autocomplete': 'new-password'
        }),
        min_length=6,
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
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'e.g. rahul_sharma',
                'maxlength': '20'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'name@example.com'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': '10-digit mobile number',
                'maxlength': '10'
            }),
            'dob': forms.DateInput(attrs={
                'class': 'form-control glass-input',
                'type': 'date'
            }),
            'gender': forms.Select(
                choices=[
                    ('', 'Select Gender'),
                    ('Male', 'Male'),
                    ('Female', 'Female'),
                    ('Other', 'Other')
                ],
                attrs={'class': 'form-select glass-input'}
            ),
            'city': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'e.g. Mumbai'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'e.g. Maharashtra'
            }),
            'profile_pic': forms.FileInput(attrs={
                'class': 'form-control glass-input'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if patientsignup.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        if patientsignup.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            s_mobile = str(mobile).strip()
            if not s_mobile.isdigit() or len(s_mobile) != 10:
                raise forms.ValidationError("Please enter a valid 10-digit mobile number.")
        return mobile

    def save(self, commit=True):
        user = super().save(commit=False)
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
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'Username',
                'maxlength': '20'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'Email address'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': '10-digit mobile number',
                'maxlength': '10'
            }),
            'dob': forms.DateInput(attrs={
                'class': 'form-control glass-input',
                'type': 'date'
            }),
            'gender': forms.Select(
                choices=[
                    ('', 'Select Gender'),
                    ('Male', 'Male'),
                    ('Female', 'Female'),
                    ('Other', 'Other')
                ],
                attrs={'class': 'form-select glass-input'}
            ),
            'city': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control glass-input',
                'placeholder': 'State'
            }),
            'profile_pic': forms.FileInput(attrs={
                'class': 'form-control glass-input'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        query = patientsignup.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise forms.ValidationError("Another patient account is already using this email address.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        query = patientsignup.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise forms.ValidationError("This username is already taken by another account.")
        return username

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            s_mobile = str(mobile).strip()
            if not s_mobile.isdigit() or len(s_mobile) != 10:
                raise forms.ValidationError("Please enter a valid 10-digit mobile number.")
        return mobile
