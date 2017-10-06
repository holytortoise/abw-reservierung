import os
from decouple import config

sudoPassword = config('SUDOPASSWORD')

def update():
    """
    Automatisches Update des Reservierungssystems über Github
    """
    try:
        command_stop = 'sudo supervisorctl stop abwreservierung && sudo supervisorctl start abwreservierung && sudo chmod +x startup'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command_stop))
    except:
        pass
    try:
        os.system('cd /home/webserver/abwreservierung && git pull')
    except:
        pass
    try:
        command_start = 'sudo supervisorctl start abwreservierung'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command_start))
    except:
        pass
    try:
        command_chmod = 'sudo chmod +x startup'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command_chmod))
    except:
        pass

def alte_reservierungen():
    """
    Automatisches entfernen der alten Reservierungen
    """
    os.system("/bin/bash -c 'source ../django-server/bin/activate && python src/manage.py alte_reservierungen && deactivate'")

scheduler = BlockingScheduler()
scheduler.add_job(update, 'cron', day_of_week='sun', hour=12)
scheduler.add_job(alte_reservierungen, 'cron', day_of_week="mon-fri", hour=17)
scheduler.start()
