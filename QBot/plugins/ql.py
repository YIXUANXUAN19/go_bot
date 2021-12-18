# -*- coding:utf-8 -*-
import logging
import os
import sys
import time
import traceback
import pymysql
from QBot.lib.DateTimeFormat import getDateTime
from QBot.plugins.send_api import *
from QBot.handle_message.handle import *


# TODO 青龙相关实现，使用socket监听青龙端口， 青龙有新任务就执行相关任务


class UpdateQlToken(object):
    """更新青龙的token等"""

    def excute_sql(self, sql):
        """
        :return: 返回sql执行的结果 类型为二维list 或空list
        """
        db = pymysql.connect(user='ql', host='127.0.0.1', passwd='eEwSCCjfSjYkhNc2', db='ql')
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
            logging.info(f'执行成功：{sql}')
            db.close()
            return list(cursor.fetchall())
        except Exception as e:
            logging.warning(e)
            db.rollback()
            db.close()
            return False

    def update_ck_token(self):
        cp = getconf('QBot', "config/config.cfg")
        for i in range(3):
            # bot_ip = get_bot_ip()
            # url = f'{bot_ip}/open/auth/token?client_id={getdata(cp, "ql", "CLIENT_ID")}&client_secret={getdata(cp, "ql", "CLIENT_SECRET")}'
            response = requests.get(url)
            if response.status_code == 200:
                token = json.loads(response.text)['data']['token']
                now = getDateTime(int(time.time()))
                if self.excute_sql('select ck_token from ql_token where ck_token is not null '):
                    self.excute_sql("update ql_token set ck_token='Bearer %s',create_time='%s'" % (token, now))
                else:
                    self.excute_sql('insert into ql_token(ck_token) values("%s")' % token)
                return token
        return False

    def update_ql_token(self, data_json):
        if not self.update_ck_token():
            data_json['message'] = "更新ql token失败"
            # reply.send_txt(get_bot_ip(), data_json)
        else:
            data_json['message'] = "更新ql token成功"
            # reply.send_txt(get_bot_ip(), data_json)

