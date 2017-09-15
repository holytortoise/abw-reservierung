import os
import datetime
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import models as m

from apscheduler.schedulers.background import BackgroundScheduler

from reservierung import models


class Command(BaseCommand):
    help = 'Scheduler für alle Wiederkehrenden Aktivitäten auf dem Server'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_job(alte_reservierungen, 'cron',
                          day_of_week='mon-fri', hour=17)
        scheduler.add_job(print_current_time, 'interval', seconds=5)
        scheduler.start()

        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()


def alte_reservierungen():
    """
    Entfernt alle Reservierungen die von Tagen früher als heute sind
    """
    reservierungen = models.Reservierung.objects.all()
    for reservierung in reservierungen:
        if reservierung.endDatum < datetime.date.today():
            print(reservierung)
            reservierung.delete()
