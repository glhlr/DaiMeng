#!/usr/bin/python3 
#coding=utf-8
#import time
import xml.etree.cElementTree as ET
'''
此模块的功能是读取配置文件的信息，为上层模块提供数据。 
'''

'''
作者：张永涛    
开始时间：2018年10月16日
最后时间：2018年10月16日
'''

'''
读取Access文件目录及名称类。
把读取方法及属性封装成类
解析Config.xml文件
找到Access/AccessFile标签，读取属性
调用方法：
    accConfig=aC.getAccessConfig(key="DaiMeng")
    print(accConfig.path)
    print(accConfig.name)
    print(accConfig.pathName)

'''

class getAccessConfig:
    def __init__(self,key):
        #解析XML
        root = xmlETparse()
        #判断解析XML是否成功
        if root==None:
            self.path=""
            self.name=""
            self.pathName=""
            return
        #查找xmlDataSite/xmlFile标签
        config=root.find("./Access/AccessFile[@key='"+key+"']")
        #把标签属性赋值给类属性
        if config==None :
            self.path=""
            self.name=""
            self.pathName=""
        else:
            self.path=config.attrib['path']
            self.name=config.attrib['name']
            self.pathName=config.attrib['path']+config.attrib['name']

'''
读取XML文件目录及名称类。
把读取方法及属性封装成类
解析Config.xml文件
找到xmlDataSite/xmlFile标签，读取属性
调用方法：
    xmlConfig=aC.getXmlConfig(key="表达2")
    print(xmlConfig.path)
    print(xmlConfig.name)
    print(xmlConfig.pathName)

'''

class getXmlConfig:
    def __init__(self,key):
        #解析XML
        root = xmlETparse()
        #判断解析XML是否成功
        if root==None:
            self.path=""
            self.name=""
            self.pathName=""
            return
        #查找xmlDataSite/xmlFile标签
        config=root.find("./xmlDataSite/xmlFile[@key='"+key+"']")
        #把标签属性赋值给类属性
        if config==None :
            self.path=""
            self.name=""
            self.pathName=""
        else:
            self.path=config.attrib['path']
            self.name=config.attrib['name']
            self.pathName=config.attrib['path']+config.attrib['name']






'''

读取http服务的配置信息
把读取方法及属性封装成类
解析Config.xml文件
找到HttpServer/add标签，读取属性
调用方法：
    httpConfig=aC.getHttpServerConfig()
    print(httpConfig.ip)
    print(httpConfig.port)

'''
class getHttpServerConfig:
    def __init__(self):
        #解析XML
        root = xmlETparse()
        #判断解析XML是否成功
        if root==None:
            self.ip=""
            self.port=-1
            return
        #查找YuYanYun/con标签
        config=root.find("./HttpServer/add[@key='localHttp']")
        #把标签属性赋值给类属性
        if config==None :
            self.ip=""
            self.port=-1
        else:
            self.ip=config.attrib['ip']
            self.port=int(config.attrib['port'])

'''
作者：张永涛    
编写时间：2018年10月16日
读取数据库连接配置
把读取方法及属性封装成类
解析Config.xml文件
找到connectionStrings/add标签，读取属性
调用方法：
    connConfig=aC.getConnConf()
    print(conn.server)
    print(conn.user)
'''
class getConnConf:
    def __init__(self):
        #解析XML
        root =xmlETparse() 
        #判断解析XML是否成功
        #server="10.65.28.23" user="sa" password="123asd" database="DaiMeng" #
        if root==None:
            self.server=""
            self.user=""
            self.password=""
            self.database=""
            return
        #查找YuYanYun/con标签
        config=root.find("./ConnectionDB/add[@name='ConnDM']")
        #把标签属性赋值给类属性
        if config==None :
            self.server=""
            self.user=""
            self.password=""
            self.database=""
        else:
            self.server=config.attrib['server']
            self.user=config.attrib['user']
            self.password=config.attrib['password']
            self.database=config.attrib['database']



'''
作者：张永涛    
编写时间：2018年10月16日
读取LtpServer的配置信息
把读取方法及属性封装成类
解析Config.xml文件
找到YuYanYun/con标签，读取属性
调用方法：
    yyyConfig=aC.getLtpServerConfig()
    print(yyyConfig.Url)
    print(yyyConfig.api_key)

'''
class getLtpServerConfig:
    def __init__(self):
        #解析XML
        root =xmlETparse() 
        #判断解析XML是否成功
        if root==None:
            self.Url=""
            self.api_key=""
            return
        #查找YuYanYun/con标签
        config=root.find("./YuYanYun/con[@key='ltp_server']")
        #把标签属性赋值给类属性
        if config==None :
            self.Url=""
            self.api_key=""
        else:
            self.Url=config.attrib['Url']
            self.api_key=config.attrib['api_key']



'''
作者：张永涛    
编写时间：2018年10月16日

读取语言云的配置信息
把读取方法及属性封装成类
解析Config.xml文件
找到YuYanYun/con标签，读取属性
调用方法：
    yyyConfig=aC.getYuYanYunConfig()
    print(yyyConfig.Url)
    print(yyyConfig.api_key)

'''
class getYuYanYunConfig:
    def __init__(self):
        #解析XML
        root =xmlETparse() 
        #判断解析XML是否成功
        if root==None:
            self.Url=""
            self.api_key=""
            return
        #查找YuYanYun/con标签
        config=root.find("./YuYanYun/con[@key='YuYanYun']")
        #把标签属性赋值给类属性
        if config==None :
            self.Url=""
            self.api_key=""
        else:
            self.Url=config.attrib['Url']
            self.api_key=config.attrib['api_key']


'''
作者：张永涛    
编写时间：2018年10月16日

读取日志文件的存储目录及文件名
把读取方法及属性封装成类
解析Config.xml文件
找到logSite/logFile标签，读取属性
调用方法：
    logConfig=aC.getLogSite()
    print(logConfig.path)
    print(logConfig.name)

'''
class getLogSite:
    def __init__(self):
        #解析XML
        root = xmlETparse()
        #判断解析XML是否成功
        if root==None:
            self.path=""
            self.name=""
            return
        #查找YuYanYun/con标签
        config=root.find("./logSite/logFile[@key='allLog']")
        #把标签属性赋值给类属性
        if config==None :
            self.path=""
            self.name=""
        else:
            self.path=config.attrib['path']
            self.name=config.attrib['name']


'''
作者：张永涛    
编写时间：2018年10月16日

获取XML解析对象
如果解析失败或文件错误，返回None
'''
def xmlETparse():
    #配置文件名称
    configFileName="Config.xml"
    # ET.parse解析文件返回结果
    tree=None
    try:
        tree= ET.parse(configFileName)
    except OSError as err:
        tree=None
        print("OS error: {0}".format(err))
    return tree

  






