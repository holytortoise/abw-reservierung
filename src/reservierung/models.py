from django.db import models
# Zugriff auf die Benutzer
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

import datetime
# Create your models here.


class Raum(models.Model):
    name = models.CharField(max_length=255)
    nummer = models.CharField(max_length=255)

    def get_name(self):
        return "{}.{}".format(self.nummer, self.name)

    def __str__(self):
        return "{}.{}".format(self.nummer, self.name)

    class Meta:
        verbose_name_plural = 'Räume'


class Reservierung(models.Model):
    reserviert_von = models.ForeignKey(User, related_name="Reserved")
    reservierterRaum = models.ForeignKey(Raum)
    reservierungsGrund = models.TextField(default="Unterricht")
    anfangsDatum = models.DateField("Start Datum", default=datetime.date.today)
    endDatum = models.DateField("End Datum", default=datetime.date.today)
    anfangsZeit = models.TimeField("Reserviert von")
    endZeit = models.TimeField("Reserviert bis")
    taeglich = models.BooleanField("Taeglich", default=False)

    def get_absolute_url(self):
        return reverse('reservierung:index')

    def create_choice(self):
        choice = []
        try:
            rooms = Raum.objects.all()
            for room in rooms:
                choice.append((room.id, room.get_name()))
        except:
            pass
        return choice

    def __str__(self):
        return "Reservnr: {}".format(self.id)

    class Meta:
        verbose_name_plural = 'Reservierungen'
        ordering = ['reservierterRaum', 'anfangsDatum','anfangsZeit']
