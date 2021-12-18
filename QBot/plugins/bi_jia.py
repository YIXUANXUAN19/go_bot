# coding=utf-8
import json
import re

import requests

from QBot.lib.DateTimeFormat import getDateTime
from QBot.plugins import reply


def send(data_json, res):
    data_json['message'] = ""
    for key, value in res.items():
        key, value = str(key), str(value)
        if not key.strip() or not value.strip(): continue

        if 'tmp' in key:
            key = ''  # 只要值的
            data_json['message'] += key + value + "\n"
        else:
            data_json['message'] += key + '：' + value + "\n"
    reply.send_txt(data_json)


# 比价狗比价
def bi_jia_go(data_json):
    def not_price():
        data_json['message'] = "暂无价格信息"
        reply.send_txt(data_json)
        return

    headers = {
        # 'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    # data_json['shop_id'] = '4047591'
    url = f'https://browser.bijiago.com/extension/price_towards?dp_ids=undefined&dp_id={data_json["shop_id"]}-3&ver=1&format=jsonp&union=union_bijiago&version=1637807968087&from_device=bijiago&from_type=bjg_ser&crc64=1'
    data = requests.get(url, headers=headers)
    data = json.loads(data.text)
    if not data.get('store'):
        not_price()
        return
    history_price = data['store'][0]
    current_price = history_price.get('current_price')
    if not current_price:
        not_price()
        return

    price_range = history_price['price_range'].split("-")
    max_price = history_price.get('highest')  # 最高价
    min_price = history_price.get('lowest')  # 最低价

    max_price = price_range[1] if price_range else max_price
    min_price = price_range[0] if price_range else min_price.split("<sc")[0]
    lowest_date = getDateTime(history_price.get('lowest_date', ''))

    analysis = data['analysis']
    tip = analysis['tip']
    promo_days = analysis['promo_days']

    title = requests.get(data_json['message'], headers=headers)
    title = re.findall("<title>(.*?)</title>", title.text)
    title = title[0].split('【')[0].strip() if title else ''
    result = dict()
    result['商品名称'] = title.strip('"') + "\n"
    result['最高价'] = max_price
    result['最低价'] = f"{min_price} ({lowest_date.split()[0]})"

    for i in promo_days:
        result[i['show']] = i['price']
    result['tmp2'] = "\n(比价结果仅供参考)"
    result['当前价'] = current_price
    result['tmp1'] = f"({tip})"  # 只要值的，key为tmp+num

    send(data_json, result)


"""
# 慢慢买比价，需要 driver，js接口需要认证参数，js混淆加密 app: "https://home.manmanbuy.com/app.aspx?type=history&value=tool_trend"
"""
# def man_man_mai():
#     from selenium import webdriver
#     from selenium.webdriver.common.keys import Keys
#     def save_cookies(cookies):
#         while True:
#             if not cookies: continue
#             with open("tmp.json", "w") as f:
#                 for ck in cookies:
#                     if ck['value']:
#                         cookie = json.dumps(ck) + "\n"
#                         f.write(cookie)
#                         f.flush()
#             f.close()
#             return
#
#     def add_cookies():
#         driver.get('https://tool.manmanbuy.com/ValidateAlibaba.aspx')
#         f = open("tmp.json", "r")
#         if not f:
#             not_cookie = True
#             return not_cookie
#         else:
#             for i in f.readlines():
#                 cookie = json.loads(i.strip())
#                 driver.add_cookie(cookie)
#
#     options = webdriver.ChromeOptions()
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_experimental_option('excludeSwitches', ['enable-automation'])
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     # options.headless = False
#     options.headless = False
#
#     driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
#     add_cookies()
#     driver.get('https://tool.manmanbuy.com/ValidateAlibaba.aspx')
#     driver.find_element_by_id("rectMask").click()
#     driver.find_element_by_id("historykey").send_keys('https://item.jd.com/4047591.html')
#     driver.find_element_by_id("searchHistory").click()
#     driver.find_element_by_xpath("//span[@id='PriorLowerPrice']/a").click()  # 详细信息
#     driver.switch_to.frame("layui-layer-iframe3")
#     data = driver.page_source
#     save_cookies(driver.get_cookies())
#     add_cookies()
#     driver.find_element_by_id("historykey").send_keys(Keys.CONTROL, "A")
#     driver.find_element_by_id("historykey").send_keys(Keys.DELETE)
#     driver.get('https://tool.manmanbuy.com/ValidateAlibaba.aspx?url=https://item.jd.com/1070843.html')
#     """
#     <body style="margin: 0px; padding: 0px;">
#     <div style="margin: 20px;" class="historyDetail">
#         <div style="margin:10px 0px; font-weight:bold; font-size:16px;">价格走势分析结果</div>
#         <div style=" line-height:20px;">商品收录时间：2019-11-8，当前价格：59元，近期价格平稳</div>
#         <div style=" line-height:20px; margin-top:10px; width:380px;">
#             <div class="divtablesm" style="height:30px;">&nbsp;</div>
#             <div class="divtableprice" style="font-size:14px; padding-top:5px; height:30px;">价格</div>
#             <div class="divtablethan" style="font-size:14px; padding-top:5px;height:30px;">涨跌</div>
#             <div class="divtablesm">当前价</div>
#             <div class="divtableprice">¥59</div>
#             <div class="divtablethan">-</div>
#             <div class="clear"></div>
#             <div class="divtablesm">历史最低价</div>
#             <div class="divtableprice">¥15<br><span class="distime">2020-12-25</span></div>
#             <div class="divtablethan priceGoUp">↑44</div>
#             <div class="clear"></div>
#             <div class="divtablesm">双11价格</div>
#             <div class="divtableprice">¥39.9<br><span class="distime"></span></div>
#             <div class="divtablethan priceGoUp">↑19</div>
#             <div class="clear"></div>
#             <div class="divtablesm">618价格</div>
#             <div class="divtableprice">¥53.1<br><span class="distime"></span></div>
#             <div class="divtablethan priceGoUp">↑6</div>
#             <div class="clear"></div>
#             <div class="divtablesm">30天最低价</div>
#             <div class="divtableprice">¥39.9<br><span class="distime">2021-11-10</span></div>
#             <div class="divtablethan priceGoUp">↑19</div>
#             <div class="clear"></div>
#             <div class="divtablesm">30天平均价</div>
#             <div class="divtableprice">¥58<br><span class="distime"></span></div>
#             <div class="divtablethan priceGoUp">↑1</div>
#             <div class="clear"></div>
#         </div>
#         <div></div>
#     </div>
#     """
#     'https://item.jd.com/4047591.html'


if __name__ == '__main__':
    data_json = {'message_type': 'group', 'user_id': '1912144021', 'message': 'https://item.jd.com/4047591.html',
                 'group_id': '623924247', 'bot_ip': 'http://127.0.0.1:5910/'}
    bi_jia_go(data_json)
