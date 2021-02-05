# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
from lxml import etree
import re
from os import path
import business.structure as structure
from business.structure import *

from business.trans_ltp import *
import business.trans_ltp as trans_ltp
import business.hownet_get_db as hownet_get_db
import platform, os
import collections

global d_key
def set_d_key(wo='', pos='', syn='', cla=''):
    # 告诉编译器我在这个方法中使用的a是刚才定义的全局变量a,而不是方法内部的局部变量.
    global d_key
    d_key = w_ana(wo=wo, pos=pos, syn=syn, cla=cla)


def get_d_key():
    global d_key
    return d_key
dicexpl_key =w_ana()  # 用于字典查询时的公用参数


# 一个词汇是否匹配描述句式一个元素
def element_match(word_ana, describe_str):

    gin_sign = False
    p_sign = False
    GP_s = False

    if (re.search('@G.in', describe_str)):
        gin_sign = True
    elif (re.search('@P.', describe_str)):
        p_sign = True
    elif  (re.search('@GP.', describe_str)):
        GP_s =True
    describe_str = re.sub('[@G()]|.in|P.|opt', '',describe_str)



        # 数据句子词汇的单词、词性、分类任意一个能匹配上描述句式当前元素则匹配成功
    element = re.sub('\d+', '', describe_str)  # 把元素后面的数字去掉


    rere = re.compile(r'((' + element + ')+)')

    if (gin_sign):

        if (re.search(re.compile(r'((' + element + ')+)'), word_ana.cla)):
            return True
    elif p_sign:

        if(re.match(re.compile(r'((' + element + ')+)'), word_ana.pos)):
            return True
    elif GP_s:
        if (re.search(re.compile(r'((' + element.split('+')[0] + ')+)'), word_ana.cla)):
            if (re.search(re.compile(r'((' + element.split('+')[1] + ')+)'), word_ana.pos)):

                return True

    else:
        if (re.match(re.compile(r'((' + element + ')+)$'), word_ana.wo)):

            return True
        else:
            sp_syn = word_ana.syn.split('+')
            for syns in sp_syn:
                if re.search(r'[#@]', syns):  # 清理同义词带#@就放过，留下=
                    continue
                for sy in syns[0:].split(' '):
                    if (re.match(re.compile(r'((' + element + ')+)'), sy)):
                        return True  # 如果直接匹配不上，某个同义词匹配上也行
                    break # 封锁该功能，只用一项
    return False


# 输入句子与描述句式严格顺序匹配，除了opt@，按顺序进行匹配
def sentence_strict_match(word_ana_list, des_sent):
    global d_key
    # return: 描述句式list与词汇数据list全部匹配则返回字典describe_dict（描述句式元素: 词汇数据元素）

    B_C = -1
    C_pars = []  # @C参数组的列表
    C_par = [0, '']  # @C匹配参数的元组
    Cw_ana = []
    des_org = des_sent.split(',')
    des_sent_list = des_sent.split(',')  # 原始数据备份，在@as变量时有效

    if des_sent.find('@C.') == -1 and des_sent.find('@Y.') == -1:
        if len(word_ana_list) - len(des_sent_list) > 2:  # 没有@C和@Y变量时，长句子不要匹配太短句型
            return {}

    compare = False
    describe_dict = collections.OrderedDict()
    i = 0  # 控制word_ana_list词汇数据List循环
    j = 0  # 控制describe_sentence_list描述句式List循环
    k = 0  # 控制最外层循环
    as_pars = []  # @as参数组的列表
    as_par = ['wo', '']  # @as匹配参数的元组
    if_as = False

    if des_sent.find('@as') > -1:
        dd = 0
        for des in des_sent_list:  # 记录装载本次des句式中包含的as变量位置和参数
            if des[:3] == '@as':
                if_as = True
                as_pai = des.split('.')
                if int(as_pai[1]) == -1:  # 如果是公用的dicexpl_key则单独装载。(-1表示)
                    d_key = get_d_key()
                    # print ('dddddddd'+d_key.wo + ':::' + d_key.pos )
                    if as_pai[2] == 'wo':
                        des_sent_list[dd] = d_key.wo
                    elif as_pai[2] == 'pos':
                        des_sent_list[dd] = '@P.' + d_key.pos
                    elif as_pai[2] == 'syn':
                        des_sent_list[dd] = d_key.syn.split('+')[0]
                    elif as_pai[2] == 'cla':
                        cat_cla = d_key.cla.split('+')[0].split('.')[-1]
                        cat_cla = re.sub('\d+', '', cat_cla)
                        cat_cla = re.sub('[=#@]+', '', cat_cla)
                        des_sent_list[dd] = '@G.in(' + cat_cla[cat_cla.find('_') + 1:] + ')'  # 只取对应目标的第0个分类的最后一截。

                    # @as变量的1号位置是跟随的des句式元素序号，从0开始；2号位置是跟随的内容（分类，词性或者词本身），dd是本身的位置。
                else:
                    as_par = [dd, int(as_pai[1]), as_pai[2]]
                    as_pars.append(as_par)
            dd += 1

    mat_id = [-1] # 初始状态也不越界
    while (i < len(word_ana_list)):
        while (j < len(des_sent_list)):
            bk_mat = False
            describe_str = des_sent_list[j]
            if describe_str[:3] == '@C.':
                B_C = i
                C_par = [describe_str, '']  # 装在@C参数,分别为@C项位置，@C项type，@C项内容（由type）决定。
                if C_par[0].split('.')[1] == 'wo':
                    C_par[1] += word_ana_list[i].wo
                Cw_ana.append(word_ana_list[i])
                C_pars.append(C_par)

                if j == len(des_sent_list) - 1:  # 如果@C是最后一项，后边直接一网打尽
                    bk_mat = True
                    iii = i
                    describe_dict[des_org[j]] = ''
                    while iii < len(word_ana_list):
                        if describe_str.split('.')[1] == 'wo':
                            describe_dict[des_org[j]] += word_ana_list[iii].wo + '+'
                        Cw_ana.append(word_ana_list[iii])
                        iii += 1
                    i = len(word_ana_list) - 1
                    print(describe_dict)

                else:  # 不在最后时建立@C参数组，准备接受连接项，接受后面项的控制。
                    if i < len(word_ana_list) - 1:  # j循环中不管i出界，需要自己防止
                        i += 1
                        j += 1
                    else:
                        compare = False
                        return {}  #
                    continue
                compare = True

            elif describe_str[:3] == '@Y.':   # @Y变量需要前后词语信息判断，Y变量建议连续使用
                for ww in range(i, len(word_ana_list)):  # 在写@Y变量时要考虑到前后秩序
                    if word_ana_list[ww].pos == '标点':
                        break
                    # 由wgr词组判断是否关联 一级直连的放行，因为前边只能是HED
                    if_rel = ('_' + word_ana_list[ww].wgr + '_').find('_' + word_ana_list[mat_id[-1]].wo + '_')
                    if j == 0:
                        if_rel = True
                    elif 'HEDCOV'.find(word_ana_list[ww].yuf) > -1:
                        if_rel = True
                    # 这里要求前后的两项有语法依存关系，HED关联的那一层关系无效，不能跨越标点使用
                    # print(sen.w_anas[ww].yuf + '++++' + cat_str('@Y.', des_str[j], '+'))
                    if if_rel and word_ana_list[ww].yuf == cat_str('@Y.', des_org[j] + '+', '+'):  # 会漏一个字符
                        if describe_str.find('+') == -1:   # 单一条件直接匹配成功
                            word_ana_list[i].ele = '+' + describe_str
                        elif element_match(word_ana_list[ww], describe_str.split('+')[-1]):   #后边还有一个条件需要满足
                            word_ana_list[i].ele = '+' + describe_str
                        else:
                            continue
                        describe_dict[des_org[j]] = word_ana_list[ww].wo
                        compare = True
                        mat_id.append(ww)
                if compare:
                    if j == len(des_sent_list) - 1:
                        return describe_dict

                    else:
                        j += 1
                        i = max(mat_id[-1],i) + 1
                        continue
                elif i == len(word_ana_list) -1:
                    return {}
                else:
                    j = 0
                    k += 1
                    i = k
                    mat_id = [-1]
                    continue

            if B_C > -1 or describe_str.find('ba') > -1:  # 单项倒序列搜索,通常用于@C之后的边界
                sp_C = C_pars[-1][0].split('.')
                ii = len(word_ana_list) - 1
                if not bk_mat:
                    while ii > i - 1:  # 如果@C是最后一项，就跳过这段
                        if (element_match(word_ana_list[ii], describe_str)):
                            bk_mat = True
                            describe_dict[des_org[j]] = word_ana_list[ii].wo
                            for iii in range(i, ii):
                                if sp_C[1] == 'wo':
                                    C_pars[-1][1] += '+' + word_ana_list[iii].wo
                                Cw_ana.append(word_ana_list[iii])

                            i = ii
                            break
                        ii += -1
                if bk_mat:  # @C的句式完成边界后，用正则表达式匹配一次内容,只匹配一项，有多项需求用宽松或者扫描了
                    if len(sp_C) > 2:
                        sp_C[2] = sp_C[2].replace('。', '.')  # 由于参数用.隔离，与正则的.冲突，只能做个替代转义
                        if len(sp_C[2]) > 1:  # 长度>1时，启动正则表达式和@C内置匹配条件，否则只是多个C.wo的编号
                            lene = 4 + len(sp_C[1])
                            cele = C_pars[-1][0][lene:]
                            print(cele)
                            if cele[0]=='@':
                                C_i = B_C
                                C_mat = False
                                while C_i < len(word_ana_list):
                                    if element_match(word_ana_list[C_i],cele):
                                        C_mat =True
                                        break
                                    C_i += 1
                                if C_mat:
                                    describe_dict[des_org[j - 1]] = (C_pars[-1][1])
                                    print('ooooooC' + C_pars[-1][1])
                                else:
                                    return {}
                            elif re.search(re.compile(r'((' + cele + ')+)'), C_pars[-1][1]): #常量不分秩序随意
                                describe_dict[des_org[j - 1]] = (C_pars[-1][1])  # 倒序发现后@C后一项，封闭赋值
                                print('oooooo@'+ C_pars[-1][1])
                            else:
                                return {}
                    elif des_org[j].find('@C.')== -1:  # 排除最后一项为@C的情况，
                        describe_dict[des_org[j - 1]] = (C_pars[-1][1])
                      # 倒序发现后@C后一项，封闭赋值

                else:
                    return {}

                if i < len(word_ana_list) - 1:
                    i += 1
                elif j == len(des_sent_list) - 1:
                    print(describe_dict)
                    return describe_dict

                else:
                    return {}
                j += 1
                B_C = -1
                continue

            if (re.match(r'opt(.*?)', describe_str)):
                # 含opt的情况
                if (element_match(word_ana_list[i], describe_str)):
                    compare = True
                    describe_dict[des_org[j]] = word_ana_list[i].wo
                    i += 1  # 当前元素匹配成功，则word_ana_list词汇数据List指针往后移1
                    j += 1  # describe_sentence_list描述句式List指针往后移1
                    mat_id.append(i)
                    break
                else:
                    compare = True
                    j += 1
                    continue
            else:
                # 不含opt的情况
                if (element_match(word_ana_list[i], describe_str)):
                    describe_dict[des_org[j]] = word_ana_list[i].wo
                    mat_id.append(i)
                    # print('mmmmmmm'+ word_ana_list[i].wo + '::' + describe_str + '!!!' + str(des_sent_list))
                    compare = True

                    if if_as:
                        for a_par in as_pars:  # 每一项匹配成功后，查找后边有没有as项追随自己，发现后按各参数执行替换。
                            if int(a_par[1]) == j:
                                if a_par[2] == 'v':
                                    des_sent_list[int(a_par[0])] = des_sent_list[j]
                                elif a_par[2] == 'wo':
                                    des_sent_list[int(a_par[0])] = word_ana_list[i].wo
                                elif a_par[2] == 'pos':
                                    des_sent_list[int(a_par[0])] = '@P.' + word_ana_list[i].pos
                                elif a_par[2] == 'cla':
                                    des_sent_list[int(a_par[0])] = '@G.in' + word_ana_list[i].cla


                    if B_C >-1:
                        B_C = -1
                        describe_dict[des_org[j - 1]] = C_pars[-1][1]  # 上一个@C变量捕捉完毕，加入字典
                    # if i < len(word_ana_list)-1:
                    i += 1
                    j += 1
                    break
                elif B_C>-1:  # 匹配不成时，装载上一个@C变量项
                    compare = True
                    if C_pars[-1][0] == 'wo':  # 装载什么内容
                        C_pars[-1][1] += ('+' + word_ana_list[i].wo)
                    if i < len(word_ana_list) - 1:  # j循环中，需要自己防止i越界
                        i += 1
                    else:
                        return {}
                else:
                    compare = False
                    j = 0  # 当前元素匹配错误，则describeList描述句式List指针归0
                    k += 1  # 当前元素匹配错误，则wordanaList词汇数据List指针加1，重新开始匹配
                    i = k
                    break
        # j循环结束到这
        if (j >= len(des_sent_list)):
            # 如果描述句式List已经比较完则返回比较结果
            if (compare):
                print(describe_dict)
                return describe_dict
                print(describe_dict)
            else:
                return {}

    # word_ana_list词汇数据已经循环结束，但是describe描述句式还未结束，则返回不匹配
    while (j < len(des_sent_list)):
        if (re.match(r'opt(.*?)', des_sent_list[j])):
            j += 1
        else:
            return {}
    if (compare):
        print(describe_dict)
        return describe_dict
    else:
        return {}

def fast_scan(js_cla='fast',sxml= None):  # 面向phsen_ana,对所有句子对短小属性做快速、可重复的匹配。已支持@as，@C，@Y，双重变量
    global this_und
    root = sxml  # 添加表达2之外其他描述句式的选择，要送出句式集合节点的上一层
    if not root:
        root = ET.parse(r'/home/ubuntu/DaiMeng/data/xmlData/表达2.xml').getroot()
    this_und = trans_ltp.get_thisund()
    Yf_ele = ['主语','V','状语']

    for ele in Yf_ele:
        this_und.Semdic[ele] = ''
    for js_no in root.iter(js_cla):  # 增加的第一层是分类标签，一般只有0号有效，所以跑一次就可以了
        ss = 0
        for sen in this_und.phsen_ana:
            Yf_str = sen.sen_mean.replace('::', ',').split(',')
            for ele in Yf_ele:
                sen_ele = ''
                for ys in Yf_str:
                    if ys.find(ele + '=') > -1:
                        sen_ele += ',' + ys
                if sen_ele != '':
                    this_und.Semdic[ele] += 'sn=' + str(ss) + sen_ele + '\n'  # 每句scan后写一行
            matrec_dic = {}   #记录每个主题中该句子各词语匹配情况
            for node in js_no.iter('句式'):
                logic_express = node.find('逻辑句式').text
                sem_t = None
                if '主题' in node.attrib:
                    sem_t = node.attrib['主题']
                sen_sem = ''
                for ch_no in node.iter('描述句式'):
                    if '逻辑' in ch_no.attrib:
                        logic_express = ch_no.attrib['逻辑']  # 在特殊情况下，使用单句有效的逻辑句式，用于截胡后边

                    if sem_t != None:
                        if not sem_t in this_und.Semdic:
                            this_und.Semdic[sem_t] = ''
                    des_str = ch_no.text.split(',')
                    as_pars = []  # @as参数组的列表
                    as_par = ['wo', '']  # @as匹配参数的元组
                    if_as = False
                    if ch_no.text.find('@as') > -1:
                        dd = 0
                        for des in des_str:  # 记录装载本次des句式中包含的as变量位置和参数
                            if des[:3] == '@as':
                                if_as = True
                                as_pai = des.split('.')
                                if int(as_pai[1]) == -1:  # 如果是公用的dicexpl_key则单独装载。(-1表示)
                                    d_key = get_d_key()
                                    if as_pai[2] == 'wo':
                                        des_str[dd] = d_key.wo
                                    elif as_pai[2] == 'pos':
                                        des_str[dd] = '@P.' + d_key.pos
                                    elif as_pai[2] == 'syn':
                                        des_str[dd] = d_key.syn.split('+')[0]
                                    elif as_pai[2] == 'cla':
                                        cat_cla = d_key.cla.split('+')[0].split('.')[-1]
                                        cat_cla = re.sub('\d+', '', cat_cla)
                                        cat_cla = re.sub('[=#@]+', '', cat_cla)
                                        des_str[dd] = '@G.in(' + cat_cla[cat_cla.find('_') + 1:] + ')'  # 只取对应目标的第0个分类的最后一截。
                                    # @as变量的1号位置是跟随的des句式元素序号，从0开始；2号位置是跟随的内容（分类，词性或者词本身），dd是本身的位置。
                                else:
                                    as_par = [dd, int(as_pai[1]), as_pai[2]]
                                    as_pars.append(as_par)
                            dd += 1

                    j = 0
                    w = 0
                    dista = 0
                    par_C = ''
                    mat_dic = {}
                    B_C = -1   # @C变量开关
                    last_mat = -1  # 上一个匹配好的w_anas位置
                    while j < len(des_str):  # 以描述句式为基准进行匹配
                        if w > len(sen.w_anas)-1:
                            break

                        mat_this =False
                        mat_des = False

                        s_mat = des_str[j].replace('opt','')
                        if des_str[j].find('@C') > -1:  # 不管@C函数
                            B_C = w
                            if des_str[j].split('.')[1]=='wo':
                                par_C = sen.w_anas[w].wo
                                if j == len(des_str) -1:   # 最后一项 @C全收
                                    ww = w+1
                                    while ww < len(sen.w_anas):
                                        par_C += '+' +sen.w_anas[ww].wo
                                        ww += 1
                                    B_C = -1
                                    last_mat = len(sen.w_anas) - 1
                            j += 1
                            w += 1
                            continue
                        elif des_str[j].find('@Y.') > -1:   # 依存句法的relate匹配
                            for ww in range(w, len(sen.w_anas)):  # 在写@Y变量时要考虑到前后秩序
                                if sen.w_anas[ww].pos == '标点':
                                    break
                                # 由wgr词组判断是否关联 一级直连的放行，因为前边只能是HED
                                if_rel = ('_' + sen.w_anas[ww].wgr + '_').find('_' + sen.w_anas[last_mat].wo + '_') > -1
                                if j == 0:
                                    if_rel = True
                                elif 'HEDCOV'.find(sen.w_anas[ww].yuf) > -1:
                                    if_rel = True
                                # 这里要求前后的两项有语法依存关系，HED关联的那一层关系无效，不能跨越标点使用
                                # print(sen.w_anas[ww].yuf + '++++' + cat_str('@Y.', des_str[j], '+'))
                                if if_rel and sen.w_anas[ww].yuf == cat_str('@Y.', des_str[j]+'+', '+'): # 会漏一个字符
                                    if des_str[j].find('+') == -1:
                                        this_und.phsen_ana[ss].w_anas[w].ele = '+' + des_str[j]
                                    elif element_match(sen.w_anas[ww],des_str[j].split('+')[-1]):
                                        this_und.phsen_ana[ss].w_anas[w].ele = '+' + des_str[j]
                                    else:
                                        continue
                                    matrec_dic[w] = des_str[j]
                                    mat_dic[des_str[j]] = sen.w_anas[ww].wo
                                    mat_this = True
                                    last_mat = ww
                                    break

                            if mat_this:   # @Y变量从这里输出了
                                if j == len(des_str)-1:
                                    t_sem = str(logic_sentence(mat_dic, logic_express)).replace('\'', '')
                                    this_und.phsen_ana[ss].w_anas[last_mat].ele = t_sem  #以此记录匹配上的词语位置

                                    if sen_sem.find(t_sem.split('=')[-1].strip(']')) == -1:
                                        sen_sem += ',' + t_sem
                                    if len(sen.w_anas) - w > len(des_str):  # 后边够长时可以重复匹配
                                        j = 0
                                        w = max(w, last_mat)+1
                                        continue
                                    else:
                                        break
                                else:
                                    j += 1
                                    w = max(w, last_mat)+1
                                    continue
                            else:
                                j = 0
                                w += 1
                                continue

                        if element_match(this_und.phsen_ana[ss].w_anas[w], s_mat):
                            last_mat = w
                            this_und.phsen_ana[ss].w_anas[w].ele = '+' + des_str[j]
                            matrec_dic[w] = des_str[j]
                            mat_dic[des_str[j]] = sen.w_anas[w].wo
                            if if_as:
                                for a_par in as_pars:  # 每一项匹配成功后，查找后边有没有as项追随自己，发现后按各参数执行替换。
                                    if int(a_par[1]) == j:
                                        if a_par[2] == 'v':
                                            des_str[int(a_par[0])] = des_sent_list[j]
                                        elif a_par[2] == 'wo':
                                            des_str[int(a_par[0])] = sen.w_anas[w].wo
                                        elif a_par[2] == 'pos':
                                            des_str[int(a_par[0])] = '@P.' + sen.w_anas[w].pos
                                        elif a_par[2] == 'cla':
                                            des_str[int(a_par[0])] = '@G.in' + sen.w_anas[w].cla   # if_as复原.cla
                            if B_C > -1:
                                mat_dic[des_str[j - 1]] = par_C
                                B_C = -1
                            if j == len(des_str) - 1:
                                mat_des = True
                            else:
                                dista = 1
                                j += 1
                                w += 1
                                continue
                        elif B_C > -1:
                            par_C += '+' + sen.w_anas[w].wo

                            w += 1
                            continue
                        elif des_str[j].find('opt') > -1:
                            j += 1
                            continue
                        elif dista > 0 and '助词副词形容词数词'.find(sen.w_anas[w].pos) > -1:
                            dista += -1
                            w += 1
                            continue
                        elif len(sen.w_anas) - w > len(des_str):   # 后边够长时可以也重复匹配
                            if if_as:
                                des_str = ch_no.text.split(',')   # if_as复原
                            mat_dic[des_str[j]] = ''
                            j = 0
                            w += 1
                            continue
                        elif not mat_des:
                            break
                        if mat_des:
                            if if_as:
                                des_str = des_str = ch_no.text.split(',')  # if_as复原
                            # 每句在字典栏目中加写一行
                            t_sem = str(logic_sentence(mat_dic, logic_express)).replace('\'', '')
                            if this_und.phsen_ana[ss].w_anas[last_mat].ele == None:
                                this_und.phsen_ana[ss].w_anas[last_mat].ele = t_sem
                            else:
                                this_und.phsen_ana[ss].w_anas[last_mat].ele += '\n' + t_sem

                            if sen_sem.find(t_sem.split('=')[-1]) == -1:
                                sen_sem += ',' + t_sem
                            if len(sen.w_anas) - w > len(des_str):  # 后边够长时可以重复匹配
                                j = 0
                                w += 1
                                continue
                            else:
                                break
                if sen_sem != '':
                    this_und.Semdic[sem_t] += 'sn=' + str(ss) + sen_sem + '\n'
                    if sen_sem.find('发送信息=') > -1:
                        if sen.sen_in[-1] != '”':
                            sss = ss + 1
                            while sss < len(this_und.phsen_ana):
                                this_und.Semdic[sem_t] += 'sn=' + str(sss) + ',信息={' + this_und.phsen_ana[sss].sen_in.replace(' ','+')+'\n'
                                sss += 1
                                if this_und.phsen_ana[sss].sen_in[-1] == '”':
                                    break
            ss += 1
        ele_sts(this_und.Semdic)

        break
    this_und.rec[0] = trans_ltp.input_a
    this_und.rec[1] = trans_ltp.thinking_str
    trans_ltp.set_thisund(ph=this_und)
    return this_und

def ele_sts(Sem_dic = None):
    if this_und.Semdic == {}:
        return Sem_dic
    del_key = []
    sts_dic = {}
    for key in Sem_dic:  # 使用一个副本，其实和this_und.semdic是一回事，不能循环中加减key
        if Sem_dic[key] == '' or len(Sem_dic[key]) < 3:
            del_key.append(key)  # 不能在循环中直接删除字典，须循环后操作
            continue
        Tc_dic = {}
        cla_dic ={}
        n_zy = 0  # 各语义值出现次数
        eles = Sem_dic[key].replace('\n', ',').split(',')

        for e in eles:  # 数数各元素，建个字典
            se = e.split('=')
            if len(se) < 2:
                continue
            if se[0].find(key) > -1 or (key.find(se[0].strip('[')) > -1):
                elev = re.sub('[\]【]', '', se[1])
                len_id = min(2,len(elev) - 1)
                if elev in trans_ltp.env_ws[len_id]:
                    e_a = trans_ltp.envw_ana[len_id][env_ws[len_id].index(elev)]
                    cla = e_a.cla.split('+')[0].split('.')
                    si = max(0,len(cla)-3)   # 准备从后边取三项
                    for cc in range(si,len(cla)):
                        if ('cla.' + cla[cc]) not in Tc_dic:
                            cla_dic['cla.' + cla[cc]] = 1
                        else:
                            cla_dic['cla.' + cla[cc]] += 1
                if elev not in Tc_dic:
                    Tc_dic[elev] = 1
                else:
                    Tc_dic[elev] += 1
                n_zy += 1

            sts_dic[key + '+统计'] =  Tc_dic

    for d_k in del_key:
        del this_und.Semdic[d_k]
    this_und.Stsdic = sts_dic  # 出了循环才能操作
    return Sem_dic

def Ds_scan( text=''):
    global this_und
    this_und = structure.ph_und(phsen_ana=trans_ltp.get_phsen())

    C_dic = structure.conj_dic
    l_dp = []
    for key in C_dic:
        if not key in l_dp:
            l_dp.append(key)
        ss = 0
        for sen in this_und.phsen_ana:
            dap_str = C_dic[key].split(',')
            for lc_p in dap_str:         # 这里就是连词搭配了
                lcs = lc_p.split('_')
                cc = 0
                w = 0
                c_mat =False
                C_wos = []
                cat_ind = -1
                cat_s = ''  # 捕捉连词之间的内容
                while cc < len(lcs):
                    if w == len(sen.w_anas)-1:
                        break
                    if '连词副词'.find(sen.w_anas[w].pos) == -1:   # 主要是连词，副词数词也可能，但数词后边不能跟量词。
                        w += 1
                        continue
                    elif sen.w_anas[w].pos == '数词' and sen.w_anas[w].pos ==量词:
                        w += 1
                        continue

                    if(re.match(re.compile(r'((' + lcs[cc] + ')+)'), sen.w_anas[w].wo)):
                        cat_ind += 1
                        if cat_ind > 0:
                            C_wos.append(key + '=' + cat_s)
                            cat_s = ''
                        if cc == len(lcs) -1:
                            c_mat = True
                            ww = w + 1
                            while ww < len(sen.w_anas)-1:
                                cat_s += '+' + sen.w_anas[ww].wo
                                ww += 1
                                if sen.w_anas[ww].pos == '标点':
                                    break
                            C_wos.append(key + '=' + cat_s)
                            break
                        elif w < len(sen.w_anas)-1:
                            cc += 1
                            w += 1
                            continue
                        else:break

                    if cat_ind > -1:
                        cat_s += sen.w_anas[w].wo

                    w += 1
                    if w > len(sen.w_anas)-1:
                        break
                if c_mat:
                    this_und.Semdic[key] = 'sn=' + str(ss) + ',' + str(C_wos)
                    trans_ltp.thinking_str += '语句关联=' + str(C_wos) + '\n'
                    # print(this_und.Semdic[key])
                    break
            ss += 1
    trans_ltp.set_thisund(ph=this_und)
    return this_und

# 输入句子与描述句式一般匹配，要求输入句子有元素能顺序（中间可以有不对应元素）对应描述句式各元素即可
def sentence_normal_match(word_ana_list, des_sent):
    # 描述句式list与词汇数据list全部匹配则返回字典describe_dict（描述句式元素: 词汇数据元素）
    global d_key
    des_sent_list = re.split(r'\,', des_sent)
    describe_dict = collections.OrderedDict()
    # 去除describe_sentence_list中带opt的元素
    C_pars = []  # @C参数组的列表
    C_par = [0, 'wo', '']  # @C匹配参数的元组
    if_C = False
    ii = 0
    while ii < len(des_sent_list):
        if re.match(r'opt(.*?)', des_sent_list[ii]):
            del des_sent_list[ii]
        else:
            ii += 1
    i = 0  # 控制describe_sentence_list描述句式List循环
    j = 0  # 控制word_ana_list词汇数据List循环
    while i < len(des_sent_list):
        if des_sent_list[i][:2] == '@C':
            if_C = True
            C_par = [i, des_sent_list[i].split('.')[1], '']  # 装在@C参数,分别为@C项位置，@C项type，@C项内容（由type）决定。
            # print(C_par)
            C_pars.append(C_par)
            i += 1
            continue
        while j < len(word_ana_list):
            describe_str = des_sent_list[i]
            if (element_match(word_ana_list[j], describe_str)):
                describe_dict[des_sent_list[i]] = word_ana_list[j].wo
                if if_C:
                    if_C = False
                    describe_dict[des_sent_list[i - 1]] = C_pars[-1][2]  # 上一个Cat变量捕捉完毕，加入字典
                i += 1
                j += 1
                break
            elif if_C:
                # 捕捉@C函数的内容
                if C_pars[-1][1] == 'wo':  # 装载什么内容
                    C_pars[-1][2] += (word_ana_list[j].wo + '+')
                j += 1
            else:
                j += 1
        if j == len(word_ana_list):
            break
    # 描述句式所有元素均衡匹配上则返回dict有效，否则没有匹配成功
    if i == len(des_sent_list):
        # print(describe_dict)
        return describe_dict
    else:
        return {}


def logic_sentence(describe_dict,logic_express):
    '''
    生成逻辑句式，替换$$=后的内容
    :param describe_dict: 描述句式字典
    :param logic_list: 逻辑句式列表
    :return: 返回替换$$=后的逻辑句式列表
    '''

    replaced_logic_list = []
    # print(logic_list)
    logic_list = re.split(r'\,',logic_express)
    for logic_element in logic_list:
        if (re.match(r'(.*?)\$\$=(.*?)', logic_element)):
            replace_str = re.findall(r'\$\$=(.+)', logic_element)  # 找到$$=后面的字符串
            if (replace_str[0] in describe_dict.keys()):
                temp_str = logic_element.replace(replace_str[0], describe_dict[replace_str[0]]).replace('$$=', '')
            else:
                temp_str = ''  # logic_element.replace(replace_str[0], '无').replace('$$=', '')
        else:
            temp_str = logic_element
        if temp_str != '':
            if len(temp_str.split('=')) < 2 and len(replaced_logic_list) > 0:  # 没有等号表示与前边同一个标识
                replaced_logic_list[-1] += '+' + temp_str
            else:
                replaced_logic_list.append(temp_str)
    return replaced_logic_list

def sentence_match_result(word_ana_list, js_cla='input'):  # 参数一为词语信息列表，增加了参数2是句式的分类，查字典和阅读分开，以后也许还有单字句型（词组）等
    # 找到表达2.xml的路径
    if platform.system() == 'Windows':
        dir = path.dirname(__file__)
        parent_path = path.dirname(dir)
    else:
        parent_path = ('/home/ubuntu/Daimeng')
        # pwd = os.getcwd()
        # parent_path = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
    tree = ET.parse(r'/home/ubuntu/DaiMeng/data/xmlData/表达2.xml')
    root = tree.getroot()
    sentence_list = []

    if len(word_ana_list) > 1:
        if word_ana_list[1].wo == ':':  # 第二个字符为：，是字典送过来的标志
            js_cla = '字典'


    for js_cla in root.iter(js_cla):  # 增加的第一层是分类标签，一般只有0号有效，所以跑一次就可以了

        for node in js_cla.iter('句式'):
            for childnode in node.iter('描述句式'):
                if (childnode.text):
                    describe_sentence = childnode.text
                    # 根据描述句式的标签判断是一般匹配还是严格匹配
                    if '匹配' in childnode.attrib:
                        if childnode.attrib['匹配'] == '一般':
                            describe_dict = sentence_normal_match(word_ana_list, describe_sentence)
                    # print(describe_dict)
                    else:
                        describe_dict = sentence_strict_match(word_ana_list, describe_sentence)

                    if (describe_dict):
                        sentence_list.append(describe_dict)
                        logic_express = node.find('逻辑句式').text
                        if '逻辑' in childnode.attrib:
                            logic_express = childnode.attrib['逻辑']  # 在特殊情况下，使用单句有效的逻辑句式，用于截胡后边的逻辑句式
                        sentence_list.append(logic_sentence(describe_dict,logic_express))
                        trans_ltp.thinking_str += '整句细读' + str(logic_sentence(describe_dict,logic_express))
                        return sentence_list  # 只要第一项
        return sentence_list  # 当前故意只跑第一项


# 根据单句逻辑语义生成经验语义
def experience_mean_result(sen_anaa):
    # 找到xml的路径
    if platform.system() == 'Windows':
        dir = path.dirname(__file__)
        parent_path = path.dirname(dir)
    else:
        parent_path = ('/home/ubuntu/Daimeng')
    tree = ET.parse(r'/home/ubuntu/DaiMeng/data/xmlData/通用经验.xml')
    root = tree.getroot()
    exp_mean = ''  # 待返回的经验语义
    for node in root.iter('jy'):
        if (node.text):
            experience = node.text  # 读每一条<jy>
            exp_list = re.split(r'[|]', experience)  # |分隔符分隔，前半部分需匹配逻辑语义，后半部分为经验语义
            exp_pre = ''
            if (exp_list):
                exp_pre = exp_list[0]
            else:
                continue
            exp_pre_lst = re.split(r';', exp_pre)
            if (sen_mean_match(exp_pre_lst, sen_anaa.sen_mean)):
                exp_mean = experience
                # 补上经验内容
                exp_mean = exp_mean + ',经验内容=' + parent_node(exp_mean)
                trans_ltp.thinking_str += '基本常识=' + exp_mean + '\n'
                break
    return exp_mean

# 根据单句逻辑语义与通用经验元素列表进行匹配
def sen_mean_match(exp_pre_lst, sen_mean):
    i = 0
    for exp_pre_element in exp_pre_lst:
        # 匹配主语
        if (re.search('主语', exp_pre_element)):
            result = re.search('.*?主语=(.*?)[,;].*?', exp_pre_element)  # 找出经验语句中主语
            if (not result):
                result = re.search('.*?主语=(.*)', exp_pre_element)  # 找出经验语句中主语
            sen_mean_zhuyu = re.search('.*?主语=(.*?)[,:].*?', sen_mean)  # 找出逻辑语义串中主语

            # 主语能匹配上，则继续循环匹配其他元素
            if (result and sen_mean_zhuyu):
                if (re.search(result.group(1), sen_mean_zhuyu.group(1))):
                    i += 1
                    continue

        # 匹配谓语
        elif (re.search('V', exp_pre_element)):
            result = re.search('.*?V=(.*?)[,;].*?', exp_pre_element)  # 找出经验语句中谓语
            if (not result):
                result = re.search('.*?V=(.*)', exp_pre_element)  # 找出经验语句中谓语
            sen_mean_v = re.search('.*?V=(.*?)[,:].*?', sen_mean)  # 找出逻辑语义串中谓语

            # 谓语能匹配上，则继续循环匹配其他元素
            if (result and sen_mean_v):
                if (result.group(1) == sen_mean_v.group(1)):
                    i += 1
                    continue

        # 宽松匹配=号后面的元素
        if (normal_match(exp_pre_element, sen_mean)):
            i += 1

    # 所有;分割的元素都匹配成功
    if (i == len(exp_pre_lst)):
        return True
    return False


# 按=后面内容一般匹配
def normal_match(exp_pre_element, sen_mean):
    exp_element__list = re.split(',', exp_pre_element)  # 通用经验按,分割成列表元素
    sen_mean_list = re.split(r'[,::\+]', sen_mean)  # 逻辑语义按,:+分割成列表元素
    for exp_element in exp_element__list:

        if exp_element == '':
            continue
        elif exp_element == None:
            continue
        exp_element_equal = re.search('.*?=(.*)', exp_element)
        # 如果匹配元素存在+，则要分隔后再匹配

        if (re.search(r'\+', exp_element_equal.group(1))):
            exp_element_equal_list = re.split(r'\+', exp_element_equal.group(1))
            # print(exp_element_equal_list)
            i = 0
            for exp_element_equal_elem in exp_element_equal_list:
                for sen_mean_elem in sen_mean_list:
                    sen_mean_elem_equal = re.search('.*?=(.*)', sen_mean_elem)
                    if (sen_mean_elem_equal):
                        if (sen_mean_elem_equal.group(1) == exp_element_equal_elem):
                            i += 1
                    else:
                        sen_mean_elem_equal = sen_mean_elem
                        if (sen_mean_elem_equal):
                            if (sen_mean_elem_equal == exp_element_equal_elem):
                                i += 1
            if (i == len(exp_element_equal_list)):
                return True
        else:
            for sen_mean_elem in sen_mean_list:
                sen_mean_elem_equal = re.search('.*?=(.*)', sen_mean_elem)
                if (sen_mean_elem_equal):
                    if (exp_element_equal.group(1) == sen_mean_elem_equal.group(1)):
                        return True
    return False


# 根据匹配到的通用经验寻找父标签
def parent_node(str):
    if platform.system() == 'Windows':
        dir = path.dirname(__file__)
        parent_path = path.dirname(dir)
    else:
        parent_path = ('/home/ubuntu/Daimeng')
    selector = etree.parse(r'/home/ubuntu/DaiMeng/data/xmlData/通用经验.xml')
    parent_node = selector.xpath("//*[jy = '%s']" % str)
    return parent_node[0].tag







if __name__ == '__main__':
    w1 = WordAnanysis('包括', '动词', '鸟类')
    w2 = WordAnanysis('中朝', '名词', '国家')
    word_ana_list = [w1, w2, w3, w4, w5, w6, w7, w8]
    sentence_match_result(word_ana_list)
