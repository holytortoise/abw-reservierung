import os
from auto_process import alte_reservierungen

os.system('sudo supervisorctl stop abwreservierung && git pull && sudo supervisorctl start abwreservierung')

alte_reservierungen()
