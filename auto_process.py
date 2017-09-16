import os
from apscheduler.schedulers.blocking import BlockingScheduler

def update():
    """
    Automatisches Update des Reservierungssystems über Github
    """
    os.system('sudo supervisorctl stop abwreservierung && git pull && sudo supervisorctl start abwreservierung')

def alte_reservierungen():
    """
    Automatisches entfernen der alten Reservierungen
    """
    os.system('source /home/webserver/django-server/bin/activate && cd src && python manage.py alte_reservierungen')

s_update = BlockingScheduler()
s_update.add_job(update, 'cron', day_of_week='sun', hour=12)
s_update.start()

s_alt = BlockingScheduler()
s_alt.add_job(alte_reservierungen, 'cron', day_of_week="mon-fri", hour=17)
s_alt.start()
