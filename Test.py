
with open('C:/Users/Daniel aka MrMatch/Documents/Ableton/User Library/Remote Scripts/log.txt', 'a') as f:
    f.write('====================\n')
log_num = 0

def log(message):
    global log_num
    with open('C:/Users/Daniel aka MrMatch/Documents/Ableton/User Library/Remote Scripts/log.txt', 'a') as f:
        f.write(str(log_num) + ' ' + message + '\n')
    log_num += 1