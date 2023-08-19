import os

USERNAME = os.getlogin()
from .Settings import Settings

if Settings.LOGGING:
    with open(f'C:/Users/{USERNAME}/Documents/Ableton/User Library/Remote Scripts/log.txt', 'a') as f:
        f.write('====================\n')
log_num = 0

def log(message):
    global log_num
    if Settings.LOGGING:
        with open(f'C:/Users/{USERNAME}/Documents/Ableton/User Library/Remote Scripts/log.txt', 'a') as f:
            if type(message) == list:
                message = '\n'.join(message)
            f.write(str(log_num) + ' ' + message + '\n')
    log_num += 1