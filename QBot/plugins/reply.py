# coding=utf-8
import logging
import requests
from requests.adapters import HTTPAdapter
from QBot.handle_message.handle import *


# get请求
def _get(url, timeout=10, max_retries=1):
    """
    get请求函数
    :param timeout: 请求超时时间，默认为10
    :param max_retries: 重试次数，默认为1
    :return: response
    """
    # 请求失败好像不需要重试， 如果失败go-cqhttp会自动重新上报
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=max_retries))
    s.mount('https://', HTTPAdapter(max_retries=max_retries))
    try:
        res = s.get(url, allow_redirects=True, timeout=timeout)
        if res:
            return res
    except requests.exceptions.RequestException:
        pass


def send_txt(data_json):
    """
    用机器人发送消息
    :param bot_api: 机器人的ip  例： http://127.0.0.1:5910
    :param data_json: 消息字典
    :return: response
    """
    msg_type = getType(data_json)
    send_id = getSenderQQ(data_json)
    msg = getMessage(data_json)
    bot_ip = data_json['bot_ip']
    if msg_type == 'private':
        url = f"{bot_ip}/send_private_msg?user_id={send_id}&message={msg}"
        return _get(url)

    elif msg_type == 'group':
        url = f"{bot_ip}/send_group_msg?group_id={getQunId(data_json)}&message=[CQ:at,qq={send_id}] {msg}"
        return _get(url)


def send_img(message, img):
    bpt_ip = message['bot_ip']
    msg_type = getType(message)
    send_id = getSenderQQ(message)
    url = ''
    if msg_type == 'private':
        url = f"{bpt_ip}/send_private_msg?user_id={send_id}&message=[CQ:image,file={img}]"
    elif msg_type == 'group':
        url = f"{bpt_ip}/send_group_msg?group_id={getQunId(message)}&message=[CQ:at,qq={send_id}] [CQ:image,file={img}]"
    _get(url)


def send_video(message, vedio):
    msg_type = getType(message)
    send_id = getSenderQQ(message)
    bpt_ip = message['bot_ip']
    url = ''
    if msg_type == 'private':
        url = f"{bpt_ip}/send_private_msg?user_id={send_id}&message=[CQ:video,file={vedio}]"
    elif msg_type == 'group':
        url = f"{bpt_ip}/send_group_msg?group_id={getQunId(message)}&message=[CQ:video,file={vedio}]"  # 视频不能@
    _get(url)


if __name__ == '__main__':
    message = {'bot_ip': 'http://127.0.0.1:5910', 'anonymous': None, 'font': 0, 'group_id': 623924247, 'message': '11',
               'message_id': 325128606, 'message_seq': 3939, 'message_type': 'group', 'post_type': 'message',
               'raw_message': '11', 'self_id': 1912144021,
               'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': '傻妞 (查询)', 'role': 'member',
                          'sex': 'unknown', 'title': '', 'user_id': 162204983}, 'sub_type': 'normal',
               'time': 1637993944, 'user_id': 162204983}

    send_txt(message)
