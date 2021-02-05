# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import xml.etree.ElementTree as ET
from business.sentenceMatch3 import *
import json
from business.trans_ltp import *
from business.structure import *
import re
import collections
import random
import business.phframe_ana as phframe_ana
g_dic={}

def auto_express(logic_str, logic_lst):
    """
    根据逻辑串以及传入的参数，按照structure模块exp_dic字典随机生成的对话语句
    :param logic_str: 传入的逻辑串，例如触景生情，寓情于景等
    :param logic_lst: 传入的参数列表，例如见到XX景色，想起XX情感等
    :return: 返回按照structure模块exp_dic中随机生成的对话语句
    """
    if(logic_str not in Exp_dic.keys()):
        return ''
    express_lst = Exp_dic[logic_str].split('+')
    rand = random.randint(0, len(express_lst) - 1)
    #print('rand:'+str(rand))
    express = express_lst[rand]
    i = 0
    for logic in logic_lst:
        s_str = '@S'+str(i)
        if(s_str in express):
            express = express.replace(s_str,logic)
        i += 1
    return express

def scan_poem(input_str):
    """
    根据输入内容在概念.我.xml中扫描古诗
    :param input_str: 输入内容
    :return: 返回古诗信息字典
    """
    poem_dic={}
    tree = ET.parse(r'/home/ubuntu/DaiMeng/data/xmlData/概念.我.xml')
    root = tree.getroot()
    for me in root:
        node = me.find('我的古诗')
        for poem_node in node:
            if(poem_node.attrib['标题']==input_str or (input_str in poem_node.attrib['原文'])):
                poem_dic['标题'] = poem_node.attrib['标题']
                poem_dic['作者'] = poem_node.attrib['作者']
                poem_dic['原文'] = poem_node.attrib['原文']
                poem_dic['主题'] = poem_node.attrib['主题']
                poem_dic['译文'] = poem_node.text
                break
    return poem_dic

# 认知判断
def cognize_estimate(sen_ana, sub_sen=''):
    """
    判断单句、子句的认知信息
    :param sen_ana: 单句语义字典队列对象
    :param sub_sen: 子句
    :return: 返回认知判断信息字符串
    """
    cognize_dic = {'感知':'', '动作':'', '思维':''}
    cognize_perception = ['自然现象','星体']
    cognize_action = ['动作','发生','交通旅行']
    cognize_thinking = ['心理','情感活动']
    for w_ana in sen_ana.w_anas:
        #print(w_ana.wo+': '+w_ana.cla)
        if(len(sub_sen)>0):
            if(w_ana.wo not in sub_sen):
                continue
        if(len([x for x in cognize_perception if x in w_ana.cla])):
            cognize_dic['感知'] += '感知.' + w_ana.wo + '+'
        if (len([x for x in cognize_action if x in w_ana.cla])):
            cognize_dic['动作'] += '动作.' + w_ana.wo + '+'
        if (len([x for x in cognize_thinking if x in w_ana.cla])):
            cognize_dic['思维'] += '思维.' + w_ana.wo + '+'
    # 认知优先级思维>感知>动作
    if(cognize_dic['思维']):
        cognize_str = cognize_dic['思维'][:-1]
    elif(cognize_dic['感知']):
        cognize_str = cognize_dic['感知'][:-1]
    elif(cognize_dic['动作']):
        cognize_str = cognize_dic['动作'][:-1]
    else:
        cognize_str = ''
    # print('cognize_str'+cognize_str)
    # try:
    #     cognize_str = max(cognize_dic, key=cognize_dic.get) # 找出字典中值最大的键
    # except Exception:
    #     cognize_str = ''
    # print(cognize_dic)
    return cognize_str


# 逻辑判断
def logic_estimate(sen_ana, sub_sen='', cognize_str='', subsenana_lst = [], sn=0):
    """
    判断单句、子句的认知信息
    :param sen_ana: 单句语义字典队列对象
    :param sub_sen: 子句
    :cognize_str: 单句认知串
    :subsenana_lst：子句句法分析
    :sn：单句是段落中的编号
    :return: 返回逻辑判断信息字符串
    """
    logic_str = ''
    # print(cognize_str)
    # print(subsenana_lst)
    # 逻辑优先级，触景生情>逻辑关系。如果句子中有感知+思维则是触景生情，没有则再考虑连词关系
    if(len(cognize_str)>0 and ('感知' in cognize_str) and ('思维' in cognize_str)):
        cognize_split_lst = cognize_str.split('+')
        # 先根据感知和思维单词找动宾关系，如果能找到则返回逻辑关系
        for subsenana in subsenana_lst:
            sub_sen_ana_str = subsenana['句式']['主语+V+宾语'][subsenana['句式']['主语+V+宾语'].find('+')+1:]
            # print(sub_sen_ana_str)
            if('null' in sub_sen_ana_str):
                continue
            for cognize in cognize_split_lst:
                if('感知' not in cognize):
                    continue
                cog_tmp_str = cognize.replace('感知.','')
                # print(cog_tmp_str)
                if(cog_tmp_str in sub_sen_ana_str):
                    logic_str = logic_str + '感知.'+ sub_sen_ana_str.replace('+','') + '+'
        for subsenana in subsenana_lst:
            sub_sen_ana_str = subsenana['句式']['主语+V+宾语'][subsenana['句式']['主语+V+宾语'].find('+')+1:]
            if('null' in sub_sen_ana_str):
                continue
            for cognize in cognize_split_lst:
                if('思维' not in cognize):
                    continue
                cog_tmp_str = cognize.replace('思维.', '')
                if(cog_tmp_str in sub_sen_ana_str):
                    logic_str = logic_str + '思维.' + sub_sen_ana_str.replace('+','') + '+'
        if('感知' in logic_str and  '思维' in logic_str ):
            logic_str = logic_str[:-1]
            logic_str = logic_str.replace('+思维.','@').replace('感知.','、').replace('思维.','、')
            if(logic_str[0]=='、'):
                logic_str = logic_str[1:]
            logic_lst = logic_str.split('@')
            sen_str = sen_ana.sen_in.replace(' ','')
            if(sen_str.find(logic_lst[0][0])>0 and sen_str[sen_str.find(logic_lst[0][0])-1]=='不'):
                logic_lst[0] = '不' + logic_lst[0]
            if (sen_str.find(logic_lst[1][0]) > 0 and sen_str[sen_str.find(logic_lst[1][0]) - 1] == '不'):
                logic_lst[1] = '不' + logic_lst[1]
            express_str = auto_express('触景生情',logic_lst)
            logic_str = '触景生情：' + express_str
            trans_ltp.thinking_str += '小呆陷入沉思:' + '发现触景生情逻辑，' + express_str + '\n'
            #trans_ltp.thinking_str += '小呆陷入沉思:' + '发现触景生情逻辑，' + logic_str.replace('感知.','由').replace('思维.','到').replace('+','') + '\n'
            #logic_str = '触景生情：' + logic_str.replace('感知.','由').replace('思维.','到').replace('+','')
            return logic_str

        # 没有找到动宾关系，则罗列出感知、思维作为逻辑关系
        cognize_lst = [i for i,x in enumerate(cognize_split_lst) if ('感知' in str(x))]
        think_lst = [i for i,x in enumerate(cognize_split_lst) if ('思维' in str(x))]
        cog_lst = cognize_lst
        thk_lst = think_lst
        new_cog_lst = []
        new_thk_lst = []
        sign = True
        for cog in cog_lst:
            for thk in thk_lst:
                if(thk < cog):
                    sign = True
                    continue
                if(cog not in new_cog_lst and sign==True):
                    new_cog_lst.append(cog)
                    sign = False
                    i = thk_lst.index(thk)
                    j = 0
                    while(j<i):
                        thk_lst.pop(j)
                        j += 1
                    break
        cog_lst = cognize_lst
        thk_lst = think_lst
        sign = True
        for thk in thk_lst:
            for cog in cog_lst:
                if(thk >cog):
                    sign = True
                    continue
                if(thk not in new_thk_lst and sign==True):
                    new_thk_lst.append(thk)
                    sign = False
                    i = cog_lst.index(cog)
                    j = 0
                    while (j < i):
                        cog_lst.pop(j)
                        j += 1
                    break
        cog_lst = cognize_lst
        thk_lst = think_lst
        if(thk_lst[-1]>cog_lst[-1]):
            for thk in thk_lst:
                if(thk>cog_lst[-1]):
                    new_thk_lst.append(thk)
                    break
        else:
            for cog in cog_lst:
                if(cog>thk_lst[-1]):
                    new_cog_lst.append(cog)
                    break
        # new_cog_lst为合并后得认知索引，new_thk_lst为合并后的思维索引
        # 例如认知索引为1，3，9，10；思维索引为5，7，11；则认知索引合并为1，9；思维索引合并为5，11
        # print(new_cog_lst)
        # print(new_thk_lst)
        for i,x in enumerate(new_cog_lst):
            xx = x
            yy = new_thk_lst[i]
            while(xx<yy):
                if('感知' in cognize_split_lst[xx]):
                    logic_str = cognize_split_lst[xx] + '+'
                xx += 1
            if(i+1 >= len(new_cog_lst)):
                while(yy<len(cognize_split_lst)):
                    if('思维' in cognize_split_lst[yy]):
                        logic_str = logic_str + cognize_split_lst[yy] + '+'
                    yy += 1
            else:
                while(yy<new_cog_lst[i+1]):
                    if('思维' in cognize_split_lst[yy]):
                        logic_str = logic_str + cognize_split_lst[yy] + '+'
                    yy += 1
        if('感知' not in logic_str):
            tmp_cog = ''
            for cognize_str in cognize_split_lst:
                if('感知' in cognize_str):
                    tmp_cog += cognize_str + '+'
            logic_str = logic_str.replace('+','、').replace('思维.','')
            tmp_cog = tmp_cog.replace('+','、').replace('感知.','')
            if(logic_str[-1]=='、'):
                logic_str = logic_str[:-1]
            if (tmp_cog[-1] == '、'):
                tmp_cog = tmp_cog[:-1]
            logic_lst = []
            if(g_dic.__contains__('主语+V+宾语')):
                zwb_lst = g_dic['主语+V+宾语'].split('\n')
                for zwb in zwb_lst:
                    if('sn='+str(sn) in zwb):
                        for r_str in zwb.split(','):
                            for logic_tmp_str in logic_str.split('、'):
                                if(logic_tmp_str in r_str):
                                    logic_str = r_str[r_str.find('=')+1:-1].replace('+','')
                                    break
                            for tmp_cog_str in tmp_cog.split('、'):
                                if (tmp_cog_str in r_str):
                                    tmp_cog = r_str[r_str.find('=') + 1:-1].replace('+', '')
                                    break
            sen_str = sen_ana.sen_in.replace(' ', '')
            if (sen_str.find(logic_str[0]) > 0 and sen_str[sen_str.find(logic_str[0]) - 1] == '不'):
                logic_str = '不' + logic_str
            if (sen_str.find(tmp_cog[0]) > 0 and sen_str[sen_str.find(tmp_cog[0]) - 1] == '不'):
                tmp_cog = '不' + tmp_cog
            logic_lst.append(logic_str)
            logic_lst.append(tmp_cog)
            express_str = auto_express('寓情于景', logic_lst)
            trans_ltp.thinking_str += '小呆陷入沉思:' + '发现寓情于景逻辑，' + express_str + '\n'
            logic_str = '寓情于景：' + express_str
            #trans_ltp.thinking_str += '小呆陷入沉思:' + '发现寓情于景逻辑，将' + logic_str+'情感融入到'+tmp_cog+ '中\n'
            #logic_str = '寓情于景：将'+ logic_str+'情感融入到'+tmp_cog+ '中'
            return logic_str
        if (logic_str[-1] == '+'):
            logic_str = logic_str[:-1]
        logic_str = logic_str.replace('+思维.', '@').replace('感知.', '、').replace('思维.', '、')
        if (logic_str[0] == '、'):
            logic_str = logic_str[1:]
        logic_lst = logic_str.split('@')
        logic_str = ''
        tmp_cog = ''
        if(logic_lst[0]):
            logic_str = logic_lst[0]
        if(logic_lst[1]):
            tmp_cog = logic_lst[1]
        if (g_dic.__contains__('主语+V+宾语')):
            zwb_lst = g_dic['主语+V+宾语'].split('\n')
            for zwb in zwb_lst:
                if ('sn=' + str(sn) in zwb):
                    for r_str in zwb.split(','):
                        for logic_tmp_str in logic_str.split('、'):
                            if (logic_tmp_str in r_str):
                                logic_str = r_str[r_str.find('=') + 1:-1].replace('+', '')
                                break
                        for tmp_cog_str in tmp_cog.split('、'):
                            if (tmp_cog_str in r_str):
                                tmp_cog = r_str[r_str.find('=') + 1:-1].replace('+', '')
                                break
        logic_lst = []
        sen_str = sen_ana.sen_in.replace(' ', '')
        if (sen_str.find(logic_str[0]) > 0 and sen_str[sen_str.find(logic_str[0]) - 1] == '不'):
            logic_str = '不' + logic_str
        if (sen_str.find(tmp_cog[0]) > 0 and sen_str[sen_str.find(tmp_cog[0]) - 1] == '不'):
            tmp_cog = '不' + tmp_cog
        logic_lst.append(logic_str)
        logic_lst.append(tmp_cog)
        express_str = auto_express('触景生情', logic_lst)
        logic_str = '触景生情：' + express_str
        trans_ltp.thinking_str += '小呆陷入沉思:' + '发现触景生情逻辑，' + express_str + '\n'
        #trans_ltp.thinking_str += '小呆陷入沉思:' + '发现触景生情逻辑，由' + logic_str.replace('感知.','').replace('思维.','到').replace('+','') + '\n'
        #logic_str = '触景生情：由' + logic_str.replace('感知.','').replace('思维.','到').replace('+','')
        return logic_str

    # 如果没有找到感知+思维则考虑连词关系
    logic_dic = {'陈述':0,'并列':0,'选择':0,'转折':0,'原因':0,'结果':0,'条件':0,'推论':0,'假设':0,'让步':0,'目的':0,'总括':0,'比喻':0}
    logic_parataxis=['一边','一会儿','既','又','又','一面','有时'] # 并列
    logic_selection=['是','还是','要么','或者','与其','不如'] # 选择
    logic_progressive=['况且','并且','反而','而且'] # 递进
    logic_adversative=['但是','却','然而','不过'] # 转折
    logic_causa=['因为','既然','由于'] # 原因
    logic_result=['因此','以致','所以','不由得'] # 结果
    logic_conditional=['只要','除非','只有','无论','不论','不管','任凭'] # 条件
    logic_inferential=['才','则','就'] # 推论
    logic_hypothetical =['如果','要是','即便','即使','倘若','要是'] # 假设
    logic_concession=['纵使','哪怕','宁可'] # 让步
    logic_target=['为了','以便'] # 目的
    logic_omnibus=['总而言之','总之'] # 总括
    logic_metaphor=['像','就像','好像','好似','仿佛','如同','好比'] # 比喻
    for w_ana in sen_ana.w_anas:
        # print(w_ana.wo+': ')
        if(len(sub_sen)>0):
            if(w_ana.wo not in sub_sen):
                continue
        if(len([x for x in logic_parataxis if x in w_ana.wo])):
            logic_dic['并列'] += 1
        if (len([x for x in logic_selection if x in w_ana.wo])):
            logic_dic['选择'] += 1
        if (len([x for x in logic_progressive if x in w_ana.wo])):
            logic_dic['递进'] += 1
        if (len([x for x in logic_adversative if x in w_ana.wo])):
            logic_dic['转折'] += 1
        if (len([x for x in logic_causa if x in w_ana.wo])):
            logic_dic['原因'] += 1
        if (len([x for x in logic_result if x in w_ana.wo])):
            logic_dic['结果'] += 1
        if (len([x for x in logic_conditional if x in w_ana.wo])):
            logic_dic['条件'] += 1
        if (len([x for x in logic_inferential if x in w_ana.wo])):
            logic_dic['推论'] += 1
        if (len([x for x in logic_hypothetical if x in w_ana.wo])):
            logic_dic['假设'] += 1
        if (len([x for x in logic_concession if x in w_ana.wo])):
            logic_dic['让步'] += 1
        if (len([x for x in logic_target if x in w_ana.wo])):
            logic_dic['目的'] += 1
        if (len([x for x in logic_omnibus if x in w_ana.wo])):
            logic_dic['总括'] += 1
        if (len([x for x in logic_metaphor if x == w_ana.wo])):
            logic_dic['比喻'] += 1
    # 如果时比喻句，则找出比喻关系
    metaphor_str = ''
    if(sub_sen=='' and logic_dic['比喻']>0 ):
        if(g_dic.__contains__('比喻')):
            metaphor_str = g_dic['比喻']
        metaphor_lst = metaphor_str.split('\n')
        ontology = '' # 本体
        vehicle = '' # 喻体
        zwb_lst = [] # 比喻句中的主谓宾字符串，从g_dic中读出
        if (g_dic.__contains__('主语+V+宾语')):
            zwb_lst = g_dic['主语+V+宾语'].split('\n')
        for metaphor in metaphor_lst:
            if(not metaphor):
                continue
            if(metaphor[metaphor.find('本体=')+3:metaphor.find(']')] in sen_ana.sen_in and
                    metaphor[metaphor.find('喻体=')+3:metaphor.find(']',metaphor.find('喻体='))] in sen_ana.sen_in):
                ontology = metaphor[metaphor.find('本体=')+3:metaphor.find(']')]
                vehicle = metaphor[metaphor.find('喻体=')+3:metaphor.find(']',metaphor.find('喻体='))]
        if(len(ontology)>0 and len(vehicle)>0):
            if(len(zwb_lst)>0):
                for zwb in zwb_lst:
                    if ('sn=' + str(sn) in zwb):
                        for r_str in zwb.split(','):
                            if (ontology in r_str):
                                ontology = r_str[r_str.find('=') + 1:-1].replace('+', '')
                            if (vehicle in r_str):
                                vehicle = r_str[r_str.find('=') + 1:-1].replace('+', '')

            if(ontology == vehicle):
                trans_ltp.thinking_str += '小呆陷入沉思:' + '发现比喻句式，' + ontology + '\n'
                logic_str = '比喻：' + ontology
            else:
                logic_lst=[]
                logic_lst.append(ontology)
                logic_lst.append(vehicle)
                print('logic**********',logic_lst)
                express_str = auto_express('比喻', logic_lst)
                trans_ltp.thinking_str += '小呆陷入沉思:' + '发现比喻句式，' + express_str +'\n'
                logic_str = '比喻：' + express_str
        else:
            # ontology = ''
            # vehicle = ''
            key_words = [x for x in logic_metaphor if x in sen_ana.sen_in][0]
            metaphor_lst = re.split('[,:]',sen_ana.sen_mean)
            metaphor_lst = [x for x in metaphor_lst if x != '']
            sign = False
            for metaphor in reversed(metaphor_lst):
                if(key_words in metaphor):
                    sign = True
                if('主语=' in metaphor and sign):
                    ontology = metaphor.replace('主语=','').replace('+','')
                    break
            sign = False
            for metaphor in metaphor_lst:
                if (key_words in metaphor):
                    sign = True
                if ('主语=' in metaphor and sign):
                    vehicle = metaphor.replace('主语=', '').replace('+', '')
                    break
            if(vehicle==''):
                sign = False
                for metaphor in metaphor_lst:
                    if (key_words in metaphor):
                        sign = True
                    if ('宾语=' in metaphor and sign):
                        vehicle = metaphor[metaphor.find('宾语=')+3:].replace('+', '')
                        break
            if (vehicle == ''):
                sign = False
                for metaphor in metaphor_lst:
                    if (key_words in metaphor):
                        sign = True
                    if ('介宾=' in metaphor and sign):
                        vehicle = metaphor.replace('介宾=', '').replace('+', '')
                        break
            if(len(ontology)>0 and len(vehicle)>0):
                if (len(zwb_lst)>0):
                    for zwb in zwb_lst:
                        if ('sn=' + str(sn) in zwb):
                            for r_str in zwb.split(','):
                                if (ontology in r_str):
                                    ontology = r_str[r_str.find('=') + 1:-1].replace('+', '')
                                if (vehicle in r_str):
                                    vehicle = r_str[r_str.find('=') + 1:-1].replace('+', '')
                if(ontology==vehicle):
                    trans_ltp.thinking_str += '小呆陷入沉思:' + '发现比喻句式，' + ontology + '\n'
                    logic_str = '比喻：' + ontology
                else:
                    logic_lst = []
                    logic_lst.append(ontology)
                    logic_lst.append(vehicle)
                    print('logic**************111',logic_lst)
                    express_str = auto_express('比喻', logic_lst)
                    trans_ltp.thinking_str += '小呆陷入沉思:' + '发现比喻句式，' + express_str + '\n'
                    logic_str = '比喻：' + express_str
            elif(len(vehicle)>0):
                if(g_dic.__contains__('主语')):
                    subject_str = g_dic['主语']
                    subject_lst = subject_str.split('\n')
                    subject_lst = [x for x in subject_lst if x!='']
                    num = sn - 1
                    for subject_sub in subject_lst:
                        if(num<0):
                            break
                        sn_str = 'sn='+ str(num) + ','
                        if( sn_str in subject_sub):
                            subject_sub = subject_sub[subject_sub.find('主语='):]
                            if(',' in subject_sub):
                                ontology = subject_sub[subject_sub.find('主语=')+3:subject_sub.find(',')]
                            else:
                                ontology = subject_sub[subject_sub.find('主语=')+3:]
                            break
                    if (len(ontology) > 0 and len(vehicle) > 0):
                        if (len(zwb_lst)>0):
                            for zwb in zwb_lst:
                                if ('sn=' + str(num) in zwb):
                                    for r_str in zwb.split(','):
                                        if (ontology in r_str):
                                            ontology = r_str[r_str.find('=') + 1:-1].replace('+', '')
                                if ('sn=' + str(sn) in zwb):
                                    for r_str in zwb.split(','):
                                        if (vehicle in r_str):
                                            vehicle = r_str[r_str.find('=') + 1:-1].replace('+', '')
                        logic_lst = []
                        logic_lst.append(ontology)
                        logic_lst.append(vehicle)
                        print('logic*****************',logic_lst)
                        express_str = auto_express('比喻', logic_lst)
                        print('exp*****************',express_str)
                        trans_ltp.thinking_str += '小呆陷入沉思:' + '发现比喻句式，' + express_str + '\n'
                        logic_str = '比喻：' + express_str
            else:
                logic_str = sen_ana.sen_in.replace(' ', '')
                logic_str = '比喻：' + logic_str[logic_str.find(key_words):]
                if('，' in logic_str):
                    logic_str = logic_str[:logic_str.find('，')]
                trans_ltp.thinking_str += '小呆陷入沉思:' + '发现比喻句式，' + logic_str.replace('比喻：','') + '\n'
        return logic_str
    # 并列和选择关系，关键词必须出现两次才成立
    if(logic_dic['并列']<2):
        logic_dic['并列']=0
    if(logic_dic['选择']<2):
        logic_dic['选择']=0
    try:
        logic_str = max(logic_dic, key=logic_dic.get) # 找出字典中值最大的键
    except Exception:
        logic_str = ''
    if(logic_str == '陈述'):
        if(sub_sen):
            if(any(word in sub_sen for word in ['？','吗','难道','谁','哪','什么','怎么'])):
                logic_str = '疑问'
        else:
            if(any(word in sen_ana.sen_in for word in ['？','吗','难道','谁','哪','什么','怎么'])):
                logic_str = '疑问'
    return logic_str

# 典故解析
def idiom_ana(sen_ana, sub_sen):
    idiom_dic={}
    for w_ana in sen_ana.w_anas:
        if(w_ana.wo in sub_sen):
            if(w_ana.pos == '习语'):
                idiom_dic = phase_json_ana(w_ana.wo, False)
    return idiom_dic

def scan_idiom(input_str):
    """
    根据输入内容在概念.我.xml中扫描典故
    :param input_str: 输入典故
    :return: 返回典故信息字典
    """
    idiom_dic={}
    tree = ET.parse(r'/home/ubuntu/DaiMeng/data/xmlData/概念.我.xml')
    root = tree.getroot()
    for me in root:
        node = me.find('我的典故')
        for idiom_node in node:
            if(idiom_node.attrib['标题']==input_str or (input_str in idiom_node.attrib['原文'])):
                idiom_dic['标题'] = idiom_node.attrib['标题']
                idiom_dic['原文'] = idiom_node.attrib['原文']
                idiom_dic['译文'] = idiom_node.text
                idiom_dic['作者'] = idiom_node.attrib['作者']
                idiom_dic['主题'] = idiom_node.attrib['主题']
                break
    return idiom_dic
# 位置解析
def location(g_dic, sub_sen, sn):
    """
    找出子句的位置信息
    :param this_und: 语义字典队列对象
    :param sub_sen: 子句
    :param sn: 单句序号
    :return: 返回时态字符串信息
    """
    location_str = ''
    if('位置' in g_dic.keys()):
        for location_sen in g_dic['位置'].split('\n'):
            if(len(location_sen)==0):
                break
            if('sn='+str(sn) in location_sen):
                location_lst = list(set([lo.replace('位置','').replace(',','').replace('=','').replace('+','').replace(' ','')
                       for lo in re.findall(r'\[(.+?)\]',location_sen)]))
                for location in location_lst:
                    if(location in sub_sen.replace(' ','')):
                        location_str += location + '+'
                break
    if('+' in location_str):
        location_str = location_str[:-1]
    return location_str

# 时态解析
def tense(sen_ana, num):
    """
    找出子句的时态信息
    :param sen_ana: 单句对象
    :param num: 子句序号
    :return: 返回时态字符串信息
    """
    tense_str = ''
    sub_sen_mean = sen_ana.sen_mean.split('，')[num]

    if(sub_sen_mean.find('时态=')>0):
        if(sub_sen_mean.find(',',sub_sen_mean.find('时态='))):
            tense_str = sub_sen_mean[sub_sen_mean.find('时态=')+3:sub_sen_mean.find(',',sub_sen_mean.find('时态='))]
        else:
            tense_str = sub_sen_mean[sub_sen_mean.find('时态='):]
    return tense_str

# 根据翻译的子句找出原句
def find_original(original_sen, sub_sen, sub_sign = True):
    """
    根据翻译的子句找出原句的子句
    :param original_sen: 原句
    :param sub_sen: 翻译的子句
    :return: 返回时态字符串信息
    """
    original_sub_sen = ''
    original_sen_dic = {}
    sub_sen = sub_sen.replace(' ', '')
    # 将原句按逗号分隔成字典，按翻译的子句的每一个字在原句中出现的次数作为字典的value，选择value的key
    if(not sub_sign):
        for sub_str in re.split('[。！？；”]',original_sen):
            i = 0
            for ch in sub_sen:
                if(ch in sub_str):
                    i += 1
            original_sen_dic[sub_str] = i
    else:
        for sub_str in original_sen.split('，'):
            i = 0
            for ch in sub_sen:
                if(ch in sub_str):
                    i += 1
            original_sen_dic[sub_str] = i
    try:
        original_sub_sen = max(original_sen_dic, key=original_sen_dic.get) # 找出字典中值最大的键
    except Exception:
        original_sub_sen = ''
    return original_sub_sen

# 子句句法分析
def depend_parse(sen_ana, num):
    depend_parse_dic = {}
    sub_mean_lst = sen_ana.sen_mean.split('，')[num].split(',')
    mean_v = ''
    mean_cv = '' # 并列V
    mean_cobject = ''  # 并列宾语
    mean_subject = '' # 主语
    mean_object = '' # 宾语
    mean_adv = '' # 状语
    mean_vc = '' # 动补
    mean_attr = [] # 定中
    for sub_mean in sub_mean_lst:
        if('V=' in sub_mean):
            if ('::' in sub_mean[:sub_mean.find('V=')]):
                sub_mean = sub_mean[sub_mean.find('V='):]
            if(len(mean_v)>0):
                if('::' in sub_mean):
                    sub_mean_tmp = sub_mean[:sub_mean.find('::')]
                    mean_cv = mean_cv + sub_mean_tmp[sub_mean_tmp.find('V=')+2:] + '+' # 并列V
                else:
                    mean_cv = mean_cv + sub_mean[sub_mean.find('V=') + 2:] + '+'  # 并列V
            else:
                if('::' in sub_mean):
                    sub_mean_tmp = sub_mean[:sub_mean.find('::')]
                    mean_v = sub_mean_tmp[sub_mean_tmp.find('V=') + 2:]
                else:
                    mean_v = sub_mean[sub_mean.find('V=')+2:]
        if('主语=' in sub_mean and mean_subject==''):
            if('定语=' in sub_mean):
                attribute_str = ''
                for str in sub_mean.replace('+','').replace('定语=','').split('::'):
                    if('主语=' in str):
                        mean_subject = str.replace('主语=','')
                    else:
                        attribute_str = attribute_str + str
                mean_attr.append(attribute_str+'+'+mean_subject)
            else:
                if('::' in sub_mean[:sub_mean.find('主语')]):
                    sub_mean = sub_mean[sub_mean.find('主语'):]
                if ('::' in sub_mean):
                    sub_mean_tmp = sub_mean[:sub_mean.find('::')]
                    mean_subject = sub_mean_tmp.replace('主语=', '')
                else:
                    mean_subject = sub_mean.replace('主语=', '')
        if('宾语=' in sub_mean):
            if (len(mean_object) > 0):
                if (sub_mean.find('::',sub_mean.find('宾语='))>-1):
                    mean_cobject = mean_cobject + sub_mean[sub_mean.find('宾语=') + 3:sub_mean.find('::',sub_mean.find('宾语='))].replace('+','') + '+'  # 并列V
                else:
                    mean_cobject = mean_cobject + sub_mean[sub_mean.find('宾语=') + 3:].replace('+','') + '+'  # 并列V
            else:
                if ('定语=' in sub_mean):
                    attribute_str = ''
                    for str in sub_mean.replace('+', '').replace('定语=', '').split('::'):
                        if ('宾语=' in str):
                            mean_object = str[str.find('宾语=')+3:].replace('宾语=','').replace('+','')
                        else:
                            attribute_str = attribute_str + str
                    mean_attr.append(attribute_str + '+' + mean_object)
                else:
                    if ('::' in sub_mean[:sub_mean.find('宾语')]):
                        sub_mean = sub_mean[sub_mean.find('宾语'):]
                    if('::' in sub_mean):
                        sub_mean_tmp = sub_mean[:sub_mean.find('::')]
                        mean_object = sub_mean_tmp.replace('宾语=', '').replace('+','')
                    else:
                        mean_object = sub_mean.replace('宾语=', '').replace('+','')
        if('状语=' in sub_mean):
            if ('定语=' in sub_mean):
                attribute_str = ''
                for str in sub_mean.replace('+', '').replace('定语=', '').split('::'):
                    if ('状语=' in str):
                        mean_adv = str.replace('状语=', '')
                    else:
                        attribute_str = attribute_str + str
                mean_attr.append(attribute_str + '+' + mean_adv)
            else:
                if('状语' not in sub_mean[sub_mean.rfind('::')+1:sub_mean.rfind('=')]):
                    sub_mean_tmp = sub_mean[:sub_mean.rfind('::')]
                    mean_adv = mean_adv + sub_mean_tmp[sub_mean_tmp.find('状语=')+3:]+ '+'
                else:
                    mean_adv = mean_adv + sub_mean[sub_mean.find('状语=')+3:] + '+'
        if('动补=' in sub_mean):
            if('动补' not in sub_mean[sub_mean.rfind('::')+1:sub_mean.rfind('=')]):
                sub_mean_tmp = sub_mean[:sub_mean.rfind('::')]
                mean_vc = mean_v + '+' + sub_mean_tmp[sub_mean_tmp.find('动补=')+3:].replace('::', '').replace('动补=', '')
            else:
                mean_vc = mean_v + '+'+sub_mean[sub_mean.find('动补=')+3:].replace('::','').replace('动补=', '')
        if('介宾=' in sub_mean):
            if(mean_object==''):
                mean_object = sub_mean[sub_mean.find('介宾=')+3:].replace('+','')
    if(len(mean_subject)==0):
        mean_subject = 'null'
    if(len(mean_v)==0):
        if('' in sen_ana.sen_mean and '::主语' in sen_ana.sen_mean):
            mean_v = sen_ana.sen_mean[sen_ana.sen_mean.find('并列=')+3:sen_ana.sen_mean.find('::',sen_ana.sen_mean.find('并列='))]
        else:
            mean_v = 'null'
    if(len(mean_object)==0):
        mean_object = 'null'
    depend_parse_dic['主语+V+宾语'] = mean_subject+'+'+mean_v+'+'+mean_object
    # 如果句子主谓宾都找不出来，则可能被列入并列=了。例如：并列=人烟稀少::后附加=的::并列=长安+城里+草木+茂密,标点=。
    if(depend_parse_dic['主语+V+宾语']=='null+null+null'):
        sub_mean_dic = collections.OrderedDict()
        for sub_mean in sub_mean_lst:
            if('并列=' in sub_mean):
                tmp_lst = re.split('[:,]',sub_mean)
                tmp_lst = [x for x in tmp_lst if '并列='in x]
                tmp_str = ''
                for ele in tmp_lst:
                    tmp_str = tmp_str+ele.replace('并列=','')+'+'
                for ss in tmp_str.split('+'):
                    if(len(ss)>0):
                        sub_mean_dic[ss]=''
        for w_ana in sen_ana.w_anas:
            # print(w_ana.wo + ':'+w_ana.pos)
            for key in sub_mean_dic:
                if(key == w_ana.wo):
                    sub_mean_dic[key] = w_ana.yuf
        if('SBV' in sub_mean_dic.values()):
            mean_subject = list(sub_mean_dic.keys()) [list(sub_mean_dic.values()).index ('SBV')]
            if (mean_v == 'null'):
                if ('COO' in sub_mean_dic.values()):
                    mean_v = list(sub_mean_dic.keys())[
                        list(sub_mean_dic.values()).index('COO', list(sub_mean_dic.values()).index('SBV'))]
        if('VOB' in sub_mean_dic.values()):
            mean_v = list(sub_mean_dic.keys()) [list(sub_mean_dic.values()).index('VOB')]
        depend_parse_dic['主语+V+宾语'] = mean_subject + '+' + mean_v + '+' + mean_object
    if(mean_cv[-1:]=='+'):
        mean_cv = mean_cv[:-1]
    depend_parse_dic['并列V'] = mean_cv
    if (mean_cobject[-1:] == '+'):
        mean_cobject = mean_cobject[:-1]
    depend_parse_dic['并列宾语'] = mean_cobject
    depend_parse_dic['定+中'] = mean_attr
    depend_parse_dic['动+补'] = mean_vc
    if(mean_adv[-1:]=='+'):
        mean_adv = mean_adv[:-1]
    depend_parse_dic['状语'] = mean_adv
    return depend_parse_dic

def phase_json_ana(input_str, idiom = True):
    """
    根据输入段落分析并解析成json格式
    :param input_str: 输入内容
    :return: 以json格式返回段落分析结果
    """
    phase_ana_dic = {}
    if idiom:
        poem_dic = scan_poem(input_str) # 根据输入的语句在xml中找出古诗信息
    else:
        poem_dic = scan_idiom(input_str) # 根据输入的语句在xml中找出典故信息

    # 能在古诗中找到则为古诗，解析译文，找不到则直接解析原文。
    title = '' # 标题
    author = '' # 作者
    original = '' # 原文
    theme = '' # 主题
    translation = '' # 译文
    if(len(poem_dic)>0):
        trans_json(request_(poem_dic['译文']))
        title = poem_dic['标题']
        author = poem_dic['作者']
        original = poem_dic['原文']
        theme = poem_dic['主题']
        translation = poem_dic['译文']
    else:
        original = input_str
        poem_dic['原文'] = input_str
        poem_dic['译文'] = input_str
        trans_json(request_(input_str))
    Ds_scan()
    fast_scan()
    global this_und
    this_und = trans_ltp.get_thisund()
    print(this_und.Semdic)
    global g_dic
    if(idiom):
        g_dic = this_und.Semdic
    ana_lst = []
    #print(trans_ltp.thinking_str)
    re_dic = phframe_ana.idiomre_ana(this_und, poem_dic)
    if re_dic:
       if re_dic['标题']:
           trans_ltp.thinking_str += re_dic['标题'].replace('\x00','')

    original_sen_lst = re.split('[。！？；”]',poem_dic['原文'])
    # print(original_sen_lst)
    while '' in original_sen_lst:
        original_sen_lst.remove('')
    i = 0
    for sen_ana in this_und.phsen_ana:
        print(sen_ana.sen_mean)
        sen_dic = {}
        sen_dic['sn'] = i
        if(idiom==True):
            # print('i='+str(i))
            sen_dic['原句'] = find_original(poem_dic['原文'], sen_ana.sen_in, False)# original_sen_lst[i]
        else:
            sen_dic['原句'] = poem_dic['原文']
        sen_dic['单句'] = sen_ana.sen_in.replace(' ','')
        sen_dic['认知'] = ''
        sen_dic['逻辑'] = ''
        sen_dic['子句'] = []
        j = 0
        cognize_str = ''
        for sub_sen in sen_ana.sen_in.split('，'):
            if(len(sub_sen) == 0):
                break
            sub_sen_dic = {}
            if(idiom==True):
                sub_sen_dic['原句'] = find_original(sen_dic['原句'], sub_sen)
            else:
                sub_sen_dic['原句'] = poem_dic['原文']
            sub_sen_dic['单句'] = sub_sen
            sub_sen_dic['认知'] = cognize_estimate(sen_ana, sub_sen)
            sub_sen_dic['逻辑'] = logic_estimate(sen_ana, sub_sen)
            if(sub_sen_dic['认知']):
                cognize_str = cognize_str + sub_sen_dic['认知'] + '+'
            sub_sen_dic['位置'] = location(g_dic, sub_sen, i)
            sub_sen_dic['时态'] = tense(sen_ana, j)
            if(idiom == True):
                sub_sen_dic['典故'] = idiom_ana(sen_ana, sub_sen)
            sub_sen_dic['句式'] = depend_parse(sen_ana, j)
            sen_dic['子句'].append(sub_sen_dic)
            j += 1
        if(cognize_str):
            sen_dic['认知'] = cognize_str[:-1]
        else:
            sen_dic['认知'] = ''
        sen_dic['逻辑'] = logic_estimate(sen_ana,'',sen_dic['认知'],sen_dic['子句'],i)
        ana_lst.append(sen_dic)
        i += 1
    phase_ana_dic['标题'] = title
    phase_ana_dic['作者'] = author
    phase_ana_dic['原文'] = original
    phase_ana_dic['译文'] = translation
    phase_ana_dic['主题'] = theme
    phase_ana_dic['解析'] = ana_lst
    if(idiom == True):
        encodedjson = json.dumps(phase_ana_dic, ensure_ascii=False)
    else:
        encodedjson = phase_ana_dic

    return encodedjson

# 将分析出的逻辑和比喻写入xml
def logic_to_xml(phase_json_dic):
    """
    将分析出的逻辑和比喻串写入xml
    :param phase_json_dic: 分析出的古诗json对象字典
    :return:
    """
    tree = ET.parse(r'/home/ubuntu/DaiMeng/data/xmlData/概念.我.xml')
    root = tree.getroot()
    for me in root:
        node = me.find('古诗经验')
        for item in node:
            if(item.attrib['标题']==phase_json_dic['标题']
                    or item.attrib['原文']==phase_json_dic['原文']):
                return
        shili = ET.SubElement(node, '古诗')
        shili.attrib['作者'] = phase_json_dic['作者']
        shili.attrib['标题'] = phase_json_dic['标题']
        shili.attrib['原文'] = phase_json_dic['原文']
        shili.text = '\n\t\t'
        for exp_sen in phase_json_dic['解析']:
            if('比喻：' in exp_sen['逻辑']
                    or '寓情于景：' in exp_sen['逻辑']
                    or '触景生情：' in exp_sen['逻辑'] ):
                shili.text =shili.text + exp_sen['逻辑']+'\n\t\t'
        shili.tail = '\n\t\t'
    tree.write('/home/ubuntu/DaiMeng/data/xmlData/概念.我.xml', encoding='utf-8')

if __name__ == "__main__":
    # input_str = '静夜思'
    # input_str = '黄鹤楼'
    # input_str = '劝君更尽一杯酒'
    # input_str = '国破山河在'
    # input_str = '每逢佳节倍思亲'
    # input_str = '千山鸟飞绝'
    # input_str = '早发白帝城'
    # input_str = '枫桥夜泊'
    # input_str = '登鹳雀楼'
    # input_str = '春眠不觉晓'
    # input_str = '琵琶行'
    # input_str = '春江花月夜'
    # input_str = '赠卫八处士'
    # input_str = '咏柳'
    # input_str = '关山月'
    input_str = '离思五首'
    #input_str = '春天到了，小燕子跟着妈妈从很远很远的南方飞回来。飞呀，飞呀，她们飞过大海。小燕子往下一看，奇怪地问：“妈妈，海面上哪儿来那么多铁塔？”妈妈笑着说：“孩子，那是井架，工人在开采海底的石油呢。”飞呀，飞呀，她们飞过高山。小燕子往下一看，奇怪地问：“妈妈，那火车为什么不冒烟呢？”妈妈笑着说：“孩子，那是电力机车。你看，车顶上还有电线呢。”飞呀，飞呀，她们飞过田野，飞到去年住过的地方。小燕子奇怪地问：“妈妈，这里哪儿来那么多新房子？”妈妈笑着说：“孩子，农民过上好日子啦。你看，那写字的孩子不是京生吗？”小燕子高兴地说：“妈妈，京生也爱学习了。”妈妈说：“是呀！农村的变化可真大啊！”'
    phase_json_object = phase_json_ana(input_str)
    print(phase_json_object)
    print(trans_ltp.thinking_str)
    phase_json = json.loads(phase_json_object)
    logic_to_xml(phase_json)



