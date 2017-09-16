import os
import datetime
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import models as m

from apscheduler.schedulers.blocking import BlockingScheduler

from reservierung import models


class Command(BaseCommand):
    help = 'Entfernen der alten Reservierungen'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        alte_reservierungen()


def alte_reservierungen():
    """
    Entfernt alle Reservierungen die von Tagen früher als heute sind
    """
    reservierungen = models.Reservierung.objects.all()
    for reservierung in reservierungen:
        if reservierung.endDatum < datetime.date.today():
            print(reservierung)
            reservierung.delete()
