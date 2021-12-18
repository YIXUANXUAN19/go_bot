import datetime
import re
import time
import logging
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import timezone

date_dict = {'刚刚': 0, '今天': 0, '今日': 0, '昨天': 1, '昨日': 1, '前天': 2, '前日': 2}
replace_dict = {'年': '-', '月': '-', '日': ' ', '时': ':', '点': ':', '分': ':', '秒': ' ', '.': '-', '上午': ' ',
                '下午': ' '}
date_before_dict = {'年': relativedelta(years=1), '月': relativedelta(months=1), '个月': relativedelta(months=1),
                    '周': datetime.timedelta(days=7), '星期': datetime.timedelta(days=7), '天': datetime.timedelta(days=1),
                    '日': datetime.timedelta(days=1), '时': datetime.timedelta(hours=1),
                    '小时': datetime.timedelta(hours=1),
                    '分': datetime.timedelta(minutes=1), '分钟': datetime.timedelta(minutes=1),
                    '秒': datetime.timedelta(seconds=1), '秒钟': datetime.timedelta(seconds=1)}


def getDateTime(date_time):
    if isinstance(date_time, str):
        date_time = date_time.strip()
        date_time = date_time.strip('(').strip(')')
        if '前' in date_time or '月' in date_time or '内' in date_time:
            date_time = re.sub('\s+', '', date_time)
    else:
        date_time = str(date_time)
    try:
        ret = getDateTime_1(date_time)
    except Exception as e:
        ret = ''
        # logging.info(f'时间转换错误----{date_time}--{e}')
    return ret


def getDateTime_1(date_time):
    '''
    :param date_time: 传入的时间参数，必须是字符串
    :return: 字典 {'timestamp': int类型时间戳, 'datetime': str类型的最终的时间格式（%Y-%m-%d %H:%M:%S）}
    '''
    if not isinstance(date_time, str):
        date_time = str(date_time)

    # try:
    if date_time.isdigit() and len(date_time) >= 10:
        if len(date_time) == 10:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(date_time)))
        elif len(date_time) == 13:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(date_time) / 1000))
        else:
            return ''

    if date_time == '':
        return ''

    # 小时结尾后面要加上一个数字
    if date_time[-1] == '点' or date_time[-1] == '时':
        date_time += '0'

    # 判断为24小时制还是12小时制
    ths = '24'
    if '下午' in date_time:
        ths = '12'

    # 处理时间爱你格式20/0903
    if date_time.count('/') == 1 and len(date_time) == 7:
        date_time = date_time.replace('/', '')

    # **时间单位前
    if date_time[-1] == '前' or date_time[-2:] == '之前':
        d_date_time = DateTimebefore(date_time).strftime("%Y-%m-%d %H:%M:%S")
        return d_date_time

    # 前天、今天、昨天类型的时间处理
    for key, value in date_dict.items():
        timestamp = time.time()
        oneday = datetime.timedelta(days=1)
        # 只有前、昨、今天
        if date_time == key:
            nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            d_date_time = (datetimeConversion(nowtime, ths) - oneday * value).strftime("%Y-%m-%d %H:%M:%S")
            return d_date_time

        # 后面加了时间的
        if key in date_time and len(date_time) > len(key):
            nowtime = time.strftime("%Y-%m-%d", time.localtime(timestamp))
            d_date_time = (datetimeConversion(nowtime) - oneday * value).strftime("%Y-%m-%d")

            date_time = re.sub(key, d_date_time + ' ', date_time)

            d_date_time = datetimeConversion(date_time, ths).strftime("%Y-%m-%d %H:%M:%S")
            return d_date_time

    d_date_time = datetimeConversion(date_time, ths).strftime("%Y-%m-%d %H:%M:%S")
    # except Exception as e:
    #     # logging.info(f'-时间解析出错--{date_time}-{repr(e)}')
    #     print(f'-时间解析出错--{date_time}-{repr(e)}')
    #     return ''
    return d_date_time


# 日期**时间单位之前转成datetime类型
def DateTimebefore(date_time):
    '''
    :param date_time: str类型时间
    :return: 返回datetime类型的最终时间
    '''
    date_time = date_time.replace('前', '').replace('之', '')
    nowtime = datetime.datetime.today()
    # 分离时间和单位
    num = ''
    for i in date_time:
        if i.isdigit():
            num += i
        else:
            break
    unit = date_time.split(num)[-1]
    # print('num:', num, ', unit:', unit)
    # 生成最终时间
    d_date_time = nowtime - date_before_dict[unit] * int(num)
    return d_date_time


# 生成日期格式
def datetimeConversion(date_time, ths='24'):
    '''
    :param date_time: 字符串类型的时间
    :param ths: 参数只能是24或12，代表24小时制或12小时制，默认为24
    :return: 返回datetime类型的时间格式 %Y-%m-%d %H:%M:%S
    '''
    s = ''
    rela = 0
    if ':00' in date_time:
        s += '0'
    date_time = re.sub(r'\s+|星期.?', ' ', date_time)

    for key, value in replace_dict.items():
        date_time = date_time.replace(key, value)
    if date_time[-1] == ':':
        date_time = date_time[:-1]

    if '/' in date_time or '.' in date_time or '-' in date_time:
        if len(date_time.split(re.search('[/|\.|-]', date_time).group(0))) < 3:
            rela = 1
    # 转日期格式
    date_time = parse(parse(date_time, yearfirst=True).strftime("%Y-%m-%d %H:%M:%S"), yearfirst=True)

    # 12小时制转24小时制
    if ths == '12':
        date_time += datetime.timedelta(hours=12)
    # 日期大于当前日期时，年份-1
    if rela == 1:
        if date_time > datetime.datetime.today():
            date_time -= relativedelta(years=1)
    # 只有日期没有时间，添加时间
    if (date_time.hour == 0 or date_time.hour == 12) and date_time.minute == 0 and date_time.second == 0 and s == '':
        date_time = datetime.datetime(year=date_time.year, month=date_time.month, day=date_time.day,
                                      hour=datetime.datetime.today().hour, minute=datetime.datetime.today().minute,
                                      second=datetime.datetime.today().second)
    return date_time


# 日期转时间戳
def timestampConversion(date_time):
    '''
    时间（str类型）转时间戳
    :param date_time: 输入的时间
    :return: 返回str类型的时间戳
    '''
    d_date_time = getDateTime(date_time)
    if d_date_time == '':
        return ''
    return int(time.mktime(time.strptime(d_date_time, "%Y-%m-%d %H:%M:%S")))


# print(getDateTime('2021-05-23 09:45:05'))
# print(timestampConversion('2021-05-23 09:45:05'))

if __name__ == '__main__':
    pass
