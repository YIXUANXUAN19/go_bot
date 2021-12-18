# coding=utf-8
import configparser
import logging
import pkgutil
import os


# 读取配置文件
def getconf(package_name, file_name):
    try:
        cp = configparser.RawConfigParser()
        resp = pkgutil.get_data(package_name, file_name).decode('utf-8')
        cp.read_string(resp)
        return cp
    except Exception as e:
        logging.error('read_config_properties_faild:%s' % e)
        return ''


# 读取配置文件内的数据
def getdata(cp, session, app_name):
    try:
        res = cp.get(session, app_name)
        return res
    except configparser.NoOptionError as e:
        return 'unconfig'  # 未写配置
    except Exception as e:
        logging.error('read_properties_faild:%s' % e)
        return ''


def linuxGetPid(process_name):
    """
    只看python脚本或sh脚本或可执行文件,类似./filename
    传入进程名字，返回进程pid,  TODO 文件加锁？
    :param process_name: 进程的名字
    :return: list:进程id
    """
    # import fcntl  # 文件锁
    # import time
    # tmp_file = f'.tmp{str(int(time.time()))[:5]}{random.randint(0, 100)}'
    # os.system(f'`ps -ef | grep {process_name} > {tmp_file}`')  # 用当前时间做文件名，防冲突，临时办法
    # f = open(tmp_file, 'r', encoding='utf8')
    # res = f.readlines()
    # f.close()
    # os.system(f'rm -f {tmp_file}')  # 删除临时文件
    # pid_list = list()
    # for pid in res:
    #     # 只看python脚本或sh脚本，防止因为名字重复错杀
    #     # if process_name in pid and 'grep --color=auto' not in pid and ('python' in pid or '.sh' in pid):
    #     if process_name in pid and 'grep' not in pid and 'grep --color=auto' not in pid and (
    #             'python' in pid or 'sh' in pid or './' in pid):
    #         logging.info(f'TEST_INFO:{pid}')
    #         pid_list.append(pid.split()[1])
    # return pid_list
    cmd = 'ps -ef | grep "%s"' % process_name
    with os.popen(cmd) as r:
        # os.popen() 以管道的方式执行cmd命令，返回一个文件对象
        result = r.read().split("\n")
        pid = [i.split()[1] for i in result if 'grep' not in i and ('python' in i or 'sh' in i or './' in i)]
        return pid


def linuxGetPort(port):
    """
    :return: list:port(占用中的)
    """
    # a, b = "{", "}"
    # cmd = f"netstat -anput |grep {port} | grep LISTEN | awk '{a}print $4{b}' | awk -F: '{a}print $2{b}'"
    cmd = "netstat -anput |grep %s | grep LISTEN | awk '{print $4}' | awk -F: '{print $2}'" % port
    with os.popen(cmd) as res:
        res = res.read().strip()
        return res.split('\n') if res else []


if __name__ == '__main__':
    print(linuxGetPid('123'))
    res = """root     17496     1  0 21:55 pts/1    00:00:00 python3 keep_alive.py
root     22725 22724  0 22:04 pts/0    00:00:00 /bin/sh -c ps -ef | grep "keep_alive.py"
root     22727 22725  0 22:04 pts/0    00:00:00 grep keep_alive.py"""
    pid = [i[1] for i in res.split("\n") if 'grep' not in i and ('python' in i or 'sh' in i or './' in i)]
