from django import forms
from django.contrib.auth.models import User


class SchilderLoginForm(forms.Form):
    model = User()
    username = forms.CharField(label="Benutzername")
    password = forms.CharField(label="Passwort",widget=forms.PasswordInput)
