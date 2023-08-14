import os

USERNAME = os.getlogin()
from .Settings import Settings

with open(f'C:/Users/{USERNAME}/Documents/Ableton/User Library/Remote Scripts/log.txt', 'a') as f:
    if Settings.LOGGING:
        f.write('====================\n')
log_num = 0

def log(message):
    global log_num
    with open(f'C:/Users/{USERNAME}/Documents/Ableton/User Library/Remote Scripts/log.txt', 'a') as f:
        if Settings.LOGGING:
            f.write(str(log_num) + ' ' + message + '\n')
    log_num += 1