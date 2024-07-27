import os
import subprocess
import time

import paramiko

from tool.exec_util import exec_and_print_result
from time_tool import *
import logging as log

from config_tool import get_cur_dir

# todo merge exec_util
import exec_util

log.basicConfig(
    level=log.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        log.FileHandler(os.path.join(get_cur_dir(), "log\\shell.log")),
        log.StreamHandler()
    ]
)
print('shell log ok')


class Shell:
    def __init__(self, cmd):
        self.process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def wait(self, timeout=10 * 60):
        stdout, stderr = self.process.communicate(timeout)
        return stdout, stderr


def ssh_remote(ip, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, port=port, username=username, password=password)
    # ??Expected type 'bytes | bytearray', got 'str' instead
    # ssh.invoke_shell().send('su root\n')
    return ssh


class ExecException(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvokeShell:
    def __init__(self, ssh, timeout=None):
        self.shell = ssh.invoke_shell()
        self.timeout = timeout

    def if_self_timeout(self, timer, msg):
        if self.timeout is not None:
            if timer.count_time() > self.timeout:
                self.close()
                raise Exception(f"{msg}")

    def su_root(self, root_password):
        log.debug('su root')
        self.shell.send('su root\n')
        buff = ''
        timer = Timer()
        while not buff.endswith('Password: '):
            self.if_self_timeout(timer, 'su root timeout')
            while self.shell.recv_ready():
                buff += self.shell.recv(9999).decode('utf-8')

            time.sleep(0.1)
        self.shell.send(root_password + '\n')

        buff = ''
        timer = Timer()
        while "root@" not in buff or not buff.strip().endswith('#'):
            if 'Authentication failure' in buff:
                log.error(f'error={buff}')
                break
            try:
                self.if_self_timeout(timer, 'su root password timeout')
            except Exception as e:
                log.error(f'error={buff}')
                raise e
            while self.shell.recv_ready():
                buff += self.shell.recv(9999).decode('utf-8')
        log.debug('su root ok')
        return buff

    def su_root_by_sudo(self):
        log.debug('sudo su root')
        self.shell.send('sudo su root\n')

        buff = ''
        timer = Timer()
        while "root@" not in buff or not buff.strip().endswith('#'):
            try:
                self.if_self_timeout(timer, 'su root password timeout')
            except Exception as e:
                log.error(f'error={buff}')
                raise e
            while self.shell.recv_ready():
                buff += self.shell.recv(9999).decode('utf-8')
        log.debug('sudo su root ok')
        return buff

    @staticmethod
    def if_timeout(timeout, timer, msg):
        log.debug(f'check if_timeout: {msg}')
        if timeout is not None:
            log.debug(f'debug={timer.count_time()} / {timeout}, {msg}')
            if timer.count_time() > timeout:
                raise ExecException(f"{msg} timeout")

    def close(self):
        self.shell.close()

    def exec_cmd(self, cmd):
        self.shell.send(cmd + '\n')
        buff = ''
        res = ''
        timer = Timer()
        while True:
            if (("root@" in res and res.strip().endswith('#'))
                    or ("@" in res and res.strip().endswith('$'))):
                break
            self.if_self_timeout(timer, 'SuRootShell exec_cmd timeout')
            resp = self.shell.recv(9999)
            buff += resp.decode('utf-8')
            res = buff.split('\r\n')[-1]
        return buff

    def ssh_another_server(self, ip, username, password, timeout=3):
        log.info(f'ssh to {username}@{ip}')
        self.shell.send(f'ssh {username}@{ip}\n')
        buff = ''
        res = ''
        timer = Timer()
        while ('password:' not in res) and ('yes/no' not in res):
            try:
                SuRootShell.if_timeout(timeout, timer, f'ssh_another_server: {username}@{ip}')
            except ExecException as e:
                log.error(f'error, buff={buff}')
                raise e
            while self.shell.recv_ready():
                buff += self.shell.recv(1024).decode('utf-8')
            res = buff.split('\r\n')[-1]
            time.sleep(0.2)
        log.debug(f'ssh to {username}@{ip}, buff={buff}')
        if 'yes/no' in res:
            self.shell.send('yes\n')
            buff = ''
            res = ''
            timer = Timer()
            while 'password:' not in buff:
                try:
                    SuRootShell.if_timeout(timeout, timer, f'ssh_another_server: {username}@{ip}')
                except ExecException as e:
                    log.error(f'error, buff={buff}')
                    raise e
                while self.shell.recv_ready():
                    buff += self.shell.recv(1024).decode()
                res = buff.split('\r\n')[-1]
                time.sleep(0.2)
            log.debug(f'ssh to {username}@{ip}, buff={buff}')
        self.shell.send(f'{password}\n')
        res = ''
        while True:
            if f'{username}@' in res and (res.strip().endswith('$') or res.strip().endswith('#')):
                break
            try:
                SuRootShell.if_timeout(timeout, timer, f'ssh_another_server enter password: {username}@{ip}')
            except ExecException as e:
                log.error(f'error, buff={buff}')
                raise e
            while self.shell.recv_ready():
                buff += self.shell.recv(1024).decode()
            res = buff.split('\r\n')[-1]
            time.sleep(0.2)
        return buff

    def exec_with_expect(self, cmd, expect_str, timeout=None):
        self.shell.send(f'{cmd}\n')
        log.debug(f'{cmd=}')
        buff = ''
        res = ''
        timer = Timer()
        while expect_str not in res:
            try:
                SuRootShell.if_timeout(timeout, timer, f'exec_with_expect: {cmd}')
            except ExecException as e:
                log.error(f'error, buff={buff}')
                raise e
            # todo
            while self.shell.recv_ready():
                buff += self.shell.recv(1024).decode()
            # resp = self.shell.recv(9999)
            # buff += resp.decode('utf-8')
            res = buff.split('\r\n')[-1]
            time.sleep(0.2)
        return buff

    def exec_cmd_debug(self, cmd):
        self.shell.send(cmd + '\n')
        buff = ''
        res = ''
        timer = Timer()
        while "root@" not in res:
            self.if_self_timeout(timer, 'SuRootShell exec_cmd timeout')
            resp = self.shell.recv(9999)
            buff += resp.decode('utf-8')
            res = buff.split('\r\n')[-1]
            # debug
            # print("buff========================\n", buff)
            # print("\n=================================")
            print(buff)
            buff = ''
        return buff


class SuRootShell(InvokeShell):
    def __init__(self, ssh, root_password, timeout=None):
        super().__init__(ssh, timeout)
        super().su_root(root_password)


def test():
    import os
    ret = os.system("tasklist2 | findstr py")
    print(f'{ret=}')
    print("===============")
    exec_and_print_result("tasklist | findstr py")
    print("-------------")
    shell = Shell("tasklist222 ")
    stdout, stderr = shell.wait()
    print('out=', stdout.decode("gbk"))
    print('error=', stderr.decode("gbk"))


if __name__ == "__main__":
    test()
