import paramiko
import os
import _thread
import time
import sys
from InterSsh import InterSsh

class Downloader:

    def print_progress(cur, total, cost_time, filename = ''):
        rate = cur / total
        # 40 is total num of progress bar
        cur_num = int(rate * 40)
        s = ('\rsftp downloading {}:' + '=' * cur_num + ' ' * (40 - cur_num) + '|').format(filename)
        print('{}{:10.4}% ({}/{}) {:5.4}MB/s'.format(s, cur/total*100, cur, total, cur/1024/1024/cost_time), end='')


    def __init__(
        self, 
        host,
        username,
        password,
        port = 22
    ) -> None:
        self._ssh = InterSsh(host=host, username=username, password=password, port=port)
        self._sftp = paramiko.SFTPClient.from_transport(self._ssh.tran)
        

    def _callback(self, cur, total):
        if time.time()-self.last_print_time < 0.05 and cur != total:
            return 
        Downloader.print_progress(cur, total, time.time() - self.start_time, self._filename)
        self.last_print_time = time.time()


    def _downloard(self):
        self.start_time = time.time()
        self.last_print_time = 0
        self._sftp.get('/root/openEuler-22.03-LTS-SP1-x86_64-dvd.iso', 'E:/fff.iso', self._callback)
        print('')


    def download(self, remote):
        self._ssh.send('mkdir test;cd test;touch f1;touch f2;touch f3')
        self._ssh.send('cd ..;tar -zcvf f.tgz test/*')
        self._filename = 'f.tgz'
        self._downloard()
        self._ssh.send('rm -f /root/f.tgz')


l = Downloader('192.168.188.128', 'root', 'root@123aa', 22)
l.get_log()

