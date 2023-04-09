import time
a=0
c=0
q='sftp :'
t = 20
while a < 67:
    a += 1
    b = a / 67
    s = q + ('=' * int((b*20))) + (' ' * (20-int(b*20))) + '|'
    print('\r{}{:20.4}%  ({}/{})'.format(s,b*100,a,67),end='')
    time.sleep(0.05)