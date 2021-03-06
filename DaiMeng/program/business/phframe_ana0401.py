
# -*- coding:utf-8 -*-
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import *
import urllib
import requests
import time
import json
import  business.trans_ltp as TL
from business.trans_ltp import *
from business.structure import *
import  business.hownet_get as hownet_get
from business.hownet_get import *
import business.sentenceMatch3 as sentenceMatch3
from business.sentenceMatch3 import *
from business.bdZhiDaoHuiDa import Query
import random
def subject_sts(this_und, des_sentence):
    """
    扫描段落理解类中sem_dic字典里的主语，主语按概念.xml文件中<内涵 模板>内“主语=$$=G.in()”描述语句搜索
    :param semdic:传入sem_dic字典参数
    :return: 返回出现次数最多的主语
    """
    sub_dic = {} # 字典的键为主语，值为次数
    sub_lst = this_und.Semdic['主语'].split('\n') # 按\n分隔成n句
    des_sentence = des_sentence[des_sentence.find('(')+1:des_sentence.find(')')]
    sub_cla_lst = des_sentence.split('|') # 将描述句式按|分隔成单个分类
    for sub_sent in sub_lst:
        if(sub_sent.find('剔重')>-1):
            continue
        num = sub_sent[sub_sent.find('sn=')+3:sub_sent.find(',')]# 第几句
        if(sub_sent.find('【') > -1):
            # 【符号后出现的主语均是对话内的主语，全部删除
            sub_sent = sub_sent[:sub_sent.find('【')]
        sub_sen_lst = sub_sent.split(',') # 每句按逗号再次分隔
        for sub_elem in sub_sen_lst:
            if(sub_elem.find('主语=')>-1 and len(sub_elem)>=4):
                # 查看主语是否满足des_sentence逻辑句式，不满足则continue
                for w_ana in this_und.phsen_ana[int(num)].w_anas:
                    if(w_ana.wo == sub_elem[sub_elem.find('主语=')+3:]):
                        for sub_cla in sub_cla_lst:
                            if(w_ana.cla.find(sub_cla)>-1):
                                # 统计主语出现次数并放入字典
                                if (sub_elem[sub_elem.find('主语=') + 3:] in sub_dic):
                                    sub_dic[sub_elem[sub_elem.find('主语=') + 3:]] += 1
                                else:
                                    sub_dic[sub_elem[sub_elem.find('主语=') + 3:]] = 1
    sub_str = ''
    try:
        sub_str = max(sub_dic, key=sub_dic.get) # 找出字典中值最大的键
    except Exception:
        sub_str = ''
    return sub_str

def content_scan(this_und, content):
    """
     根据概念.xml中<内涵 模板>下一级<**内容>中的内容content，搜索sem_dic字典包含该内容的句子数量，
     如果超过总句子数量的20%，则进入该模板主题
     :param sem_dic:传入sem_dic字典参数
     :param content:传入<**内容>中国的内容content
     :return:返回True或者False
     """
    lst = []
    content_bool = True
    if(content.find('{') > -1):
        sub_content = content[:content.find('{')]
        print(sub_content)
        des_sentence = content[content.find('{') + 1:-1]
        print(des_sentence)
        subject_str = subject_sts(this_und,des_sentence)
        if(not subject_str):
            return  False
        if (sub_content in this_und.Semdic):
            # sem_dic字典中content关键字对应的语句数
            lst = this_und.Semdic[sub_content].split('\n')
            num = 0 # 主语满足条件的计数
            for sub_str in lst:
                if(sub_str.find(subject_str) > -1):
                    num +=1

            print(num/len(lst))
            if(num / len(lst) > 0.3):
                content_bool = True
            else:
                content_bool = False
    else:
        if(content.find('.')>0):
            # 例如思维.疑问，搜索this_und.Semdic[思维]的语句达到30%，且疑问占到思维的30%以上，则进入思维.疑问模板
            pre_content = content[:content.find('.')]
            post_content = content[content.find('.')+1:]
            if (pre_content in this_und.Semdic):
                # sem_dic字典中content关键字对应的语句数
                lst = this_und.Semdic[pre_content].split('\n')
            # content关键字对应的语句数超过总句子数量的30%，则返回True
            if '主语' in this_und.Semdic:
                if (len(lst) / len(this_und.Semdic['主语'].split('\n')) > 0.3):
                    count = 0
                    for scan_sen in lst:
                        if(scan_sen[scan_sen.find(pre_content+'=')+len(pre_content)+1:scan_sen.find(',',scan_sen.find(pre_content+'='))] in post_content):
                            count += 1
                    if(count/len(lst) > 0.3):
                        content_bool = True
                else:
                    content_bool = False
        else:
            if (content in this_und.Semdic):
                # sem_dic字典中content关键字对应的语句数
                lst = this_und.Semdic[content].split('\n')
            # content关键字对应的语句数超过总句子数量的30%，则返回True
            if '主语' in this_und.Semdic:
                if (len(lst) / len(this_und.Semdic['主语'].split('\n')) > 0.3):
                    count = 0
                    for scan_sen in lst:
                        if ('问' in scan_sen[scan_sen.find(content + '=') + len(content) + 1:scan_sen.find(',',scan_sen.find(content + '='))]):
                            count += 1
                    if (count / len(lst) > 0.3):
                        content_bool = False
                    else:
                        content_bool = True
                else:
                    content_bool = False
            else:
                trans_ltp.thinking_str += '小呆的语法检查:没有主语你说谁?\n'
    return content_bool


def concept_sen_match(this_und, tag, sen_type):
    """
    # 概念.xml模板中对应的子模版标签，到表达2.xml中搜索对应的逻辑句式
    :param this_und:传入ph_und对象
    :param tag: 传入概念.xml文件名，与表达2.xml中的父标签搜索匹配
    :param sen_type: 传入句式类型，与表达2.xml中的<句式 类型="">搜索匹配
    :return: 返回搜索到的逻辑句式列表
    """
    # 找到表达2.xml的路径
    tree = ET.parse('/home/ubuntu/DaiMeng/data/xmlData/表达2.xml')
    root = tree.getroot()
    sentence_list = []
    for sen_ana in this_und.phsen_ana:
        for parentnode in root.iter(tag):
            for node in parentnode.iter('句式'):
                if(node.attrib):
                    if(node.attrib['类型'] != sen_type):
                        continue
                for childnode in node.iter('描述句式'):
                    if (childnode.text):
                        describe_sentence = childnode.text
                        print('describe_sentence:'+describe_sentence)
                        # 根据描述句式的标签判断是一般匹配还是严格匹配
                        if '匹配' in childnode.attrib:
                            if childnode.attrib['匹配'] == '一般':
                                describe_dict = sentence_normal_match(sen_ana.w_anas, describe_sentence)
                        else:
                            describe_dict = sentence_strict_match(sen_ana.w_anas, describe_sentence)
                        print(sen_ana.w_anas[2].wo+sen_ana.w_anas[2].cla)
                        print(describe_dict)
                    if (describe_dict):
                        #sentence_list.append(describe_dict)
                        if ('逻辑' in childnode.attrib):
                            logic_express = childnode.attrib['逻辑']
                        else:
                            logic_express = node.find('逻辑句式').text
                        sentence_list.append(logic_sentence(describe_dict, logic_express))
                        print(sentence_list)
                        break
    #print(sentence_list)
    # 按出现次数排序，合并相同项
    sentence_dic = {}
    for sentence in sentence_list:
        for sen_elem in sentence:
            if(sen_elem in sentence_dic):
                sentence_dic[sen_elem] += 1
            else:
                sentence_dic[sen_elem] = 1
    lst = []
    while(sentence_dic):
        key_str = max(sentence_dic, key=sentence_dic.get)
        lst.append(key_str)
        sentence_dic.pop(key_str)
    #print(sentence_dic)
    return lst



def spider_result(word_ana_list, des_express, logic_express):
    """
    对爬虫爬回来的信息使用trans_ltp模块进行解析后按照<Q_A匹配>内的句式进行匹配，输出逻辑句式
    :param word_ana_list:爬虫返回的段落的一句
    :param des_express:描述句式
    :param logic_express:逻辑句式
    :return:返回替换后的逻辑句子列表
    """
    #result_str = '燕子燕子善飞，妇孺皆知。其飞行速度每小时可达120公里,堪称是鸟类大家庭中最善于飞翔的成员之一'
    sentence_list = [] #匹配出来的句式列表
    describe_dict = sentence_strict_match(word_ana_list, des_express)
    if (describe_dict):
        sentence_list.append(logic_sentence(describe_dict, logic_express))
    return sentence_list

def qa_model(fra_node, key_words):
    """
    小呆/小萌提问的模板，在概念.xml中查找关键字对应的提问模板
    :param fra_node: 概念.xml中<内涵节点>
    :param key_words: 概念.xml<过程>中关键字主题
    :return: 返回小呆/小萌发现的问题
    """
    qa_str = ''
    for key_node in fra_node.iter(key_words):
        if(key_node.text):
            qa_lst = key_node.text.split('，')
        if(len(qa_lst)>0):
            qa_str = qa_lst[random.randint(0, len(qa_lst) - 1)]
    return qa_str

def move_fun(con_sen,fra_par,main_sub):
    if(fra_par[0].find('.') > 0):
        content = fra_par[0][:fra_par[0].find('.')]
    else:
        content = fra_par[0]
    rand = random.randint(0, len(con_sen) - 1)
    print('con_sen, rand ')
    print(con_sen)
    print(rand)
    while (con_sen[rand][con_sen[rand].find(content + '=') + len(content) + 1:-1] == '下' or
           con_sen[rand][con_sen[rand].find(content + '=') + len(content) + 1:-1] == '上'):
        rand = random.randint(0, len(con_sen) - 1)
    if (rand == 0):
        trans_ltp.thinking_str += '小呆回答问题:' + main_sub + '从' + con_sen[rand][con_sen[rand].find(
            content + '=') + len(content) + 1:con_sen[rand].find(']',con_sen[rand].find(
            content + '='))] + '来\n'
    else:
        trans_ltp.thinking_str += '小呆回答问题:' + main_sub + '经过了' + con_sen[rand][con_sen[rand].find(
            content + '=') + len(content) + 1:con_sen[rand].find(']',con_sen[rand].find(
            content + '='))] + '\n'

def question_fun(con_sen, fra_par, main_sub):
    if (fra_par[0].find('.') > 0):
        content = fra_par[0][:fra_par[0].find('.')]
    else:
        content = fra_par[0]
    rand = random.randint(0, len(con_sen) - 1)
    count = 0
    while('问' not in con_sen[rand][con_sen[rand].find(content + '=') + len(content) + 1:-1]):
        rand = random.randint(0, len(con_sen) - 1)
        count += 1
        if(count == 5):
            break
    if(count < 5):
        rst = con_sen[rand][con_sen[rand].find(content + '=') + len(content) + 1:-1]
        rst = rst[:rst.find(',')] + rst[rst.find('{')+1:rst.find('}')]
        trans_ltp.thinking_str += '小呆回答问题:' + main_sub + rst + '\n'
        rand += 1
        if(not con_sen[rand]):
            return
        if('问' not in con_sen[rand][con_sen[rand].find(content + '=') + len(content) + 1:-1]):
            rst = con_sen[rand][con_sen[rand].find(content + '=') + len(content) + 1:-1]
            rst= rst[rst.find('{')+1:rst.find('}')]
            if('，'in rst):
                rst = rst[rst.find('，')+1:]
            trans_ltp.thinking_str += '小呆陷入沉思:' + rst + '\n'
    else:
        trans_ltp.thinking_str += '小呆回答问题:' + main_sub + '没啥问题呀' + '\n'


def default_fun(con_sen, fra_par, main_sub):
    if (fra_par[0].find('.') > 0):
        content = fra_par[0][:fra_par[0].find('.')]
    else:
        content = fra_par[0]
    rand = random.randint(0, len(con_sen) - 1)
    trans_ltp.thinking_str += '小呆回答问题:' + main_sub + con_sen[rand][con_sen[rand].find(
        content + '=') + len(content) + 1:-1] + '\n'

def indent(elem, level=0):
# 格式化xml
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def search_example(node, qa_all_lst):
    """
    根据Q_A关键字及匹配元素列表qa_all_lst，在<实例与经验>中搜素是否已有实例无需再进行爬取。如果搜索到多个则随机返回一条。
    :param node: <实例与经验>节点
    :param qa_all_lst: Q_A关键字及匹配元素列表qa_all_lst
    :return: 返回搜索匹配到的实例
    """
    example_lst = [] # 用于存储匹配到的实例
    if(not node):
        return ''

    for example_node in node:
        if(example_node.text):
            qa_lst_len = len(qa_all_lst)
            num = 0 # 计数，qa_all_lst内所有元素匹配上才算匹配一条实例
            for qa_ele in qa_all_lst:
                if(qa_ele in example_node.text):
                    num += 1
            if(num == qa_lst_len):
                example_lst.append(example_node.text)
    if(len(example_lst)>0):
        rand = random.randint(0, len(example_lst)-1)
        return example_lst[rand]
    else:
        return ''


def phase_ana():
    """
    根据概念xml中各类模板，分析段落，提取主题内容，写入语义.段落xml中
    """
    global this_und
    this_und = trans_ltp.get_thisund()
    ss = ''
    if len(this_und.phsen_ana) < 3:
        ss += trans_ltp.input_talk  # this_und.rec[0]
    if len(this_und.phsen_ana) <2:
        return
    p_xml = '/home/ubuntu/DaiMeng/data/xmlData/'
    fs = os.listdir(p_xml)
    files = []
    ana_no = []
    for f1 in fs:
        t_path = os.path.join(p_xml, f1)
        if os.path.isdir(t_path):
            continue
        root = None
        if f1[-4:] == '.xml':  # 依次打开xml概念文档。
            if f1.find('概念.') > -1:
                files.append(f1)
                tree0 = ET.parse(t_path)
                root = tree0.getroot()
        else:
            continue
        if root == None:
            continue
        else:
            print(f1)
            selector = etree.parse(t_path)
            for chi in root:
                if chi.find('内涵') == None:
                    continue
                elif '模板' not in chi.find('内涵').attrib:
                    continue
                else:
                    frsem_dic = {}
                    fra_par = [] # 段落语义扫描的主题列表
                    ph_cont = [] # 取回段落中所有关联的语义片段。
                    fra_node = chi.find('内涵')
                    sbv_s = '我们'
                    if '主语' in this_und.Semdic:
                        sbv_s = this_und.Semdic['主语'].split('\n')
                    sta_no = None
                    flag = False
                    for fra_item in fra_node:
                        if fra_item.tag.find('内容') > -1:
                            for content in fra_item.text.split(','):
                                if (content_scan(this_und, content)):
                                    # 装入第一个参数变化内容，即段落语义扫描的主题，可能不止一个。
                                    if(content.find('{') > -1):
                                        fra_par.append(content[:content.find('{')])
                                    else:
                                        fra_par.append(content)
                                    flag = True
                                    print(fra_par)
                            for key in this_und.Semdic:
                                if(len(fra_par)>0 and (key in fra_par[0])):
                                    # 从扫描字典中找出各主题内容，存在ph_cont列表中
                                    key_sem = this_und.Semdic[key]
                                    if('主语' not in fra_par):
                                        ph_cont.append(key_sem)
                        if fra_item.tag.find('过程') > -1:
                            # 处理动词框架的过程。
                            sta_no = ET.fromstring(ET.tostring(fra_item, encoding='UTF-8', method="xml"))
                        if (fra_par):
                            prop_lst = concept_sen_match(this_und, f1[:-4], fra_par[0])
                        else:
                            prop_lst = []
                        print(prop_lst)
                        if (not prop_lst):
                            flag = False
                        if not flag:
                            break
                        if sta_no != None:
                            process_lst = sta_no.text.split('，') # <**过程>中的text按逗号解析成lst
                            sta_no.text = ''
                            main_sub = '' # 主体
                            for process_node in process_lst:
                                if('{' in process_node):
                                    # {}符号内为描述语句，调用subject_sts()方法获取主体内容
                                    sub_proc = process_node[:process_node.find('{')]
                                    des_sentence = process_node[process_node.find('{')+1:-1]
                                    main_sub = subject_sts(this_und, des_sentence)
                                    sta_no.text = sta_no.text + sub_proc +'='+ main_sub + '；'
                                elif('Q_A' in process_node):
                                    # 含Q_A表示要按照<Q_A匹配>模板在网上爬取
                                    # 提取Q_A后面的主题
                                    sub_proc = process_node[3:]
                                    question = qa_model(fra_node, sub_proc)
                                    if(len(main_sub)>0 and len(question)>0):
                                        trans_ltp.thinking_str += '小萌发现问题:' +main_sub+question+'？'+'\n'
                                    print(sub_proc)
                                    phsen_ana = []
                                    for qa_node in fra_node:
                                        if(qa_node.tag.find('Q_A搜索') > -1):
                                            for qa_sub_node in qa_node:
                                                qa_all_lst = [] # Q_A关键字及匹配元素列表，用于判断<实例与经验>中是否已有实例无需再进行爬取
                                                qa_sign = True # Q_A关键字内元素是否在段落中匹配成功
                                                if(qa_sub_node.attrib['主题'] and (qa_sub_node.attrib['主题'] == sub_proc)):
                                                    qa_key = ''# Q_A搜索关键字
                                                    if(qa_sub_node.tag.find('Q_A关键字') > -1):
                                                        qa_key_lst = qa_sub_node.text.split('+')
                                                        for qa in qa_key_lst:
                                                            if ('@N.' in qa):
                                                                qa_str = qa[qa.find('.') + 1:]
                                                                qa_ana = '' # Q_A关键字匹配出的信息
                                                                if(sta_no.text.find(qa_str) > -1):
                                                                    qa_ana = sta_no.text[sta_no.text.find(qa_str)+len(qa_str)+1:sta_no.text.find('；',sta_no.text.find(qa_str))]
                                                                    qa_all_lst.append(qa_str+'='+qa_ana)
                                                                else:
                                                                    qa_sign = False # Q_A关键字如果匹配不出来则不再进行爬取
                                                                if(re.match(r'你|我|他|她|它|你们|我们|他们|她们|它们|咱们',qa_ana)):
                                                                    continue
                                                                qa_key += qa_ana + '+'
                                                            if ('@C.' in qa):
                                                                qa_key += qa[qa.find('.')+1:] + '+'
                                                                qa_all_lst.append(qa[qa.find('.')+1:]+'=')
                                                        if(not qa_sign):
                                                            # Q_A搜索关键字如果匹配不出来，则跳过
                                                            continue
                                                        qa_key = qa_key[:-1]
                                                        search_str = qa_key.replace('+', ' ')
                                                        print(qa_all_lst)
                                                        exp_node = chi.find('实例与经验')
                                                        example = search_example(exp_node, qa_all_lst)
                                                        if(example):
                                                            trans_ltp.thinking_str += '小呆回答问题:' + example[example.find(sub_proc+'=')+len(sub_proc)+1:] + '\n'
                                                            continue
                                                        print('search_str: ', search_str)
                                                        result_str = Query(search_str)['Answer']  # 按关键字爬取段落并返回
                                                        print('result_str: ', result_str)
                                                        result_str.strip('\r\n').replace(u'\u3000', ' ').replace(
                                                            u'\xa0', u' ')
                                                        result_str = result_str.replace('　', '。').replace(',','，').replace(
                                                            '!', '！').replace(':', '：').replace(';', '；').replace(' ', '，').replace('.','。')
                                                        result_str = re.sub('[\+]{3}',r'。',result_str)
                                                        result_str = re.sub('(\d+)(。)',r'\g<1>.',result_str) # 英文句号替换为中文句号后，小数的小数点替换回英文
                                                        result_str = result_str[:350]
                                                        print(result_str)
                                                        if (len(main_sub) > 0 and len(question) > 0):
                                                            if(random.randint(0, 2)):
                                                                think_ans_lst = ['我想想','我问问','思考中','这个问题嘛','我来说说']
                                                                trans_ltp.thinking_str += '小呆陷入沉思:' +think_ans_lst[random.randint(0, len(think_ans_lst)-1)]+'\n'
                                                        phsen_ana = trans_json(request_(result_str))
                                                    # 对爬取的内容按照<Q_A搜索>内描述句式进行匹配，返回逻辑句式
                                                    if(qa_sub_node.tag.find('句式') > -1 and (qa_sub_node.attrib['主题'] == sub_proc)):
                                                        num = 0
                                                        qa_ans_lst = [] # 回答句子列表
                                                        if(not phsen_ana):
                                                            continue
                                                        for sen in phsen_ana:
                                                            logic_result_lst = []
                                                            for childnode in qa_sub_node.iter('描述句式'):
                                                                logic_express = ''
                                                                # 在特殊情况下，使用单句有效的逻辑句式，用于截胡后边的逻辑句式
                                                                if('逻辑' in childnode.attrib):
                                                                    logic_express = childnode.attrib['逻辑']
                                                                else:
                                                                    logic_express = qa_sub_node.find('逻辑句式').text
                                                                logic_result_lst = spider_result(sen.w_anas,childnode.text,logic_express)
                                                                print(logic_result_lst)
                                                                if (len(logic_result_lst)>0):
                                                                    for logic_result in logic_result_lst:
                                                                        if (logic_result):
                                                                            for i,logic_result_str in enumerate(logic_result):
                                                                                if(logic_result_str.find(sub_proc) > -1):
                                                                                    logic_str = logic_result[i].replace('+', '')
                                                                                    logic_str = logic_str[logic_str.find('='):]
                                                                                    sta_no.text = sta_no.text + sub_proc +str(num)+logic_str + '|'
                                                                                    qa_ans_lst.append(logic_str[1:])
                                                                                    num += 1
                                                                    break
                                                        phsen_ana = []
                                                        if (len(main_sub) > 0 and len(question) > 0 and len(qa_ans_lst)>0):
                                                            trans_ltp.thinking_str += '小呆回答问题:' + qa_ans_lst[random.randint(0, len(qa_ans_lst)-1)] + '\n'
                                    sta_no.text = sta_no.text[:-1] + '；'
                                else:
                                    sub_proc = process_node
                                    question = qa_model(fra_node, sub_proc)
                                    if(len(main_sub)>0 and len(question)>0):
                                        trans_ltp.thinking_str += '小萌发现问题:' +main_sub+question + '？'+'\n'
                                    for prop_str in prop_lst:
                                        if('+' in prop_str):
                                            prop_str = prop_str.replace('+','')
                                        if (sub_proc in prop_str):
                                            sta_no.text += prop_str + '；'
                                            if (len(main_sub) > 0 and len(question) > 0):
                                                trans_ltp.thinking_str += '小呆回答问题:' + prop_str[prop_str.find('=')+1:] + '呀\n'
                                            break

                            #parent_node = selector.xpath(" //内涵[@模板 = '%s']/.." % fra_node.attrib['模板'])
                            #if(len(parent_node)>0):
                                #print(parent_node[0].tag)
                            print(chi.tag)
                            name_lst = ['速度', '习性', '外形']
                            if( any(name in sta_no.text for name in name_lst)):
                                for childnode in chi.iter('实例与经验'):
                                    print(childnode)
                                    tmp_shili = ''
                                    qa_lst = [] # 存放<**过程>中包含Q_A的元素
                                    for process in process_lst:
                                        # 提取<**过程>中不包含Q_A的元素，因为Q_A元素可匹配多个答案，而其他元素只匹配一个
                                        if('Q_A' not in process):
                                            if (process.find('{')>-1):
                                                process = process[:process.find('{')]
                                            if (sta_no.text.find(process) == -1):
                                                continue
                                            tmp_str = sta_no.text[sta_no.text.find(process)+len(process)+1:sta_no.text.find('；',sta_no.text.find(process))]
                                            tmp_shili = tmp_shili + process + '=' + tmp_str + ','
                                        else:
                                            qa_lst.append(process.replace('Q_A',''))
                                    for qa_str in qa_lst:
                                        # 循环遍历<**过程>中包含Q_A的元素，按元素值在sta_no.text中查找匹配值
                                        qa_ans_str = sta_no.text[sta_no.text.find(qa_str):sta_no.text.find('；',sta_no.text.find(qa_str))]
                                        qa_ans_lst = qa_ans_str.split('|')
                                        if(len(qa_ans_lst)==0):
                                            continue
                                        # 将<**过程>中元素匹配到的值写入<实例与经验>中
                                        for ss in qa_ans_lst:
                                            # 如果写入的实例与原有重复则不写入
                                            shili_str = tmp_shili + qa_str + ss[ss.find('='):]
                                            con = False
                                            for exam in childnode.iter('实例'):
                                                if(exam.text == shili_str):
                                                    con = True
                                            if(con):
                                                continue
                                            shili = ET.SubElement(childnode, '实例')
                                            shili.text = shili_str
                                            indent(childnode, 2)
                                tree0.write(t_path, encoding='utf-8')
                            for cont in ph_cont:  # 按句子组装模板需要的内容。
                                con_sen = cont.replace('+','').split('\n')
                                con_sen = [x for x in con_sen if x != '']
                                question = qa_model(fra_node, fra_par[0])
                                if (len(main_sub) > 0 and len(question) > 0):
                                    trans_ltp.thinking_str += '小萌发现问题:' + main_sub + question + '？' + '\n'
                                    if('位置' in fra_par[0]):
                                        move_fun(con_sen, fra_par, main_sub)
                                    elif('疑问' in fra_par[0]):
                                        question_fun(con_sen, fra_par, main_sub)
                                    else:
                                        default_fun(con_sen, fra_par, main_sub)
                                for ele in con_sen:
                                    s_id = cat_str('sn=', ele)
                                    t_sbv = ''
                                    for ss in sbv_s:  # 主体涉及的句子去关联主语
                                        if cat_str('sn=', ss) == s_id:
                                            t_sbv = ss.split(',')[-1]
                                    if s_id not in frsem_dic:
                                        frsem_dic[s_id] = 'sn=' + s_id
                                    frsem_dic[s_id] += ',' + t_sbv
                                    frsem_dic[s_id] += ele.replace('sn=' + s_id, '')
                            if len(frsem_dic) > 1:
                                num = 0
                                for k_sn in frsem_dic:
                                    if not k_sn=='':
                                        sta_no.text += fra_par[0]+str(num)+'='+frsem_dic[k_sn]+'|'
                                        num +=1
                                sta_no.text = sta_no.text[:-1]+'；'
                            sta_no.tail = '\n\t'
                            ana_no.append(sta_no)
                            print('sta_no.text:'+sta_no.text)
                            break
    print('ana_no')
    print(ana_no)
    wr_ph(ana_no=ana_no)
    print(trans_ltp.thinking_str)
    #trans_ltp.thinking_str=''


def wr_ph( file='/home/ubuntu/DaiMeng/data/xmlData/语义.段落.xml', ana_no = None):      #写入指定文件，在阅读场景模板中插入扩展思维模板节点
    tree0 = ET.parse(file)
    root = tree0.getroot()
    global ph
    ph = trans_ltp.get_thisund()
    ph_mb = None
    if len(ph.phsen_ana) > 2:
        Mb = root.find('模板')
        Mbno = Mb.find('阅读场景')
        ph_mb = ET.fromstring(ET.tostring(Mbno, encoding='UTF-8', method="xml"))
    else:
        for MM in root:
            if '类型' in MM.attrib:
                if MM.attrib['类型'] == '闲聊':
                    ph_mb = ET.fromstring(ET.tostring(MM, encoding='UTF-8', method="xml"))
                    maxid = 0
                    if 'maxid' in MM.attrib:
                        maxid = int(MM.attrib['maxid']) + 1
                    else:
                        MM.attrib['maxid'] = '0'
                        maxid = 0
                    ph_mb.find('原文').text += 'sn=' + str(maxid) + ',' + ph.rec[0] + '\n'
                    ph_mb.attrib['maxid'] = str(maxid)
                    ss = 0
                    Yc_str = ''
                    Ex_str = ''
                    for sen in ph.phsen_ana:
                        Yc_str += 'sn=' + str(ss) + ',' + sen.sen_mean + '\n'
                        if sen.exp_mean != '':
                            Ex_str += 'sn=' + str(ss) + ',' + sen.exp_mean + '\n'
                        ss += 1
                    ph_mb.find('依存语义').text += Yc_str
                    ph_mb.find('经验语义').text += Ex_str
                    ph_mb.find('语义扫描').text += str(ph.Semdic)+'\n'
                    ph_mb.find('思维记录').text += Thlog_ana()
                    ph_mb.tail = '\n\t'
                    root.append(ph_mb)
                    root.remove(MM)
                    tree0.write(file, encoding='UTF-8')
                    return
    if ph_mb == None:
        return

    ph_mb.find('原文').text += ph.rec[0] + '\n'
    ss = 0
    Yc_str = ''
    Ex_str = ''
    for sen in ph.phsen_ana:
        Yc_str += 'sn=' + str(ss) + ',' + sen.sen_mean + '\n'
        if sen.exp_mean != '':
            Ex_str += 'sn=' + str(ss) + ',' + sen.exp_mean + '\n'
        ss += 1
    ph_mb.find('依存语义').text = Yc_str
    ph_mb.find('经验语义').text = Ex_str
    ph_mb.find('语义扫描').text = str(ph.Semdic)
    ph_mb.find('思维记录').text = Thlog_ana()

    if ana_no != None:
        for an in ana_no:
            ph_mb.append(an)
            ph_mb.tail = '\n\t'
    root.append(ph_mb)
    mb = -2
    new_str = ph.rec[0]
    while mb > max(-7, -len(root)):  # 删除重复节点
        Yw_str = None
        Yw_str = root[mb].find('原文').text
        if Yw_str == None:
            continue
        if Yw_str == new_str:
            root.remove(root[mb])
            break
        else:   # 抽样检查,词语重复率95%以上视为一致
            c_m = 0
            c_l = 0
            cc = 0
            while cc < len(Yw_str):
                f_cc = max(0, cc-5)
                b_cc = min(cc+6, len(new_str))
                if new_str[f_cc:b_cc].find(Yw_str[cc:cc+2]) > -1:
                    c_m += 1
                c_l += 1
                cc += 3
            if c_m * 100 / c_l > 95:
                root.remove(root[mb])
                break
        mb = mb -1
    tree0.write(file, encoding='UTF-8')


def Query_ana(phase=phsen_ana):  # 分析疑问
    ss = 0
    for sen in phase:
        if sen.env_mean.find('=疑问') > -1:
            sen_res = sentence_match_result(sen.w_anas, js_cla='疑问')  # 加一轮句式匹配。
            if sen_res:

                index = str(sen_res[-1]).find('疑问内容=')
                add_senmean = sen.sen_mean
                if index > -1:  # 做一词疑问句匹配后，捕捉疑问内容
                    ind_dh = str(sen_res[-1])[index:].find('，')
                    add_senmean += str(sen_res[-1])[index:ind_dh - 1]
                if add_senmean[-2:] == '=V':  # 明示动词的疑问指代，即干什么，疑问不仅是宾语，还是谓词
                    add_senmean = add_senmean.replace('V=', 'V=疑问=')
                    phase[ss].sen_mean = add_senmean


        ss += 1
    An_result = Answer_mat(phase)
    return An_result

def Answer_mat(phase=phsen_ana):  # 在xml文档中，分别匹配1内存phsen，2tag树和text，3简易概念库中匹配底层tag和text里的逻辑语义元素
    global tag_mat
    Q_id = []  # 疑问句子号
    Q_log = []  # 疑问句逻辑句式
    Q_mat = []  # 疑问句匹配情况标记，临时使用
    Q_Answer = []  # 所有回答集合
    s0 = 0
    for sen in phase:
        if sen.env_mean.find('=疑问') > -1:
            Q_id.append(s0)
            Q_Answer.append([])
            Q_log.append(sen.sen_mean)
            Q_mat.append(False)
        s0 += 1
    ee = 0
    for sen in phase:
        for Qs in range(0, len(Q_log)):
            if ee == Q_id[Qs]:
                continue
            sp_Q = Q_log[Qs].split(',')
            for Q_se in sp_Q:
                sp_Qe = Q_se.split('=')
                if '主语CV宾语状语定语'.find(sp_Qe[0]) == -1:  # 非主要句子成分忽略
                    continue
                elif sen.sen_mean.find(Q_se) > -1:  # 直接包含最好
                    Q_mat[Qs] = True
                    continue
                elif sen.sen_mean.find(sp_Qe[0]) > -1:
                    if sp_Qe[1] == '疑问':  # 匹配疑问的后面一段
                        Q_mat[Qs] = True
                        r_mean = sen.sen_mean[sen.sen_mean.find(sp_Qe[0]) + 1:]
                        Q_cat = r_mean[:r_mean.find(',') - 1]
                        continue
                    else:
                        Q_mat[Qs] = False
                        break
                else:
                    Q_mat[Qs] = False
                    break

            if Q_mat[Qs]:
                Q_Answer[Qs].append(sen.sen_in + '\n')
                Q_mat[Qs] = False

        ee += 1

    if Q_Answer == [[]]:  # 在之前内存句子中找不到，则搜索xml概念库
        print('seach_fr文档xml')
        p_xml = '/home/ubuntu/DaiMeng/data/xmlData/'
        fs = os.listdir(p_xml)
        for f1 in fs:
            t_path = os.path.join(p_xml, f1)
            if os.path.isdir(t_path):
                continue
            if f1[-4:] == '.xml':  # 依次打开xml概念文档。
                tree0 = ET.parse(t_path)
                root = tree0.getroot()
                read_list = []
                tag_mat = []
                for QQ in Q_log:    # 先以标签为线索找一遍。
                    walk_mat(root, read_list, QQ)

                if len(read_list) > 0:
                    Q_Answer.append(read_list[-1][-1])
                    print('*'*10)
                    print(read_list[-1][-1])
                gn_node = root.find('简易概念')  # 简易概念里面再找一遍
                if gn_node:
                    for child in gn_node.getchildren():
                        for Q_str in Q_log:
                            if Q_str.find('=' + child.tag) > -1:  # 拆开疑问句，和简易概念里的文档匹配
                                c_t = child.text
                                sp_Q = Q_str.replace('::', ',').split(',')

                                for Q_e in sp_Q:
                                    if_emat = False
                                    if Q_e.find('=') == -1:
                                        continue

                                    index = -1  # 拆开疑问句，和简易概念里的文档匹配
                                    t_mat = ''
                                    if c_t.rfind(Q_e.split('=')[1] + '=') > -1:
                                         index = c_t.rfind(Q_e.split('=')[1] + '=')
                                         if_emat = True
                                         Q_Answer.append(child.tag + '呢，')
                                    elif c_t.rfind('=' + Q_e.split('=')[1]) > -1:
                                        index = c_t.rfind('=' + Q_e.split('=')[1])
                                        if_emat = True
                                        Q_Answer.append(child.tag + '呢，')
                                    while index > -1:
                                        ind = index
                                        t_mat += c_t[index:][:c_t[index:].find('\']')]  # mat后半部分，以]为界
                                        while index > 0:  # 向前找
                                            if '[]\''.find(c_t[index]) == -1:
                                                t_mat = c_t[index - 1] + t_mat
                                            else:
                                                break
                                            index += -1
                                        c_t = c_t[:ind-1]

                                        if c_t.rfind(Q_e.split('=')[1] + '=') > -1:
                                            index = c_t.rfind(Q_e.split('=')[1] + '=')
                                        elif c_t.rfind('=' + Q_e.split('=')[1]) > -1:
                                            index = c_t.rfind('=' + Q_e.split('=')[1])
                                        else:
                                            index = -1

                                    if t_mat != '':
                                        Q_Answer[-1] += t_mat
                                        print('AAAAAAAAAAA')
                                        print(len(Q_Answer))

    for an in Q_Answer:
        trans_ltp.thinking_str += '问题回答::' + str(an) + '\n'
    return Q_Answer


def myexp_ana(f1='概念.我.xml',no='我所知'):  # 逐步向通用搜索引擎演变。
    Rem_str = ''
    global this_und
    this_und = get_thisund()
    # this_und = structure.ph_und(phsen_ana=trans_ltp.get_phsen())  可能会安装一个新的ph_und
    p_xml = '/home/ubuntu/DaiMeng/data/xmlData/'
    tree0 = ET.parse(p_xml + f1)
    root = tree0.getroot()

    myexp = None
    exp_my = []


    keys = []   # 要搜的元素值（关键字）剔重
    att = []    # 以上对应的语义标签
    pron = False
    dic_k = {}
    for sem in this_und.Semdic:
        if sem not in ['主语+V+宾语','位置']:
            continue
        if sem.find('统计') > -1:
            continue
        for ele in this_und.Semdic[sem].strip('\n').split(','):
            if ele.find('sn=') > -1:
                continue

            sp_ele = ele.split('=')
            for es in sp_ele[-1].strip(']').split('+'):
                if es not in keys:
                    if re.match(r'[你我他她它上后里]', es):  #
                        continue
                    hn_es = find_words(word_key=es)
                    stop = False
                    for hn in hn_es:
                        if hn.def_trans_groups()[0].find('是非关系.是') > -1:
                            stop = True
                            break
                    if not stop and es not in dic_k:
                        dic_k[es] = sp_ele[0].strip('[')

                # cw_ana = Hn_ana(ele)
    if re.search(r'[你] ', this_und.phsen_ana[0].sen_in):
            pron = True
            dic_k['小萌'] = '你'

    for exp in root.iter(no):  #找到节点参数的大XML
        myexp = exp
        break
    ei = 0
    mat_v = {}  # 记录匹配元素的次数

    for ex in myexp:
        double = False
        score = 0  # 拟合评分
        mat_d = {}
        topic = ex.tag
        if topic == '象声词': #先放过
            continue
        if not ex.text:
            continue

        for sen in re.split('[。！”？\n]|\.\.\.*',ex.text):
            if len(sen) < 3:
                continue
            ssco = 0 # 大句子评分
            for sse in re.split('[,，；]', sen):  # 小句子评分
                sco = 0
                mat_e = []
                for k in dic_k:
                    if topic.find(k) > -1:
                        mat_e.append(k)
                        mat_d[topic] = k
                    if sse.find(k) > -1:
                        sco += 1
                        if k.strip() not in mat_e:   #重复项只加一分
                            mat_e.append(k.strip())
                            sco += 5
                        if sse in mat_d:
                            if ('+' + mat_d[sse] + '+').find('+' + k + '+') == -1:  #  重复的不要
                                mat_d[sse] += '+' + k
                            else: continue
                        else:mat_d[sse] =  k
                        if k in mat_v:
                            mat_v[k] += 1
                        else: mat_v[k] = 1
                if len(mat_e) == 1:
                    for sk in dic_k:  # 只找到一个词，则找其它关联词
                        if sk == mat_e[0]:
                            continue
                        rel_w = relate_ana(sse,sk)
                        if rel_w:
                            mat_e.append(rel_w)
                            if sse in mat_d:
                                if sse.find(rel_w) > sse.find(mat_d[sse]):
                                    mat_d[sse] += '+' + rel_w
                                else:
                                    mat_d[sse] = rel_w + mat_d[sse]
                                break
                            else:mat_d[sse] = rel_w

                if len(mat_e) > 1:
                    print('eeeeeeeeeeeeee')
                    print(mat_d[sse])
                    double = True
                    sco += (len(mat_e) - 1) * 15

                if double and len(mat_d) > 2:
                    break
                ssco = max(ssco,sco)
                score = max(score, ssco)
            if double and topic.find('.设定') > -1:
                break

          # 简单记录三个得分最高的句子段落。

        if double:  #两个元素是必要条件
            res = [ex.text,score,mat_d,mat_v,topic]
            print('tttttttttt'+topic)
            exp_my.append(res)
            double = False
            if len(exp_my) > 2:   # 目前记录5个单句分值最高的段落。
                break
        ei += 1

    bak_und = get_thisund()

    for key in mat_v:
        mat_v[key] = mat_v[key] * 1000 / ei
    a_exp = ''
    if len(exp_my) > 1:
        ra = random.randint(0, len(exp_my) - 1)
        exp_my[ra][3] = mat_v
        a_exp = riji_ana(exp_my[ra])
        print(exp_my[ra][2])
    elif len(exp_my) == 1:
        print(exp_my[0][2])
        a_exp = riji_ana(exp_my[0])

    if len(a_exp) > 3:
        Rem_str += a_exp
    print(Rem_str)
    trans_ltp.set_thisund(ph=bak_und)
    return(Rem_str)


def riji_ana(exp = None):
    if exp == None:
        return None
    rj_text = exp[0]
    if len(rj_text) < 3:
        return ''
    top_dic ={'日记':'的回忆','象声词':'反复嚷嚷','行为规范':'讲规矩','典型儿歌':'放飞自我','安全常识':'警察叔叔提醒小朋友们',
              '作息时间':'咱讲讲习惯','卫生常识':'讲卫生','小呆.设定':'我的亲朋','小萌.设定':'我的亲朋'}
    add_dic ={'日记':'那一回','象声词':'这样响的','行为规范':'小朋友们要牢记','典型儿歌':'咱也来一段','安全常识':'注意：谨记',
              '作息时间':'是时候该','卫生常识':'请注意卫生习惯','小呆.设定':'我爱他们','小萌.设定':'我爱他们'}
    d_m = ['小呆','小萌']
    rem_str = ''
    rem_top = top_dic[exp[4]]
    dm = 0 # 0呆1萌 控制字头，轮换发言者
    if re.search(r'卫生|儿歌|日记|象声词',rem_top):
        dm = 1

    lines = 0
    for sen in re.split('[。！”？]|\.', rj_text):   #大句子送语言云，减小篇幅
        if_m = False
        if len(sen) < 3:
            continue
        t_key = ''
        M_s = ''
        for key in exp[2]:  # key是标点间的短句。
            if sen.find(key) > -1:
                if_m = True
                t_key = key
                M_s = exp[2][key]
                break

        if not if_m:
            continue
        trans_json(request_(sen))
        Ds_scan()
        fast_scan()

        my_und = get_thisund()
        lines += 1
        jcx = '偶尔'  # 日常 经常 还是偶尔 dic_v记录了匹配的归一化次数 将来做个数组或者dic，记录多个参数
        sc = 0
        dm = 1
        for j in M_s.split('+'):
            if j in exp[3]:
                sc = max(sc,exp[3][j])
        if sc > 500:
            jcx = '日常'
        elif sc > 80:
            jcx = '经常'

        rem_str += d_m[dm] + rem_top + ':'
        if exp[4] == '日记':
            ran = structure.Rem_dic[jcx].split('+')
            r_s = ran[random.randint(0, len(ran) - 1)]
            rem_str += r_s.replace('@S1',M_s) + '...'
        rem_str += add_dic[exp[4]] + '，' + key + '......\n'


        for ss in my_und.phsen_ana:
            t_sen = ss.sen_in.replace(' ','')
            b_id = t_sen.find(t_key.replace('+','')) # 发现关键字短句的起始位置
            if b_id == -1:
                continue
            print (t_sen)
            sp = 0
            for sss in re.split('[,，]',t_sen):
                if len(sss) < 2:
                    continue
                if dm == 0:  # 一人一句
                    dm = 1
                else:
                    dm = 0
                    sss = re.sub(r'[今明后昨前]天','那天',sss.replace('我','你'))
                if t_sen.find(sss) > b_id:

                    if re.search('[然?而|一边]',sss):  # 如果有连词就不加表达插件
                        rem_str += d_m[dm] + rem_top + ':' + sss + '，\n'

                    elif exp[4] in Rem_dic:
                        ran = structure.Rem_dic[re.sub(r'小[呆萌]','',exp[4])].split('+')
                        r_s = ran[random.randint(0, len(ran) - 1)]
                        rem_str += d_m[dm] + rem_top + ':' + r_s.replace('@S1', sss) + '\n'

                    else:
                        rem_str += d_m[dm] + rem_top + ':' + sss + '，\n'
                    print(sss)
                    if exp[4].find('设定') > -1 and sp > 2:
                        break
                sp += 1
        if lines > 2:
            break
    if exp[4].find('设定') > -1:
        ssm = ''
        ssd = ''
        for rr in rem_str.split('\n'):
            if ssm == '':
                ssm += rr
                continue
            if rr[0:2]=='小萌':
                ssm += rr.split(':')[-1]
            else: ssd += rr
        rem_str = ssm + '\n' + ssd + '\n'
    return rem_str


def relate_ana(sse='',sk=''):
    if sse=='' or sk=='':
        return None
    stop = ['姥爷']
    syn = []
    for w_a in trans_ltp.envw_ana[len(sk) - 1]:
        if sk == w_a.wo:
            syn = w_a.syn.split(' ')
            if re.search(r'[子员老]', sk):
                syn.append(re.sub(r'[子老员]', '', sk))
            elif len(sk) == 2 and sk not in stop:
                syn.append(sk[0])
                syn.append(sk[1])
            break

    for kk in syn:
        if kk == '' or kk == '=':
            continue

        if sse.find(kk) > -1:
            return(sk+':'+kk)
            break
    return None


def Hn_ana(ele):
    hn_dic = {}
    wg_c = ele.split('=')[-1].strip(']')
    # cw_ana = w_ana(wo=wg_c)
    for e in wg_c.split('+'):
        hn_dic['DEF.' + e] = []  # 找出整理.txt中的DEF分类。将形成一个二维列表。
        for hn_d in find_words(word_key=e):
            hn_dic['DEF.' + e].append(hn_d.def_trans_groups())

    print('hn'*5)
    print(hn_dic)
    return(hn_dic)



def Thlog_ana(t_s = ''):  # 思维记录分析后最终表达。
    think_exp = ''
    if t_s == '':
        t_s = trans_ltp.thinking_str
    # print(think_str)
    sp_th = t_s.split('\n')
    for ps in sp_th:
        spk = thinksen_trans(ps)
        if len(spk) > 0:
            think_exp += spk + '\n'
    return think_exp


def thinksen_trans(ps=''):  # 根据字典最后一步转换为表达口语
    if re.match('小[呆萌]', ps):
        return ps
    exp_str = ''
    value = ''
    key = cat_str('重要的', ps, '=')
    if key == '':
        key = cat_str('记得的', ps, '=')
    if ps.find('=') > -1:
        value = ps.split('=')[1]
    Exp_dic = trans_ltp.Exp_dic
    sp_expjs = []
    if key in Exp_dic:
        sp_expjs = Exp_dic[key].split('+')
    exp_str = ''
    if sp_expjs == []:
        return ''

    for ee in value.split(','):
        e_str = sp_expjs[random.randint(0, len(sp_expjs) - 1)]
        if len(key.split('+')) == 1:  # 属性项没有+号就不循环了
            exp_str += e_str.replace('@S0', ee) + ','
            continue
        if len(key.split('+')) != len(ee.split('+')):
            continue
        for kk in range(0, len(key.split('+'))):  # 前边按+分，后边按,分元素
            e_str = e_str.replace('@S' + str(kk), ee.split('+')[kk])  # 有+ 的元素一次替换
        exp_str += e_str
    exp_str = exp_str.replace('+', '')
    if exp_str != '':
        if',，'.find(exp_str[0]) > -1:
            return ''
    return exp_str


if __name__ == "__main__":
    exp_ana()





