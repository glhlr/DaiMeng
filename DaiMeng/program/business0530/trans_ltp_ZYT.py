#!/usr/bin/python3 
#coding=utf-8
'''

改编：张永涛    
编写时间：2018年11月7日
小部份改进

模块说明



'''
#import business.LTPana as ltpana


import re
import xml.etree.cElementTree as ET
import urllib
#import requests
from urllib import request
import time
import json
#import synonyms as SY
from business.structure import w_ana,sen_ana
from business.structure import PosTag   #这两条上服务器要加'daimeng.'
#import gensim
#from gensim.models import word2vec
#import business.sentenceMatch3
#from business.sentenceMatch3 import *
import accessData.accessDB as aDB

import platform, os 

Yufa_dic = {'ADV':'状语','SBV':'主语','VOB':'宾语','ATT':'定语','COO':'并列','COV':'CV','RAD':'后附加','CMP':'动补','POB':'介宾','DBL':'C宾语','WP':'标点','FOB':'宾语前置'}   #YYY语法依存-自知者逻辑标签转换，这里的COO仅仅限于对HED，即并列谓语
input_a = ''

#全局变量

env_ws = [ [],[],[] ]  #环境词汇列表，不重复，分1、2、3字以上
envw_ana = [ [],[],[] ]   #环境词汇数据分析，重复的不用再搜,再按1、2、3字以上分类，元素结构是structure.w_ana
This_sen = ''

global phsen_ana  #各函数公用的句子分析表（列车），成员必须确保sen_ana对象，装载语言云输出的句子分析数据（含词语分析对象列表），另外词语信息中做了词林分类。
phsen_ana =[]
def set_phsen( ph = []):
    # 告诉编译器我在这个方法中使用的a是刚才定义的全局变量a,而不是方法内部的局部变量.
    global phsen_ana
    phsen_ana = ph

def get_phsen():
    # 同样告诉编译器我在这个方法中使用的a是刚才定义的全局变量a,并返回全局变量a,而不是方法内部的局部变量.
    global phsen_ana 
    return phsen_ana


'''
作者：张永涛    
编写时间：2018年11月5日

函数说明
本模块内的调用函数。增加容错。调用过程限制在本模块内
参数：输入的问话文本
'''



def trans_ltp(queryText):
    #返回的结果
    resule="测试结果"
    fenCiJson={}
    fenCiJson=ltpana.fenCiJson(queryText)
    trans_json (fenCiJson)
    phsen_ana = get_phsen()
    #resule=str(fenCiJson)
    return phsen_ana

'''

对分词结构进行分析
输入参数：json结构。对一个段落的分词结构

[[[

{'arg': [], 'cont': '中华人民共和国', 'id': 0, 'ne': 'S-Ns', 'parent': -1, 'pos': 'ns', 'relate': 'HED'}, 

{'arg': [], 'cont': '，', 'id': 1, 'ne': 'O', 'parent': 0, 'pos': 'wp', 'relate': 'WP'}, 

{'arg': [], 'cont': '中华人民共和国', 'id': 2, 'ne': 'S-Ns', 'parent': 0, 'pos': 'ns', 'relate': 'COO'}

]]]


'''
def trans_json (json_ltp = []):
    #定义全局变量
    global phsen_ana,env_ws,envw_ana
    phsen_ana = []
    logic_sens = []
    logic_ele = {}   #主干节点的逻辑语义元素，含依存的二三级语义
    json_str = ''   

    for sen_dics in json_ltp[0]: # 每个句子送回的分析字典列表，目前总是只会送一段

        logic_sens.append("")  # 每个新句子建立一个逻辑语义串,逻辑元素和主干接点id清0
        logic_ele = {}   # 每句之中的主干逻辑元素        
        tree_line = []  #描述每个词需要几次才能连到hed上
        #词语信息分类。structure.sen_ana
        thesen_ana = sen_ana () #初始化句子分析对象（车厢）
        thew_anas = [] #初始化句子分析对象（句子内一队词语）
        the_ws = [] #词林分类使用的单词列表
        list_HED = [] #现在把CV也当做HED等级。核心关系	HED
        wgrs = [] #依存串也送入句子分析，每局做个临时的列表
     
        for h_dic in sen_dics:  #开始专门找‘HED’,并列动词处于同等地位。核心关系	HED
            t_wo = h_dic['cont'] #原句子内容
            
            w_l = min(2,len(t_wo)-1) #区分1,2，3以上字数的词
            t_r = h_dic['relate']
            if t_r == 'HED':
                list_HED.append (h_dic['id'])
                logic_ele [h_dic['id']] = 'V=' +  t_wo
            elif t_r == 'COO' :
                if h_dic ['pos'] == 'v' :
                    h_dic ['relate'] = 'COV'   #单独标识并列的动词
                    list_HED.append (h_dic['id'])
            elif t_r == 'WP':
                t_id = h_dic['id']
                if t_id < len(sen_dics)-1:
                    if sen_dics[t_id+1]['cont']=='”':
                        sen_dics[t_id+1]['cont']=' '
                        h_dic['cont'] += '”'
                    
            Pos_ = PosTag.pos_cn(h_dic['pos'])
            thisw_ana = w_ana (wo = t_wo ,pos = Pos_) #构造加载新词汇信息
            if '助词介词连词人名地名'.find(thisw_ana.pos) > -1:
                thisw_ana.syn = t_wo
                thisw_ana.cla = Pos_
                env_ws[w_l].append(t_wo)
                envw_ana[w_l].append(thisw_ana)
            elif thisw_ana.pos == '方位名词':
                thisw_ana.syn = t_wo
                thisw_ana.cla = Pos_    
                env_ws[w_l].append(t_wo)
                envw_ana[w_l].append(thisw_ana)
            thew_anas .append (thisw_ana)
                  
        tsen_in = ''  
        for w_dic in sen_dics :     #回头找一级主干依存
            json_str += str(w_dic)+'\n'
               
            the_wo = w_dic['cont']
            
            tsen_in += the_wo + ' '
       
            the_ws.append (the_wo)
            this_line = ""
            this_wgr = ''
                   
            if w_dic ['relate'] == 'HED' :
                this_line = '-1_'
            if w_dic['parent'] in list_HED :  #以下是与HED关联的主干成分：主谓宾，直接谓语，并列谓语CV，parent=HED的id

                t_r = w_dic['relate']
                if t_r in Yufa_dic :                      
                    logic_ele [w_dic['id']] = Yufa_dic [w_dic['relate']] + '=' +  w_dic['cont']  #先添加主干语义元素内容
                    
                    if t_r =='VOB':
                        print(the_wo)
                        #在对上级依存为SBV，且被依存关系中有SVB/动补、后附加时，这个宾语同时也是谓语，添加一个V
                        t_id = w_dic['id']
                        for w_d in sen_dics:
                            if w_d['parent'] == t_id:
                                if 'VOBCMPRAD'.find (w_d['relate']) > -1 :
                                    logic_ele [w_dic['id']] = logic_ele [w_dic['id']].replace('=','V=')
                    this_line += str(w_dic['id']) +  '_'
                    this_wgr += w_dic['cont'] + '_'            
                else : print ('========' + w_dic['relate'])
            else :
                par = w_dic['parent']   # 用tree_line表示依存线路
                while not (par in list_HED) :  # 顺着parent找HED的id，找到为止，形成一个串
                    if this_line.find('-1') > -1 :
                        break
                    this_line = str(par) + '_' + this_line
                    this_wgr += sen_dics[par]['cont'] + '_'
                    
                    par = sen_dics[par]['parent']
                
                this_line += str(w_dic['id']) +  '_'
                this_wgr += w_dic['cont'] + '_'
            tree_line.append(this_line.strip('_'))   # 依存线索id串
            wgrs.append(this_wgr) #语义关联字符串，和id串对应
        cizu_temp = {}
        ii = 0   # 循环中辅助计数
      
        for w_dic in sen_dics :   #再回头，找主干之后的二级依存，根据依存串描述，二级加标签用冒号挂接，三级直接按顺序用数组连上
            tree_node = tree_line[ii].split('_')
                 
            if tree_node [0] == '-1':
                del tree_node [0]           
                
            if len(tree_node) > 1 :                
                t_key = tree_node [0] + '_' + tree_node [1]                
                if t_key in cizu_temp :
                    cizu_temp [ t_key ] = cizu_temp [ t_key ] + '+' + w_dic['cont']  # 以前两级为key，词组为值，写入字典
                else :
                    cizu_temp [ t_key ] = w_dic['cont']
            ii = ii + 1
      
        for key in cizu_temp :
            any_rela = sen_dics [int(key.split('_')[1])]['relate']  #词组key前一部分是一级id，标识一级ele字典，后一部分是二级id，用两冒号挂接
            logic_ele[int(key.split('_')[0])] += '::' + Yufa_dic [any_rela] + '=' + cizu_temp [key]
         
        for key in logic_ele :            
            logic_sens[-1] += logic_ele [key] + ','
        #查询文本文件方式调用
        #dics = cla_search (the_ws)  #分类函数返回value为syn和cla的两个字典
        #查询数据库方式调用
        dics = newCla_search (the_ws)  #分类函数返回value为syn和cla的两个字典

        
        ww=0
        for wa_dic in sen_dics:  #装载段落分析列车信息
            
            t_wo = wa_dic['cont']
            w_l = min(2,len(t_wo)-1) #区分1,2，3以上字数的词
            thew_anas[ww].wgr = wgrs[ww]
            if thew_anas[ww].syn == '':  #连词助词介词等虚词已经预先装载，跳过类型搜索
                if t_wo in env_ws[w_l]:
                    e_id = env_ws[w_l].index(t_wo)

                    thew_anas[ww].syn = envw_ana[w_l][e_id].syn
                    thew_anas[ww].cla = envw_ana[w_l][e_id].cla
                elif t_wo in dics[0]:
                    thew_anas[ww].syn = dics[0][t_wo]
                    thew_anas[ww].cla = dics[1][t_wo]
                    env_ws[w_l].append(thew_anas[ww].wo)
                    envw_ana[w_l].append(thew_anas[ww])
            ww = ww+1
        thesen_ana = sen_ana(sen_in = tsen_in.strip(' '),sen_mean = logic_sens[-1],w_anas = thew_anas)
        phsen_ana .append(thesen_ana)
    logsen_fix (logic_sens)

    wr_logic = ''
    wr_sen = ''
    time1 = str(time.time())
    new = False
    if new:
        for sen in phsen_ana:
            wr_logic += sen.sen_mean + '\n'
            wr_sen += sen.sen_in
        
        tree0 = ET.ElementTree(file= 'd:/xml/段落语义ltp.xml')   # xml读写的模板，标签写入、模板插入方式大不相同，就分头写算了
        tree0.getroot()
        root = tree0.getroot()    
    #从某文件提取一个模板，加上一个根节点a，再写入指定文档    
        xx=ET.tostring(root.find('阅读场景'),encoding='UTF-8',method="xml")   
        yy= ET.fromstring(xx)
    
        yy.find('句式语义').text=wr_logic
        yy.find('原文').text = wr_sen
        yy.find('依存句法').text = json_str 
    
        root.insert(1,yy)
        tree0.write('d:/xml/段落语义ltp.xml', encoding='UTF-8')

    
            
    

    set_phsen(ph = phsen_ana)  
    return  phsen_ana




def logsen_fix (sens = []):
    fix_dic = {'后附加=了':'时态=完成','。”':'】','！”':'】','标点= ':''}
    
    for se in range(0,len(sens)-1):
        t_se = sens[se].replace('“','【')
        for fix in fix_dic :
            t_se = t_se.replace(fix,fix_dic [fix] ).strip(',')
        phsen_ana[se].sen_mean = t_se
        


'''
通过数据库方式查找同义词及分类

输入：["人","狗","在"]

输出：（｛"人"：第一个同义词CiLin.CiZu，"狗"：第一个同义词，｝,｛"人"："人.品性.英雄 硬汉 烈士cilin_cont.tag_fullname"，，｝)
第一组SQL：SELECT C2.CiZu AS CiZuIn,   C1.CiZu AS CiZuOut　FROM     CiLin AS C1 INNER JOIN
               CiLin AS C2 ON C1.BianMa = C2.BianMa AND C1.XuHao = C2.XuHao 
                WHERE  C2.LeiBie='='  AND  C1.ZiXuHao=1 AND C2.CiZu IN ( '人士','獒')

第一组SQL：SELECT  C.CiZu,CC.tag_fullname  FROM     cilin_cont AS CC INNER JOIN
               CiLin AS C ON CC.tag = left(C.BianMa,4) WHERE   (C.CiZu IN ( '人士','獒'))


'''
def newCla_search (wos = [ ]):
    #把输入的参数列表转换成字符串：['人士','獒']
    strWos=str(wos)
    #删除头尾的[]。做一个SQL的IN参数。'人士','獒'
    strWos=strWos[1:len(strWos)-1]
    #print(p)
    helper = aDB.msSqlHelper()

    #查询同义词。装入字典
    #受底层访问函数的限制。无法把[ ]参数传送给SQL中的IN语句。
    #在此做一个另类处理。直接把参数编写到SQL语句中。
    sql = "SELECT C2.CiZu AS CiZuIn,   C1.CiZu AS CiZuOut　FROM     CiLin AS C1 INNER JOIN  "
    sql =sql + "  CiLin AS C2 ON C1.BianMa = C2.BianMa AND C1.XuHao = C2.XuHao "
    sql =sql + "  WHERE  C2.LeiBie='='  AND  C1.ZiXuHao=1 AND C2.CiZu IN ( "+strWos+" ) ORDER BY CiZuIn"
    aparams = ()
    rows =helper.GetAll(sql  , aparams)
    #把查询结构导入字典中。
    #结构：{'狗': '狗', '人': '身体+人格+人数+人+成年人', '在': '参加+活+取决+存在+位于+在于+正在+在'}
    syndic={}
    CiZuIn="" #输入的词组
    CiZuOuts="" #输出的词组
    for row in rows:
        if row[0] not in syndic.keys():
            syndic[row[0]] = row[1]          #
        else:
            syndic[row[0]]=syndic[row[0]]+"+"+row[1]
    #print(str(syndic))

    #查询词组分类。

    sql = " SELECT  C.CiZu,CC.tag_fullname  FROM     cilin_cont AS CC INNER JOIN "
    sql =sql + "  CiLin AS C ON CC.tag = left(C.BianMa,4) WHERE   (C.CiZu IN ( "+strWos+" ))  "
    aparams = ()
    rows =helper.GetAll(sql  , aparams)
    #把查询结构导入字典中。
    #结构：{'人': '人.泛称.人 人民 众人+人.男女老少.老人 成年人 老小+抽象事物.性能.体格+抽
    #象事物.性格 才能.性格 品行 道德 作风+抽象事物.数量 单位.数量', '狗': '物.动物.猪}
    cladic={}
    CiZuIn="" #输入的词组
    tag_fullnames="" #输出的词组分类
    for row in rows:
        if row[0] not in cladic.keys():
            cladic[row[0]] = row[1]          #
        else:
            cladic[row[0]]=cladic[row[0]]+"+"+row[1]
    #print(str(cladic))
    result = [syndic,cladic]
    #print(str(result))
    return result #输出两字典


def cla_search (wos = [ ]):   #测试了词林分类表.txt搜索的有效性和速度，同时给出组内第一个作为同义词输出，大约40个词/秒。
    #a = str(input("输入或粘贴文本，按下 enter 显示结果"))
    #wos = a.split(' ')
    
    time1 = time.time()
    f=''
    if platform.system()=='Windows':
        
        f = open("D:/MY/python/DaiMeng/DaiMeng/data/xmlData/class_cilin_v0.txt",'r',encoding='UTF-8')
        #f = open("d:/xml/class_cilin_v0.txt",'r',encoding='UTF-8')
    else:f = open("/home/ubuntu/Daimeng_flask/xml/class_cilin_v0.txt",'r',encoding='UTF-8')
    
    lines = f.readlines()
    cc1 ='ABCDEFGHIJKL'   #词林原分类首字母
    cc7 = '0123456789'   #词林原分类末位
    this_cl = '社会.人.人群'  #当前大分类
    Sen = ''
    
    syndic = {}  # 返回同义词和分类字典
    cladic = {}

    wos_bak = wos
    for w in wos:
        w_l = min(2,len(w)-1) #区分1,2，3以上字数的词
        Sen += w
        if w in env_ws[w_l]:  #留下了备份，大胆删除环境池里重复的w_ana数据
            wos.remove(w)
                     

    
      
    for line in lines:   
        line =line.strip('\n').strip(' ') + ' '
        sing_cl = ''
        if line.find('*') > -1 :
            continue
        if len(line) < 3:
            continue
   
        if cc1.find(line[0]) == -1 : 
            line= line.strip(' ')
            sp_line = line.split(' ')
               
            if cc7.find (sp_line[0][-2]) > -1:
                this_cl = sp_line[0]
            else :
                sing_cl = sp_line[0]
               
        cl_len = len(line.split(' ')[0])
        
        ii = 0
        for wo in wos:
            wo_rela = []  #单组同义词替换比较
            sen_rela = []  #二维数组，用于同义词替换后的句子相似度比较
            mulwo = []
            
            sp_line = line.split(' ')
            
            if line[cl_len:].find(' ' + wo + ' ') > -1: #
                rr=0
                syn_str = sp_line[0][-1] + sp_line[1]  #送出井号/等号 + 第一个词，可以区分同义词还是同类词
                if len(wo) == 1: #词的字数做开关
                    mul_ind = -1   #临时多义词序号
                    relas = []
                    if wo not in mulwo:
                        mulwo.append(wo)
                        mul_ind = len(mulwo)-1
                    else: mul_ind = mulwo.index(wo)  #其实都用不着搜集起来，直接标到每个分类后边啦，只是还没下决心删除
                    
                    for sp in sp_line[1:]: #第0个空格前是分类，后边是展开同义词
                        rela_max = 0
                      
                       
                        for w in wos_bak: #每个同义词都要和局子里除自己之外的词算距离
                            if w == wo:   
                                continue
                                
                            try:
                                rela_max = max(rela_max,model.similarity(w,sp))  #调用词汇相似度计算，model60
                            except Exception:continue   #向量表里缺少太多的词，没词就终止，只能强行推进
                       
                        relas.append(rela_max)
                               #以下评分算法是只选三个大于.5的来平均，需要改进
            
                    if len(relas)>0:  
                        rs = 0
                        for r in relas:
                            rs += r
                        rr= int(rs/len(relas)*100)
                         
                    
                  
                
                if sing_cl == '':
                    cla_str = this_cl
                else: cla_str = sing_cl      #单行分类管一行，大分类管到下一个大分类之间  

                if wo in syndic:
                    syndic [wo] += '+' + syn_str  
                    cladic [wo] += '+' + cla_str
                else:
                    syndic [wo] = syn_str 
                    cladic [wo] = cla_str

                if rr > 0:
                    cladic[wo] += str(rr)  #记录每个分类的相似度评分，直接写两个字符
                    #print (wo + cladic[wo])
              
               
                
                #wos.remove(wo)       #只取一个分类的做法，注销后一词有多个分类

    result = [syndic,cladic]
    time2 = time.time()
   
    print (time2 - time1)
    print(str(result))   
    return result #输出两字典
    


