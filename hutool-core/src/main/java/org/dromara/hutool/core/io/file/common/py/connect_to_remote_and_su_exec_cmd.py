from config_tool import get_config
from config_tool import get_cur_dir
from shell import *
from time_tool import time_util


def main():
    config = get_config()
    ip = config['ip']
    port = config['port']
    username = config['username']
    password = config['password']
    root_password = config['root_password']

    if ip is None:
        ip = os.getenv('ip')
    if not password:  # empty
        password = os.getenv('password')

    ssh = ssh_remote(ip, port, username, password)

    test1(ip, password, root_password, ssh, username)

    test2(ssh)

    ssh.close()


def test2(ssh):
    print("####################")
    invoke_shell = InvokeShell(ssh, 10)
    invoke_shell.ssh_another_server('{ip2}', 'ubuntu', os.getenv('password2'), 3)
    print(invoke_shell.exec_cmd('docker ps'))
    # print(invoke_shell.su_root(root_password))
    print(invoke_shell.su_root_by_sudo())
    print(invoke_shell.exec_cmd('docker ps'))
    invoke_shell.close()


def test1(ip, password, root_password, ssh, username):
    root_shell = SuRootShell(ssh, root_password, None)
    # debug
    # print(root_shell.exec_cmd("watch 'docker ps'"))
    # print(root_shell.exec_cmd_debug('cd /bk/00proxy-watcher/mylogs; tail -6f mylog.2024-07-02.log'))
    rs_file1 = "/tmp/t1/" + time_util.get_cur_time_str() + ".txt"
    rs_file2 = "/tmp/t2/" + time_util.get_cur_time_str() + ".txt"
    print(root_shell.exec_cmd('chmod -R 777 /tmp'))
    sftp = ssh.open_sftp()
    sftp.put(os.path.join(get_cur_dir(), 'shell', 'sh1.sh'), '/tmp/t1/sh1.sh')
    print(root_shell.exec_cmd(f'sh /tmp/t1/sh1.sh {rs_file1}'))
    connect_to_another_server(root_shell)
    # continue connecting (yes/no/[fingerprint])?
    # print(root_shell.exec_with_expect(f'ssh ubuntu@{ip}\n', 'password:', 3))
    # print(root_shell.exec_with_expect(f'{password}\n', 'ubuntu@', 3))
    print('----------------')
    print(root_shell.ssh_another_server(ip, username, password, 3))
    print('-----------------------------')
    print(root_shell.exec_with_expect('docker ps\n', f'{username}@', 3))
    print('end')
    # print(root_shell.exec_cmd("docker ps"))
    # print(root_shell.exec_cmd("java --help"))
    sftp.close()
    root_shell.close()


def connect_to_another_server(root_shell):
    print(root_shell.exec_with_expect('ssh ubuntu@{ip2}\n', 'password:', 3))
    password2 = os.getenv('password2')
    print(root_shell.exec_with_expect(password2 + '\n', 'zhu-202.96-ubuntu@', 3))
    print(root_shell.exec_with_expect('ifconfig\n', 'zhu-202.96-ubuntu@', 3))
    print(root_shell.exec_with_expect('sudo su\n', 'zhu-202.96-root@', 3))
    print(root_shell.exec_with_expect('docker ps\n', 'zhu-202.96-root@', 3))
    # print(root_shell.exec_with_expect('exit\n', 'zhu-202.96-ubuntu@', 3))
    # print(root_shell.exec_cmd('exit\n'))
    # print(root_shell.exec_cmd('docker ps\n'))


if __name__ == '__main__':
    main()
