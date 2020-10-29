#!/bin/sh
ps -ef | grep 9090|grep -v grep |awk '{print $2}'|xargs kill -9
nohup python3 manage.py runserver 10.8.32.127:9090 >output.log 2>&1 &