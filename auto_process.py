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
    os.system('cd src && python manage.py alte_reservierungen')

scheduler = BlockingScheduler()
scheduler.add_job(update, 'cron', day_of_week='sun', hour=12)
scheduler.add_job(alte_reservierungen, 'cron', day_of_week="mon-fri", hour=17)
scheduler.start()
