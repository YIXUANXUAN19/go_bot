import logging
import os.path
import time
from flask import Flask, request
from QBot.lib.utils import getconf, getdata, linuxGetPid, linuxGetPort
from QBot.lib.log import BASE_DIR, logger
from QBot.handle_message.handle import verifiedMes
from QBot.core import main_bot

# 实例化，可视为固定格式
app = Flask(__name__)


# route()方法用于设定路由；类似spring路由配置
@app.route('/', methods=['POST'])
def post_data():
    data_json = request.get_json()
    data_json['bot_ip'] = get_bot_ip()
    if verifiedMes(data_json):
        main_bot(data_json)
    return "OK"


@app.route('/test', methods=['get'])
def tmp():
    return "OK"


def run():
    # 5910端口：go-cqhttp机器人服务端口
    # 5911端口：go-cqhttp反向post端口，通过flask来接收数据
    '''
    当调用app.run()的时候，用到了Werkzeug库，它会生成一个子进程，当代码有变动的时候它会自动重启
    如果在run（）里加入参数 use_reloader=False，就会取消这个功能，当然，在以后的代码改动后也不会自动更新了。
    可以查看WERKZEUG_RUN_MAIN环境变量， 默认情况下，调用子程序时，它会被设置为True。
    '''
    logging.info('正在开启flask监听')
    cp = getconf('QBot', 'config/config.cfg')

    ipaddr = getdata(cp, "Bot", "IPADDR")
    port = getdata(cp, "Bot", "WEBSOCKET_PORT")
    app.run(debug=False, port=port, host=ipaddr)


def init_env():
    """
    1、写入重启shell脚本
    2、导入config配置为bot的配置
    """
    info = '*' * 20 + ' start ' + '*' * 20
    logger.info(info)
    logging.info('正在初始化环境')

    """检测端口是否被占用"""
    cp = getconf('QBot', 'config/config.cfg')
    WEBSOCKET_PORT = getdata(cp, "Bot", "WEBSOCKET_PORT")
    port = linuxGetPort(WEBSOCKET_PORT)
    if port:  # 当前端口占用
        logging.info(f'端口 {WEBSOCKET_PORT}--{port}（配置文件端口--已被占用端口） 已被占用，请检查或更换端口！')
        exit(0)

    """写入重启shell脚本"""
    os.chdir(BASE_DIR)
    with open('restart.sh', 'w', encoding='utf8') as f:
        a = "{"
        b = "}"
        restart_sh = f"""#!/usr/bin/env bash
# cd {BASE_DIR}
name="{FILE_NAME}"
pid=$(ps -aux | grep "$name" | awk '{a}print$2{b}')
# echo $pid

for i in $pid ; do
  kill -9 "$i" &>/dev/null
done
sleep 3
nohup python3 "$name" > /dev/null 2>&1 &

# pid=$(ps -aux | grep "$name" | awk '{a}print$2{b}')
# echo $pid

# for i in $pid ; do
#   echo "$i" >'.reboot_cache'
#   break
# done
"""
        f.write(restart_sh)
        f.flush()

    """更改bot的配置文件"""
    logging.info('更改bot的配置文件')
    bot_file = os.path.join(BASE_DIR, 'bot')
    os.chdir(bot_file)
    if os.path.exists('config.yml'):
        config_file = os.path.join(bot_file, 'config.yml')
        cp = getconf('QBot', 'config/config.cfg')

        ipaddr = getdata(cp, "Bot", "IPADDR")
        port = getdata(cp, "Bot", "PORT")
        websocket_port = getdata(cp, "Bot", "WEBSOCKET_PORT")
        WEBSOCKET_TIMEOUT = getdata(cp, "Bot", "WEBSOCKET_TIMEOUT")
        bot_qq = getdata(cp, "Bot", "BOT_QQ").strip('"')
        bot_pass = getdata(cp, "Bot", "BOT_PASS")
        logging.info(f'机器人QQ：{bot_qq}')
        replace_list = {'      host:': f'      host: {ipaddr}',  # 机器人的ip
                        '      port: ': f'      port: {port}',  # 机器人的端口
                        '      timeout:': f'      timeout: {WEBSOCKET_TIMEOUT}',  # 反向post超时时间
                        '      - url: ': f'      - url: \'http://{ipaddr}:{websocket_port}\'',  # 反向post地址
                        '  uin:': f'  uin: {bot_qq}',  # 机器人的qq号
                        '  password:': f"  password: {bot_pass}"  # 机器人qq的密码
                        }
        f = open(config_file, 'r', encoding='utf-8')
        result = f.read()
        for i in result.split('\n'):
            for key, value in replace_list.items():
                if key in i:
                    # 把包含key的行替换成key的values
                    result = result.replace(i, value)
        f.close()
        with open(config_file, 'w', encoding='utf-8') as f:
            # 覆盖原先的配置文件
            f.write(result)
        logging.info('配置文件更改完成')
    os.chdir(BASE_DIR)
    return True


def start_plugin():
    """
    检测目录是否有插件，如果有则插件使用独立后台运行
    """
    file = os.path.join(BASE_DIR, 'independent')
    os.chdir(file)
    plugins = os.listdir(file)
    for plugin in plugins:
        if not plugin.endswith('py') and not plugin.endswith('sh'): continue

        # 检测是否有之前运行的插件进程，关闭重新开启，防止开启多个相同进程
        for pid in linuxGetPid(plugin):
            logging.info(f'检测到插件{plugin}正在运行, 执行 kill {pid}')
            os.system(f'kill -9 {pid}')
            time.sleep(0.2)

        # 后台运行插件
        logging.info(f'正在开启插件：{plugin}')
        os.system(f'nohup python3 {plugin} > {plugin}.log 2>&1 &')
        pid = linuxGetPid(plugin)
        logging.info(f'成功：{plugin}') if pid else logging.info(f'失败：{plugin},pid:{pid}')
        os.chdir(BASE_DIR)
    return True


def get_bot_ip():
    cp = getconf('QBot', "config/config.cfg")
    port = getdata(cp, "Bot", "PORT")
    ip = getdata(cp, "Bot", "IPADDR")
    return f'http://{ip}:{port}'


if __name__ == '__main__':
    FILE_NAME = os.path.basename(__file__)  # 当前运行的文件的名字
    if init_env():
        if start_plugin():
            run()
