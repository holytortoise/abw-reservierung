import os
import datetime
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import models as m

from apscheduler.schedulers.blocking import BlockingScheduler

from reservierung import models


class Command(BaseCommand):
    help = 'Scheduler für alle Wiederkehrenden Aktivitäten auf dem Server'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        scheduler = BlockingScheduler()
        scheduler.add_job(alte_reservierungen, 'cron',
                          day_of_week='mon-fri', hour=17)
        scheduler.start()


def alte_reservierungen():
    """
    Entfernt alle Reservierungen die von Tagen früher als heute sind
    """
    reservierungen = models.Reservierung.objects.all()
    for reservierung in reservierungen:
        if reservierung.endDatum < datetime.date.today():
            print(reservierung)
            reservierung.delete()
