import paramiko
import time
import sys
import re
import os
import threading


def print_progress(cur, total, cost_time, filename = ''):
    rate = cur / total
    # 40 is total num of progress bar
    cur_num = int(rate * 40)
    s = ('\rsftp downloading {}:' + '=' * cur_num + ' ' * (40 - cur_num) + '|').format(filename)
    print('{}{:10.4}% ({}/{}) {:5.4}MB/s'.format(s, cur/total*100, cur, total, cur/1024/1024/cost_time), end='')

class InterSsh:
    def __init__(
        self, 
        host,
        username,
        password,
        port = 22
    ):
        self._host = host
        self._username = username
        self._password = password
        self._port = port

        tran = paramiko.Transport(sock=(self._host, self._port))
        tran.connect(username = self._username, password = self._password)
        channel = tran.open_session()
        channel.get_pty()
        channel.invoke_shell()
        self._tran = tran
        self._channel = channel
        if not self._wait_result(timeout = 3):
            print("err: connect {} timeout!".format(host))

        self._sftp = paramiko.SFTPClient.from_transport(tran)


    def _wait_result(self, ends = None, timeout = 60, show = False):
        result = ''
        pattern = (ends, '# ','? ', ': ') if ends else ('# ', '? ', ': ')
        timer = time.time()
        while True:
            res = self._channel.recv(65535).decode('utf8')
            if res:
                timer = time.time()
                result += res
                if res.endswith(pattern):
                    if show:
                        sys.stdout.write(result.strip('\n'))
                    return True
            elif (time.time() - timer > timeout):
                return False
            time.sleep(0.1)


    def _send(
        self,
        cmd,
        wait = True,
        ends = None,
        timeout = 60,
        show = False
    ):
        if cmd:
            self._channel.send(cmd + '\n')
            if wait and not self._wait_result(ends, timeout, show):
                print("warning: wait for result of cmd:{} timeout!".format(cmd))

    def send(
        self,
        cmd,
        wait = True,
        ends = None,
        timeout = 60,
        show = False
    ):
        cmds = cmd.split(';')
        for i in cmds:
            self._send(i, wait, ends, timeout, show)


    def _callback(self, cur, total):
        if time.time()-self.last_print_time < 0.05 and cur != total:
            return 
        print_progress(cur, total, time.time() - self.start_time, self._filename)
        self.last_print_time = time.time()


    def download(self, remote_path, local_path):
        self.start_time = time.time()
        self.last_print_time = 0
        self._filename = os.path.basename(remote_path)
        self._sftp.get(remote_path, local_path, self._callback)
        print('')


    def close(self):
        self._tran.close()


    def __del__(self):
        self.close()

def download_log(*args):
    filename = args[1]
    host = args[0]
    test = InterSsh(host, 'root', 'root@123aa', 22)
    test.send('rm -r -f ./*;mkdir test;cd test;rm -r -f ./*;touch f1 f2 f3 f4 f5;cd ..;tar -cvf {} ./*'.format(filename))
    test.download('/root/' + filename, 'D:/' + filename)


for i in range(2):
    hostlist = ['192.168.188.128', '192.168.188.129']
    t = threading.Thread(target=download_log, args=(hostlist[i],hostlist[i]+'_test{}.tgz'.format(i)))
    t.start()
    t.join()