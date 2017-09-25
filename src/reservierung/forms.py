from django import forms
import datetime
from .models import Reservierung,Raum


# Create the form class
class ReservierungForm(forms.Form):
    choice = ()
    model = Reservierung()
    choice = model.create_choice()
    reservierterRaum = forms.ChoiceField(choice)
    reservierungsGrund = forms.CharField(max_length=255)
    anfangsDatum = forms.DateField()
    endDatum = forms.DateField()
    anfangsZeit = forms.TimeField(help_text='HH:mm')
    endZeit = forms.TimeField(help_text='HH:mm')
    taeglich = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(ReservierungForm, self).clean()
        anfangsdatum = cleaned_data.get("anfangsDatum")
        enddatum = cleaned_data.get("endDatum")
        anfangszeit = cleaned_data.get("anfangsZeit")
        endzeit = cleaned_data.get("endZeit")

        if anfangsdatum and enddatum:
            # Only do something if both fields are valid so far.
            if anfangsdatum < datetime.date.today():
                raise forms.ValidationError("Anfangsdatum kann nicht in der Vergangenheit liegen.")
            if anfangsdatum == datetime.date.today():
                if anfangszeit < datetime.datetime.now().time():
                    raise forms.ValidationError("Anfangszeit kann nicht in der Vergangenheit liegen")
            if anfangsdatum > enddatum:
                raise forms.ValidationError("Enddatum kann nicht vor Anfangsdatum sein")
            if anfangsdatum == enddatum:
                if anfangszeit > endzeit:
                    raise forms.ValidationError("Anfangs Zeit kann nicht nach der End Zeit liegen")
                if anfangszeit == endzeit:
                    raise forms.ValidationError("Anfangs und End Zeit können nicht gleich sein")
