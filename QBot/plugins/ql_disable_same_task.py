import json
import logging
import time
import traceback
import os
import sys
import requests

from QBot.plugins import reply

ip = "localhost"
sub_str = os.getenv("RES_SUB", "Aaron-lv_sync")
sub_list = sub_str.split("&")
res_only = os.getenv("RES_ONLY", True)
headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
}


def send():
    reply.send_txt()


# def load_send() -> None:
# logging.info("加载推送功能中...")
# global send
# send = None
# cur_path = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(cur_path)
# if os.path.exists(cur_path + "/notify.py"):
#     try:
#         from notify import send
#     except Exception:
#         send = None
#         logging.info(f"❌加载通知服务失败!!!\n{traceback.format_exc()}")


def get_tasklist() -> list:
    tasklist = []
    t = round(time.time() * 1000)
    url = f"http://{ip}:5700/api/crons?searchValue=&t={t}"
    response = requests.get(url=url, headers=headers)
    datas = json.loads(response.content.decode("utf-8"))
    if datas.get("code") == 200:
        tasklist = datas.get("data")
    return tasklist


def filter_res_sub(tasklist: list) -> tuple:
    filter_list = []
    res_list = []
    for task in tasklist:
        for sub in sub_list:
            if task.get("command").find(sub) == -1:
                flag = False
            else:
                flag = True
                break
        if flag:
            res_list.append(task)
        else:
            filter_list.append(task)
    return filter_list, res_list


def get_index(lst: list, item: str) -> list:
    return [index for (index, value) in enumerate(lst) if value == item]


def get_duplicate_list(tasklist: list) -> tuple:
    logging.info("\n=== 第一轮初筛开始 ===")

    ids = []
    names = []
    cmds = []
    for task in tasklist:
        ids.append(task.get("_id"))
        names.append(task.get("name"))
        cmds.append(task.get("command"))

    name_list = []
    for i, name in enumerate(names):
        if name not in name_list:
            name_list.append(name)

    tem_tasks = []
    tem_ids = []
    dup_ids = []
    for name2 in name_list:
        name_index = get_index(names, name2)
        for i in range(len(name_index)):
            if i == 0:
                logging.info(f"【✅保留】{cmds[name_index[0]]}")
                tem_tasks.append(tasklist[name_index[0]])
                tem_ids.append(ids[name_index[0]])
            else:
                logging.info(f"【🚫禁用】{cmds[name_index[i]]}")
                dup_ids.append(ids[name_index[i]])
        logging.info("")

    logging.info("=== 第一轮初筛结束 ===")

    return tem_ids, tem_tasks, dup_ids


def reserve_task_only(tem_ids: list, tem_tasks: list, dup_ids: list, res_list: list) -> list:
    if len(tem_ids) == 0:
        return tem_ids

    logging.info("\n=== 最终筛选开始 ===")
    task3 = None
    for task1 in tem_tasks:
        for task2 in res_list:
            if task1.get("name") == task2.get("name"):
                dup_ids.append(task1.get("_id"))
                logging.info(f"【✅保留】{task2.get('command')}")
                task3 = task1
        if task3:
            logging.info(f"【🚫禁用】{task3.get('command')}\n")
            task3 = None
    logging.info("=== 最终筛选结束 ===")
    return dup_ids


def disable_duplicate_tasks(ids: list) -> None:
    t = round(time.time() * 1000)
    url = f"http://{ip}:5700/api/crons/disable?t={t}"
    data = json.dumps(ids)
    headers["Content-Type"] = "application/json;charset=UTF-8"
    response = requests.put(url=url, headers=headers, data=data)
    datas = json.loads(response.content.decode("utf-8"))
    if datas.get("code") != 200:
        logging.info(f"❌出错!!!错误信息为：{datas}")
    else:
        logging.info("🎉成功禁用重复任务~")


def disable_same_task(bot_api, data_json):
    logging.info("===> 禁用重复任务开始 <===")
    # load_send()
    headers["Authorization"] = f"Bearer {token}"

    # 获取过滤后的任务列表
    sub_str = "\n".join(sub_list)
    logging.info(f"\n=== 你选择过滤的任务前缀为 ===\n{sub_str}")
    tasklist = get_tasklist()
    if len(tasklist) == 0:
        logging.info("❌无法获取 tasklist!!!")
        exit(1)
    filter_list, res_list = filter_res_sub(tasklist)

    tem_ids, tem_tasks, dup_ids = get_duplicate_list(filter_list)
    # 是否在重复任务中只保留设置的前缀
    if res_only:
        ids = reserve_task_only(tem_ids, tem_tasks, dup_ids, res_list)
    else:
        ids = dup_ids
        logging.info("你选择保留除了设置的前缀以外的其他任务")

    sum = f"所有任务数量为：{len(tasklist)}"
    filter = f"过滤的任务数量为：{len(res_list)}"
    disable = f"禁用的任务数量为：{len(ids)}"
    logging.info("\n=== 禁用数量统计 ===\n" + sum + "\n" + filter + "\n" + disable)

    if len(ids) == 0:
        logging.info("😁没有重复任务~")
    else:
        disable_duplicate_tasks(ids)
    # if send:
    #     send("💖禁用重复任务成功", f"\n{sum}\n{filter}\n{disable}")


if __name__ == "__main__":
    from test import bot_api, data_json

    disable_same_task(bot_api, data_json)
