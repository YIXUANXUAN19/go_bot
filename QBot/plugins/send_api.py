# coding=utf-8
import json
from QBot.plugins import reply
from QBot.plugins.reply import _get


def api_setu(message):
    url = 'https://www.accy.top/api/1/api.php'
    response = _get(url, timeout=8, max_retries=3)
    reply.send_img(message, response.url)


# P站，需要梯子
def api_setu2(message):
    if '白丝' in message:
        url = 'https://api.lolicon.app/setu/v2?tag=白丝&size1200=true'
    elif '黑丝' in message:
        url = 'https://api.lolicon.app/setu/v2?tag=黑丝&size1200=true'
    elif '萝莉' in message:
        url = 'https://api.lolicon.app/setu/v2?tag=萝莉&size1200=true'
    elif '少女' in message:
        url = 'https://api.lolicon.app/setu/v2?tag=少女&size1200=true'
    else:
        url = 'https://api.lolicon.app/setu/v2?size1200=true'
    response = _get(url, timeout=5, max_retries=3)
    if response.status_code == 200:
        setu_url = json.loads(response.text)['data'][0]['urls']['original']
        reply.send_img(message, setu_url)


def api_xjj(message):
    url = 'http://api.qemao.com/api/pic/?type=ad'
    response = _get(url, timeout=5, max_retries=3)
    reply.send_img(message, response.url)


# 扭一扭
def api_nyn(message):
    url = 'http://api.qemao.com/api/douyin/'
    response = _get(url, timeout=5, max_retries=3)
    reply.send_video(message, response.url)


if __name__ == '__main__':
    fake_msg = {'message_type': 'group', 'user_id': '1912144021', 'message': 'https://item.jd.com/4047591.html',
                'group_id': '623924247'}
    bot_api = 'http://127.0.0.1:5910/'
    # api_nyn(bot_api, message)
    url = 'http://api.qemao.com/api/douyin/'
