from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'gender')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
