#!/usr/bin/python3 
#coding=utf-8
'''
张永涛的测试启动模块
'''
import accessData.writeLog as wLog; #引入填写日志模块
import accessData.accessConfig as aC;
import accessData.accessDB as aDB

import business.ltp_in as bLin
#from business.ltp_in import * 
import business.ltp_in as bLin

import xml.etree.cElementTree as ET
#import requests
from urllib import request
import json
import urllib
#import business.LTPana as bL

import business.trans_ltp_ZYT as trLtp
import httpServer.httpServer as httpS;  #引入http服务模块
import platform 
#import business.sentenceMatch3 as sM3
import numpy as np
import time

#去除警告
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
#import gensim
import pandas as pd

def zytMain():
    print("===张永涛的测试启动模块===")
    print("已启动...")
    print("python版本号:"+platform.python_version())
    httpS.startHttpServer()

    #bLin.in_.mainloop()
    #testTrans_ltp1()
    #accessDBtest()
    #testWord2Vec()
    #npyToText()
    #wos=["人","狗","在"]
    #trLtp.newCla_search (wos)
    #testInfo


    #bL.fenCiJson("===张永涛的测试启动模块===")

    '''
    print(bL.fenCiJson("关于中国海军世界排名第二的言论流传已久，那么中国海军真的能凭借建造第二艘国产航母"))   
    logConfig=aC.getBiaoDaConfig()
    print(logConfig.path)
    print(logConfig.name)


    yyyConfig=aC.getYuYanYunConfig()
    print(yyyConfig.Url)
    print(yyyConfig.api_key)



    logConfig=aC.getConString()
    print(logConfig.connectionString)
    print(logConfig.providerName)
    '''
    #xml_ET_test()
    #httpS.startServer()
    ##写日志测试
    #wLog.writeLog("t","dmMain.py","test0001","填写日志测试信息")
    #aC.lxml_parser_iter()
    #aC.xml_parser()

'''
npy文件格式的读取

'''

def npyToText():
    test=np.load('D:/MY\python/词向量/数据/wiki.zh.text.model.syn0.npy',encoding = "latin1")  #加载文件
    doc = open('D:/MY\python/词向量/数据/wiki.zh.text.model.syn0.txt', 'a')  #打开一个存储文件，并依次写入
    print(test, file=doc)  #将打印内容写入文件中

def testWord2Vec():
    time1=time.time()
    print(time.localtime(time1 ))
    #微信数据训练数据。。计算时间10秒
    #model = gensim.models.Word2Vec.load('D:/MY/python/词向量/word2vec_from_weixin/word2vec_wx')
    #维精百科训练数据。。计算时间64秒
    #model = gensim.models.Word2Vec.load('D:/MY/python/词向量/word2vec_from_wiki/wiki.zh.text.model')
    #Word60练数据。。计算时间6秒
    model = gensim.models.Word2Vec.load('D:/MY/python/词向量/word2vec_from_Word60/Word60.model')

    
    word2Vec=model.most_similar(u'你好')
    #print(str(word2Vec))
    pds=pd.Series(word2Vec)
    print(pds)
    time2=time.time()
    print(time.localtime(time2))
    print(time2-time1)
    '''
    输出结果
    0 (QQ, 0.752506196499)
    1 (订阅号, 0.714340209961)
    2 (QQ号, 0.695577561855)
    3 (扫一扫, 0.695488214493)
    4 (微信公众号, 0.694692015648)
    5 (私聊, 0.681655049324)
    6 (微信公众平台, 0.674170553684)
    7 (私信, 0.65382117033)
    8 (微信平台, 0.65175652504)
    9 (官方, 0.643620729446)

    '''
    '''
    gensim源程序修改说明
    matutils.py的737行做如下修改。
    if np.issubdtype(vec.dtype, np.int):改为if np.issubdtype(vec.dtype, np.int32):

    '''

                
            




'''
调用Trans_ltp函数
显示逻辑句式等信息

'''
def testTrans_ltp1():
    phsen_ana=trLtp.trans_ltp("春天来了")
    #print(phsen_ana)
    print(str(len(phsen_ana)) +'句')

    i = 0    
    for sen in phsen_ana:
        sen_result = sM3.sentence_match_result(sen.w_anas)
        #exp_result = experience_mean_result(sen)
        print("开始输出-----------------")
        #print(sen_result)
        dsent_list = []
        lsent_list =[]
        while(sen_result):
            dsent_list.append(sen_result.pop(0))
            lsent_list.append(sen_result.pop(0))
            phsen_ana[i].l_form = lsent_list
            phsen_ana[i].d_form = dsent_list
            #phsen_ana[i].exp_mean = exp_result
            i += 1

        print('111:'+sen.sen_mean + '\n')
        print('222:'+str(lsent_list) + '\n')
        print('333:'+str(dsent_list) + '\n')

        disp_wo = ''
        for w in sen.w_anas:
            disp_wo +=(w.wo + '  ' +w.pos + '::' + w.syn + ' :: ' + w.cla + '\n')
        print('444:'+disp_wo)



def testTrans_ltp():
    phsen_ana=trLtp.trans_ltp("习近平在上海工作期间亲自审定了大厦的设计方案")
    print(phsen_ana)
    print(str(len(phsen_ana)) +'句')
    for sen in phsen_ana:
        '''
        self.sen_in = sen_in # 句子原文
        self.sen_mean = sen_mean # 本句逻辑语义，单句语义元素的集合主谓宾等
        self.env_mean = env_mean # 环境逻辑语义，标明本句和其它句子关系，如因果条件递进转折、疑问、回答、
        self.exp_mean = exp_mean # 经验逻辑语义，单句或多句推导出来的言外之意
        self.w_anas = w_anas # 单词分析列表组成句子
        self.l_form = l_form # 本句match获得的逻辑语句
        self.d_form = d_form # 本句match过来的描述句式
        '''
        print("句子原文："+sen.sen_in)
        print("逻辑语义："+sen.env_mean)
        print("环境逻辑语义："+sen.env_mean)
        print("经验逻辑语义："+sen.exp_mean)
        print("逻辑语句："+sen.l_form)
        print("描述句式："+sen.d_form)

        '''
        self.wo = wo # 单词
        self.pos = pos # 词性
        self.wgr = wgr # 词组分析输出
        self.wgr_ty = wgr_ty # 词组类型
        self.cla = cla # 分类
        self.syn = syn # 同义词
        self.sp_cla = sp_cla # 单字语义
        '''
        for w_ana in sen.w_anas:
            print("单词："+w_ana.wo)
            print("词性："+w_ana.pos)
            print("词组分析输出："+w_ana.wgr)
            print("词组类型："+w_ana.wgr_ty)
            print("分类："+w_ana.cla)
            print("同义词："+w_ana.syn)
            print("单字语义："+w_ana.sp_cla)

def accessDBtest():
    helper = aDB.msSqlHelper()
    sql = "SELECT BianMa,XuHao,LeiBie,CiZu  FROM dbo.CiLin WHERE BianMa=%s AND XuHao=%s"
    params = ('Be04A','06')
    row =helper.GetOne(sql,params)
    #
    for cols in row:
        print(cols)
    print (row)

    sql = "SELECT BianMa,XuHao,LeiBie,CiZu  FROM dbo.CiLin WHERE BianMa=%s AND XuHao=%s"
    params = ('Be04A','06')
    rows =helper.GetAll(sql,params)
    for row in rows:
        print(row[0], row[1], row[2], row[3])


def xml_ET_test():
    fileName="code/Config.xml"
    root = ET.parse(fileName)
    #/con[@key='YuYanYun']
    configs=root.find("./YuYanYun/con[@key='YuYanYun']")
    print( configs.attrib['Url'])
    for configs_list in configs:
        for config in configs_list:
            print("测试")
            print ("="*20)
            #if config.attrib['key']=="YuYanYun":
            print( config.attrib['Url'])
            print ("="*20)


    
#ElementTree.iterparse方式学习

def lxml_parser_iter():

    print("ElementTree.iterparse方式学习测试")
    fileName="code/Config.xml"
    i = 0
    attribs = {}
    #用ElementTree.iterparse方法遍历XML文件。相应事件为'start','end'。
    for event, elem in ET.iterparse(fileName,events=('start','end')):
        #如果事件为start
        if event == 'start':
            #判断元素标签是否为con
            if elem.tag == 'YuYanYun/con':
                #获取此标签的属性
                attribs=elem.attrib
                if attribs['key']=="YuYanYun":
                    print(attribs['Url'])



def xml_parser():
    fileName="code/Config.xml"
    root = ET.parse(fileName)
    configs=root.findall("./YuYanYun")
    #print(configs)
    for configs_list in configs:
        for config in configs_list:
            print ("="*20)
            #if config.attrib['key']=="YuYanYun":
            print( config.attrib['Url'])
            print ("="*20)

if __name__ == '__main__':
    zytMain()


