import os

os.system('sudo supervisorctl stop abwreservierung && git pull -b development https://github.com/holytortoise/abwreservierung.git && sudo supervisorctl start abwreservierung')
