#!/usr/bin/env bash
# cd D:\my_file\go-cqhttp\QBot
name="server.py"
pid=$(ps -aux | grep "$name" | awk '{print$2}')
# echo $pid

for i in $pid ; do
  kill -9 "$i" &>/dev/null
done
sleep 3
nohup python3 "$name" > /dev/null 2>&1 &

# pid=$(ps -aux | grep "$name" | awk '{print$2}')
# echo $pid

# for i in $pid ; do
#   echo "$i" >'.reboot_cache'
#   break
# done
