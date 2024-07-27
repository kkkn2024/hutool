import os
import subprocess

class ExecResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


# 这个会有多余的空行打印，exec_new()比较好，不会有空行
def exec_and_print_result(cmd, encode='gbk'):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line.decode(encode))  # 指定编码


# todo https://docs.python.org/zh-cn/3/library/subprocess.html#subprocess.PIPE
def exec_new(cmd, encode='gbk', timeout=10 * 60):
    process = subprocess.Popen(cmd, shell=False, encoding=encode, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(timeout=timeout)
    return ExecResult(process.returncode, stdout, stderr)


def exec(cmd):
    status = os.system(cmd)  # 输出会乱码
    if status != 0:
        print(f"exec status={status}")
