# coding=utf-8
# 处理消息类型
import logging
from QBot.lib.utils import *
from QBot.lib.DateTimeFormat import getDateTime


# 认证，是否需要处理此消息,从配置文件读取配置的QQ号和QQ群号，过滤不需要监听的
# 需要回复的消息返回True，不需要的返回False
def verifiedMes(data):
    cp = getconf("QBot", "config/config.cfg")
    qqs = getdata(cp, "QQ", "QQNumber")
    qqs = qqs.split("&") if qqs else "all"  # 如果未配置qq，则默认监听所有人
    groups = getdata(cp, 'QQ', 'GroupNumber')
    groups = groups.split("&") if groups else "all"  # 如果未配置群，则默认监听所有群
    flag = False
    debug = getdata(getconf('QBot', "config/config.cfg"), "CORE", "DEBUG")
    if debug in ['TRUE', 'true', 'True']:
        logging.info(f'DEBUG--data_json: {data}')
    # 群消息
    if getType(data) == "group":
        if getQunId(data) in groups or groups == 'all':
            return True
    # 私聊消息
    elif getType(data) == "private":
        if getSenderQQ(data) in qqs or qqs == 'all':
            return True
    # 加好友消息
    elif data.get('post_type') == 'request':
        return True
    return flag


def getType(data):
    # 获取群消息或者私人消息
    return data.get('message_type')


def getMessage(data):
    # 获取收到的消息
    return data.get('message')


def getSenderQQ(data):
    # 获取发送者的QQ号
    return str(data.get('user_id'))


def getQunId(data):
    # 获取群号
    return str(data.get('group_id'))


def getMessageId(data):
    # 信息id，可用来撤回对应信息
    return data.get('message_id')


def getMessageTime(data):
    return getDateTime(data.get('time'))


def getSenderName(data):
    if data.get('sender'):
        return data.get('sender').get('nickname')
