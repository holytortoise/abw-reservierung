import os
from decouple import config

sudoPassword = config('SUDOPASSWORD')

def update():
    """
    Automatisches Update des Reservierungssystems über Github
    """
    command = 'sudo supervisorctl stop abwreservierung && cd /home/webserver/abwreservierung && git pull && sudo supervisorctl start abwreservierung && sudo chmod +x startup'
    os.system('echo %s|sudo -S %s' % (sudoPassword, command))

def alte_reservierungen():
    """
    Automatisches entfernen der alten Reservierungen
    """
    os.system("/bin/bash -c 'source ../django-server/bin/activate && python src/manage.py alte_reservierungen && deactivate'")

update()
alte_reservierungen()
