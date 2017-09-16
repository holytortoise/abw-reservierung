import os

os.system('sudo supervisorctl stop abwreservierung && git pull && sudo supervisorctl start abwreservierung')
