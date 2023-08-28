import os
from .Settings import Settings

USER_HOME = os.path.expanduser('~')
LOG_DIRECTORY = USER_HOME+"/Documents/Ableton/User Library/Remote Scripts"
os.makedirs(LOG_DIRECTORY, exist_ok=True)

LOG_FILE = LOG_DIRECTORY + "/log.txt"

if Settings.LOGGING:
    with open(LOG_FILE, 'a') as f:
        f.write('====================\n')
log_num = 0

def log(message):
    global log_num
    if Settings.LOGGING:
        with open(LOG_FILE, 'a') as f:
            if type(message) == list:
                message = '\n'.join(message)
            f.write(str(log_num) + ' ' + str(message) + '\n')
    log_num += 1