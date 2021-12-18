# coding=utf-8
import re
import requests
from QBot.lib.log import BASE_DIR
from QBot.plugins.bi_jia import bi_jia_go
from QBot.plugins.ql import *
from QBot.handle_message.handle import *
from QBot.plugins import reply, send_api

cp = getconf('QBot', "config/config.cfg")


def menu(data_json, menu_list):
    msg = ''
    for index, i in enumerate(menu_list):
        msg += f"{index + 1}、{i}\n"
    data_json['message'] = "\n" + msg.rstrip()
    reply.send_txt(data_json)


def verified(data_json):
    """
    返回re匹配后识别的类型
    :return: type data_json
    """
    message = data_json['message']

    def jd(data):
        # 京东比价规则匹配
        """
        // [rule:raw https://item\.m\.jd\.com/product/(\d+).html]
        // [rule:raw https://.+\.jd\.com/(\d+).html]
        // [rule:raw https://item\.m\.jd\.com/(\d+).html]
        // [rule:raw https://m\.jingxi\.com/item/jxview\?sku=(\d+)]
        // [rule:raw https://m\.jingxi\.com.+sku=(\d+)]
        // [rule:raw https://kpl\.m\.jd\.com/product\?wareId=(\d+)]
        // [rule:raw https://wq\.jd\.com/item/view\?sku=(\d+)]
        // [rule:raw https://wqitem\.jd\.com.+sku=(\d+)]
        // [rule:raw https://.+\.jd\.com.+sku=(\d+)]
        """
        rules = list()
        rules.append(re.compile(r'https://.+\.jd\.com/(\d+).html', re.S))
        rules.append(re.compile(r'https://item\.m\.jd\.com/product/(\d+).html', re.S))
        rules.append(re.compile(r'https://item\.m\.jd\.com/(\d+).html', re.S))
        rules.append(re.compile(r'https://m\.jingxi\.com/item/jxview\?sku=(\d+)', re.S))
        rules.append(re.compile(r'https://m\.jingxi\.com.+sku=(\d+)', re.S))
        rules.append(re.compile(r'https://kpl\.m\.jd\.com/product\?wareId=(\d+)', re.S))
        rules.append(re.compile(r'https://wq\.jd\.com/item/view\?sku=(\d+)', re.S))
        rules.append(re.compile(r'https://wqitem\.jd\.com.+sku=(\d+)', re.S))
        rules.append(re.compile(r'https://.+\.jd\.com.+sku=(\d+)', re.S))
        for rule in rules:
            res = rule.findall(data)
            if res:
                data_json['shop_id'] = res[0]
                return "JDBiJia"

    if 'com.tencent.structmsg' in message:  # 结构化消息
        try:
            message = json.loads(
                re.findall('{.+}', message.replace("&#44", "").replace('; "', ', "').replace(';"', ', "'))[0])
        except Exception as e:
            logging.info(f"ERROR--{data_json}--info: {e}")
            return None
        news = message['meta']['news']
        data_json['JD'] = news if news['tag'] == '京东商城' else ''
        data_json['message'] = news['jumpUrl']
        tag = jd(news['jumpUrl'])
    else:
        tag = jd(message)  # 直接的链接消息
    return tag


# TODO callback函数
def cmd(msg, data_json, admin=False):
    normal_list = ["小姐姐", "色图", "扭一扭", "命令"]  # 普通菜单
    admin_list = ["更新ql token", "重启"]  # 管理员
    if admin:  # 管理员命令
        if msg == '命令':
            normal_list += admin_list
            menu(data_json, normal_list)

        elif msg == '更新ql token':
            ql_up = UpdateQlToken()
            ql_up.update_ql_token(data_json)

        elif msg == '重启':
            reboot(data_json)

        # else:
        #     # 如果不知道消息是什么，就启用复读机模式
        #     reply.send_txt(data_json['bot_ip'], data_json)
    else:
        if msg == '命令':
            menu(data_json, normal_list)

    # 共有的命令
    if msg == '色图':
        send_api.api_setu(data_json)

    elif msg == '小姐姐':
        send_api.api_xjj(data_json)

    elif msg == '扭一扭':
        send_api.api_nyn(data_json)

    # 需要使用re匹配的命令
    types = verified(data_json)
    if types == "JDBiJia":  # 京东比价
        bi_jia_go(data_json)


def reboot(data_json):
    data_json['message'] = "即将重启"
    reply.send_txt(data_json)
    bot_dir = os.path.join(BASE_DIR, 'bot')
    os.chdir(bot_dir)
    for i in range(2):  # 一共尝试两次重启
        # 查看机器人的进程ID  悄悄杀掉
        pids = linuxGetPid("go-bot")
        if 'go-bot' in os.listdir():
            for i in pids:
                os.system(f'kill -9 {i}')
        else:
            logging.warning(f'错误--未找到go-bot文件，请确保go-bot文件在 {os.path.join(bot_dir, "bot/go-bot")} 此位置')
            exit(0)

        # 开启机器人
        logging.info('正在启动机器人')
        start = os.system(f'./go-bot -d faststart')
        logging.info(f"result: {type(start)}--{start}")

        for i in range(10):
            logging.info('等待QQ登录中....')
            data_json['message'] = "正在重启"
            res = reply.send_txt(data_json)
            if res:
                if res.status_code == 200:
                    logging.info('重启成功！')
                    data_json['message'] = "重启成功"
                    reply.send_txt(data_json)
                    return
            else:
                time.sleep(3)
    logging.info('reboot 失败！')


# 机器人的main方法，实现消息回复等
def main_bot(data_json):
    msg_type = getType(data_json)
    if msg_type == 'friend':  # 加好友请求
        add_friends(data_json)
        return

    msg = getMessage(data_json).strip()
    # 发送者的id，可以是群也可以是qq号
    send_id = getQunId(data_json) if getQunId(data_json) != 'None' else getSenderQQ(data_json)

    if msg_type == 'group':
        logging.info(f"收到群 {getQunId(data_json)} 内{getSenderName(data_json)}({getSenderQQ(data_json)}) 的消息: {msg}")
    elif msg_type == 'private':
        logging.info(f"收到好友 {getSenderName(data_json)}({send_id}) 的消息: {msg}")

    if getSenderQQ(data_json) in getdata(cp, "QQ", "MASTER").split("&"):
        cmd(msg, data_json, admin=True)  # 特权命令  admin=True
    else:
        cmd(msg, data_json)


def add_friends(data):
    request_type = data.get('request_type')  # friend
    comment = data.get('comment').strip()  # 验证消息
    request_id = data.get('flag')  # flag，同意加好友用
    user_id = data.get('user_id')  # 发送加好友请求的QQ
    AUTO_ADD_FRIEND = getdata(cp, "QQ", 'AUTO_ADD_FRIEND').strip()
    params = {
        'flag': data.get('flag'),
        'approve': 'true',
        'remark': ''
    }
    if not AUTO_ADD_FRIEND or comment in AUTO_ADD_FRIEND:
        requests.get(data['bot_ip'] + '/set_friend_add_request', params=params)


if __name__ == '__main__':
    from server import get_bot_ip

    # fake_msg = {'bot_ip': get_bot_ip(), 'message_type': 'private', 'user_id': '1912144021',
    #             'message': '[CQ:json,data={"app":"com.tencent.structmsg"&#44;"config":{"autosize":true&#44;"ctime":1639494593&#44;"forward":true&#44;"token":"e62399475a1464c592d20e5bf7a580b1"&#44;"type":"normal"}&#44;"desc":"新闻"&#44;"extra":{"app_type":1&#44;"appid":100273020&#44;"msg_seq":7041575664209099042&#44;"uin":1912144021}&#44;"meta":{"news":{"action":""&#44;"android_pkg_name":""&#44;"app_type":1&#44;"appid":100273020&#44;"ctime":1639494593&#44;"desc":"&#91;来自PLUS会员分享&#93;我在京东发现了一个不错的商品，..."&#44;"jumpUrl":"https://item.m.jd.com/product/100026453590.html?utm_user=plusmember&amp;gx=RnE3kDJYOTfQydRP--tzCXgM_1rbGyW1haAk&amp;ad_od=share&amp;utm_source=androidapp&amp;utm_medium=appshare&amp;utm_campaign=t_335139774&amp;utm_term=QQfriends"&#44;"preview":"https://m.360buyimg.com/mobilecms/s120x120_jfs/t1/200363/40/14101/153913/6170fe34E7a918421/5c3cacebe7c95ce4.jpg!q70.jpg"&#44;"source_icon":""&#44;"source_url":""&#44;"tag":"京东商城"&#44;"title":"森马羽绒服男帅气潮笑脸图案短款加厚外套2021冬季 保..."&#44;"uin":1912144021}}&#44;"prompt":"&#91;分享&#93;森马羽绒服男帅气潮笑脸图案短款加厚外套2021冬季 保..."&#44;"ver":"0.0.0.1"&#44;"view":"news"}]',
    #             'group_id': ''}
    fake_msg = {'bot_ip': get_bot_ip(), 'comment': '我是阿东一号(发送：登陆/查询)', 'flag': '1639799238000000',
                'post_type': 'request',
                'request_type': 'friend',
                'self_id': 162204983, 'time': 1639799238, 'user_id': 428955496}
    add_friends(fake_msg)
