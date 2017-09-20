from django import forms
from django.contrib.auth.models import User


class SchilderLoginForm(forms.Form):
    model = User()
    username = forms.CharField(label="Benutzername")
    password = forms.CharField(label="Passwort",widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(ReservierungForm, self).clean()
        f_username = cleaned_data.get("username")
        f_password = cleaned_data.get("password")

        if username and password:
            # Only do something if both fields are valid so far.
            if authenticate(username=f_username, password=f_password):
                raise forms.ValidationError("Nutzername oder Passwort ist falsch")
