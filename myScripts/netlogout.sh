#!/bin/bash
ps | awk -F" " '{print $1}'
ps -ef | awk -F" " '{print $2}'

ps -ef | grep sioan |awk -F" " '{print $2}'


ssh sxr-console kill `ps -ef | grep sioan | grep bash |awk -F" " '{print $2}'`

