#!/usr/bin/python3 
#coding=utf-8
import time
import accessData.accessConfig as aC; #引入读取配置文件模块

'''
作者：张永涛    
编写时间：2018年10月11日

填写日志模块
输入参数为：日志类型（技术、业务） 、模块名称、日志编码、日志信息
日志类型：技术类用“t”表示、业务类用“b”）
日志编码：10位。函数名+序号。。writeLog01
日志文件为文本文件。每天一个文件。日期戳自动产生。
文件名格式为：Log20180919.txt

调用方法
    wLog.writeLog("t","dmMain.py","test0001","填写日志测试信息")
'''
def writeLog(type,module,logCode,message):
    #生成日志文件名。文件名格式为：Log20180919.txt
    #data/log/log.txt的路径名是测试出来的。不知道为什么会这么写。
    #就此程序而言。相对路径应该是：../../data/log/log20180927.txt
    #读取日志文件的存储位置及名称
    logConfig=aC.getLogSite()
    #组织文件名
    if logConfig.path !="" and logConfig.name!="" :
        fileName=logConfig.path+logConfig.name.replace(".txt", time.strftime("%Y%m%d", time.localtime())+".txt")
        # 打开一个文件。
        with open(fileName, "a",encoding='utf-8') as fo:
            #写入日志
            fo.write(type+"--"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"--"+module+"--"+logCode+"--"+message+"\n");
            # 关闭打开的文件    fo.close()

