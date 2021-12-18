import os
import time
import json
import logging
import requests
from QBot.server import get_bot_ip
from QBot.plugins import reply
from QBot.lib.log import BASE_DIR
from QBot.lib.utils import getdata, getconf, linuxGetPid


def listen(data_json):
    """
    :return: first_tip true(下一次继续发送登录消息) false(下一次只监听是否在线)
    """
    logging.info('正在检查机器人是否运行')
    for i in range(10):
        try:
            if first_tip:
                res = reply.send_txt(data_json)
            else:
                res = requests.get(f'{data_json["bot_ip"]}/get_status')
            if json.loads(res.text).get('status') == 'ok':
                logging.info('机器运行')
                return res, False
        except Exception as e:
            logging.info(f'错误--{e}')
            time.sleep(1)
            continue
    return '', True


def start():
    bot_pid = linuxGetPid(f'./{BOT_FILE}')
    if not bot_pid:  # 如果机器人程序没有在运行,就开启
        os.chdir(os.path.join(BASE_DIR, 'bot'))
        os.system(f'./{BOT_FILE} -d faststart')  # 后台开启机器人
        logging.info('未检测到机器人运行， 正在开启机器人')
        time.sleep(8)
        return False
    else:
        logging.info(f"当前机器人正在运行 pid：{bot_pid}")
        time.sleep(3)
        return True


if __name__ == '__main__':
    cp = getconf('QBot', 'config/config.cfg')
    master = getdata(cp, 'QQ', 'MASTER')
    BOT_QQ = getdata(cp, 'Bot', 'BOT_QQ')
    fake_msg = {'bot_ip': get_bot_ip(), 'message_type': 'private', 'user_id': master, 'message': 'bot登录成功',
                'group_id': ''}
    BOT_FILE = 'go-bot'
    first_tip = True
    while True:
        # 每次重启后， 发送一次登录提示
        # if first_tip:
        # 如果消息发送失败，并且没有机器人的进程pid
        fake_msg['user_id'] = master
        response, first_tip = listen(fake_msg)
        if not response:
            start()
            continue
        time.sleep(60)

