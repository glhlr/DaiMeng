#!/usr/bin/python3 
#coding=utf-8
'''
作者：张永涛    
编写时间：2018年9月27日

呆萌系统的主启动程序。
由此模块调用httpServer.py的服务启动程序，
使用系统进入服务等待状态。
'''

import httpServer.httpServer as httpS;  #引入http服务模块
import platform 
import os

def dmMain():
    print("===张永涛的测试启动模块===")
    print("已启动...")
    print("python版本号:"+platform.python_version())
    path1=os.path.abspath('.')   # 表示当前所处的文件夹的绝对路径
    print("dmMain.py绝对路径："+path1)
    httpS.startHttpServer()



if __name__ == '__main__':
    dmMain()


