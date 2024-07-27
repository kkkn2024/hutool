import psutil
from psutil import AccessDenied
import sys


def print_process(process):
    print(f'{process=}')
    try:
        print(f"cmdline={' '.join(process.cmdline())}")
    except:
        pass
    try:
        print(f'cwd={process.cwd()}')
    except:
        pass
    try:
        parent = process.parent()
        print(f"parent={parent}")
    except:
        pass
    try:
        children = process.children()
        if children is None or len(children) == 0:
            return
        print("-------------children-----------")
        for child in children:
            if child.name() == 'conhost.exe':
                continue
            print_process(child)
    except:
        pass


# 是否直接其他进程调用，调用方式my_psutil.py 3 cmd_search_key
exec_not_input = False
cmd_search_key = None
if len(sys.argv) == 3 and sys.argv[1] == '3':
    exec_not_input = True
    cmd_search_key = sys.argv[2]

while True:
    if not exec_not_input:
        print("""
查询进程:
1)按进程号查询
2)按进程名关键字查询（不少于4个字符）
3)按命令行关键字查询（不少于4个字符）
9)结束
        """)
        print("请选择:")
    if exec_not_input:
        choose = '3'
    else:
        choose = input()
    if choose == '1':
        print('输入进程号:')
        try:
            pid = int(input())
            process = psutil.Process(pid)
            print_process(process)
        except Exception as e:
            print('error=', e)
    elif choose == '2':
        print("输入关键字:")
        search_key = input()
        if len(search_key) < 4:
            continue
        pids = psutil.pids()
        count = 0
        for pid in pids:
            try:
                process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            except Exception as e:
                pass
            if search_key in process.name().lower():
                count += 1
                print(f"------------------------{count}")
                print_process(process)
    elif choose == '3':
        if exec_not_input:
            search_key = cmd_search_key
        else:
            print("输入命令行关键字:")
            search_key = input()
            if len(search_key) < 4:
                continue
        pids = psutil.pids()
        count = 0
        for pid in pids:
            try:
                process = psutil.Process(pid)
                try:
                    if search_key.lower() in " ".join(process.cmdline()).lower():
                        count += 1
                        print(f"------------------------{count}")
                        print_process(process)
                except AccessDenied as e:
                    pass
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                pass
        if exec_not_input:
            break
    elif choose == '9':
        break
