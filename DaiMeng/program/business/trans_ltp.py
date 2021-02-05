# -*- coding:utf8 -*-
import re
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import *
import urllib
import requests
import time
import json
# import synonyms as SY
from business.structure import *
from business.structure import PosTag  # 这两条上服务器要加'daimeng.'
# import gensim
from gensim.models import word2vec

import platform, os



global input_a
global input_talk
global thinking_str
stop_list = ['预备概念', '实例', '最常见']

Yufa_dic = {'ADV': '状语', 'SBV': '主语', 'VOB': '宾语', 'ATT': '定语', 'COO': '并列', 'COV': 'CV', 'RAD': '后附加', 'CMP': '动补',
            'POB': '介宾', 'DBL': 'C宾语', 'WP': '标点', 'FOB': '宾语前置','IOB':'间接宾语',
            'LAD': '前附加'}  # YYY语法依存-自知者逻辑标签转换，这里的COO仅仅限于对HED，即并列谓语


tag_mat = []  # 搜索xml文档时，循环调用walk_mat来遍历子节点，需要一个全局变量来控制。
# model = gensim.models.Word2Vec.load('d:/data/Word60.model')
# model = gensim.models.Word2Vec.load('/home/ubuntu/Daimeng_flask/xml/Word2vec/Word60.model') #词向量模型
# model = gensim.models.Word2Vec.load('d:/xml/word2vec/wiki.zh.text.model')
# model = gensim.models.Word2Vec.load('d:/xml/word2vec/word2vec_wx')

env_ws = [[], [], []]  # 环境词汇列表，不重复，分1、2、3字以上
envw_ana = [[], [], []]  # 环境词汇数据分析，重复的不用再搜,再按1、2、3字以上分类，元素是w_ana
This_sen = ''
thinking_str = ''

global phsen_ana  # 各函数公用的句子分析表（列车），成员必须确保sen_ana对象，装载语言云输出的句子分析数据（含词语分析对象列表），另外词语信息中做了词林分类。
phsen_ana = []
def set_phsen(ph=[]):
    # 告诉编译器我在这个方法中使用的a是刚才定义的全局变量a,而不是方法内部的局部变量.
    global phsen_ana
    phsen_ana = ph
def get_phsen():
    global phsen_ana
    return phsen_ana


global this_und
def set_thisund(ph=None):
    # 告诉编译器我在这个方法中使用的a是刚才定义的全局变量a,而不是方法内部的局部变量.
    global this_und
    this_und = ph
def get_thisund():
    global this_und
    return this_und


# 局域网服务器
def request_(input):
    global input_a, thinking_str , input_talk
    global thinking_str
    #uri_base = "http://3s.dkys.org:10008/ltp"
    # uri_base = "http://192.168.101.89:9090/ltp"
    # uri_base = "http://cq.xuduan.tech:12016/ltp"
    uri_base = "http://106.12.122.16:9090/ltp"
    data = {'s': input, 'x': 'n', 't': 'all'}

    response = requests.get(uri_base, data=data)
    print(123,data)
    rdata = response.json()
    input_talk = ''

    input_a = input
    return rdata
    print(rdata)

def trans_json(json_ltp=[]):
    global phsen_ana, env_ws, envw_ana
    phsen_ana = []
    logic_sens = []
    logic_ele = {}  # 主干节点的逻辑语义元素，含依存的二三级语义
    json_str = ''
    for sen_dics in json_ltp[0]:  # 每个句子送回的分析字典列表，目前总是只会送一段
        logic_sens.append("")  # 每个新句子建立一个逻辑语义串,逻辑元素和主干接点id清0
        logic_ele = {}  # 每句之中的主干逻辑元素

        thesen_ana = sen_ana()  # 初始化句子分析对象（车厢）
        thew_anas = []  # 初始化句子分析对象（句子内一队词语）
        the_ws = []  # 词林分类使用的单词列表
        list_HED = []  # 现在把CV也当做HED等级
        for h_dic in sen_dics:  # 开始专门找‘HED’,并列动词处于同等地位
            t_wo = h_dic['cont']
            w_l = min(2, len(t_wo) - 1)  # 区分1,2，3以上字数的词
            t_r = h_dic['relate']
            if t_r == 'HED':
                list_HED.append(h_dic['id'])
                logic_ele[h_dic['id']] = 'V=' + t_wo
                h_id = h_dic['id']
            elif t_r == 'COO':
                if h_dic['pos'] == 'v':
                    h_dic['relate'] = 'COV'  # 单独标识并列的动词
                    list_HED.append(h_dic['id'])
            elif t_r == 'WP':   # 最后两个标点带引号的去掉一个，为什么？可能是有时见句号就停
                t_id = h_dic['id']
                if t_id < len(sen_dics) - 1:
                    if sen_dics[t_id + 1]['cont'] == '”':
                        sen_dics[t_id]['cont'] += '”'

            Pos_ = PosTag.pos_cn(h_dic['pos'])
            thisw_ana = w_ana(wo=t_wo, pos=Pos_)  # 构造加载新词汇信息
            if '助词介词连词'.find(thisw_ana.pos) > -1:
                thisw_ana.syn = t_wo
                thisw_ana.cla = Pos_

            elif thisw_ana.pos == '标点':
                if '、.<>（）()=[]【〖〗】'.find(thisw_ana.wo) > -1:
                    thisw_ana.pos = '符号'
                    thisw_ana.cla = '符号'
                    thisw_ana.syn = t_wo
                    env_ws[w_l].append(t_wo)
                    envw_ana[w_l].append(thisw_ana)
                else:
                    thisw_ana.cla = '标点'
                    thisw_ana.syn = t_wo
                    env_ws[w_l].append(t_wo)
                    envw_ana[w_l].append(thisw_ana)
            elif thisw_ana.pos == '方位名词':
                thisw_ana.syn = t_wo
                thisw_ana.cla = Pos_
                env_ws[w_l].append(t_wo)
                envw_ana[w_l].append(thisw_ana)

            elif thisw_ana.pos == '代词':
                if '为什么怎么怎样谁几多哪些'.find(thisw_ana.wo) > -1:
                    thisw_ana.pos = '疑问词'
            thew_anas.append(thisw_ana)

        tsen_in = ''
        ww = 0
        for w_dic in sen_dics:  # 回头找一级主干依存
            json_str += str(w_dic) + '\n'

            the_wo = w_dic['cont']

            tsen_in += the_wo + ' '
            if not (the_wo in the_ws):
                the_ws.append(the_wo)

            this_line = ""
            this_wgr = ''

            if w_dic['relate'] == 'HED':
                thew_anas[ww].wgr = the_wo  # 依存线路词组装载
                thew_anas[ww].rel = '-1' # 依存路线装载
                thew_anas[ww].yuf = w_dic['relate']
            if w_dic['parent'] in list_HED:  # 以下是与HED关联的主干成分：主谓宾，直接谓语，并列谓语CV，parent=HED的id
                t_r = w_dic['relate']
                if t_r in Yufa_dic:
                    logic_ele[w_dic['id']] = Yufa_dic[w_dic['relate']] + '=' + w_dic['cont']  # 先添加主干语义元素内容

                    if t_r == 'VOB':
                        # 在对上级依存为SBV，且被依存关系中有SVB/动补、后附加时，这个宾语同时也是谓语，添加一个V
                        t_id = w_dic['id']
                        for w_d in sen_dics:
                            if w_d['parent'] == t_id:
                                if 'VOBCMPRAD'.find(w_d['relate']) > -1:
                                    logic_ele[w_dic['id']] = logic_ele[w_dic['id']].replace('=', 'V=')
                    if ww < w_dic['parent']:
                        thew_anas[ww].wgr = w_dic['cont'] + '_' + sen_dics[w_dic['parent']]['cont']  # 依存线路词组装载
                    else:
                        thew_anas[ww].wgr = sen_dics[w_dic['parent']]['cont'] + '_' + w_dic['cont']
                    thew_anas[ww].rel = str(w_dic['id'])  # 依存路线装载
                    thew_anas[ww].yuf = w_dic['relate']
                else:
                    print('========' + w_dic['relate'])
            else:
                par = w_dic['parent']  # 用tree_line表示依存线路
                li_list = [w_dic['id']]
                while not (par in list_HED):  # 顺着parent找HED的id，找到为止，形成一个串
                    if this_line.find('-1') > -1:
                        break
                    li_list.append(par)
                    this_line = str(par) + '_' + this_line
                    par = sen_dics[par]['parent']
                    if par in list_HED:   # 只加词组串不加id串，否则依存sen_mean会乱。
                        li_list.append(par)

                wg_max = max(li_list)
                wg_min = min(li_list)
                this_wgr = '_'
                for gg in range(wg_min, wg_max+1):  # 注意wgr词组按照自然顺序而非依存顺序
                    if gg in li_list:
                        this_wgr += sen_dics[gg]['cont'] + '_'
                thew_anas[ww].wgr = this_wgr.strip('_')  # 依存线路词组装载
                thew_anas[ww].rel = this_line + str(w_dic['id'])  # 依存路线装载
                thew_anas[ww].yuf = w_dic['relate']

            ww += 1

        cizu_temp = {}
        ii = 0  # 循环中辅助计数
        for w_dic in sen_dics:  # 再回头，找主干之后的二级依存，根据依存串描述，二级加标签用冒号挂接，三级直接按顺序用数组连上
            tree_node = thew_anas[ii].rel.split('_')
            if tree_node[0] == '-1':
                del tree_node[0]

            if len(tree_node) > 1:
                t_key = tree_node[0] + '_' + tree_node[1]
                if t_key in cizu_temp:
                    cizu_temp[t_key] = cizu_temp[t_key] + '+' + w_dic['cont']  # 以前两级为key，词组为值，写入字典
                else:
                    cizu_temp[t_key] = w_dic['cont']
            ii += 1

        for key in cizu_temp:
            any_rela = sen_dics[int(key.split('_')[1])]['relate']  # 词组key前一部分是一级id，标识一级ele字典，后一部分是二级id，用两冒号挂接
            logic_ele[int(key.split('_')[0])] += '::' + Yufa_dic[any_rela] + '=' + cizu_temp[key]

        for key in logic_ele:
            logic_sens[-1] += logic_ele[key] + ','
        dics = cla_search(the_ws)  # 分类函数返回value为syn和cla的两个字典
        ww = 0
        for wa_dic in sen_dics:  # 装载段落分析列车信息

            t_wo = wa_dic['cont']
            w_l = min(2, len(t_wo) - 1)  # 区分1,2，3以上字数的词
            if thew_anas[ww].syn == '':  # 连词助词介词代词等分类预先装载，其它的在这里装入类型搜索
                if t_wo in env_ws[w_l]:
                    e_id = env_ws[w_l].index(t_wo)

                    thew_anas[ww].syn = envw_ana[w_l][e_id].syn
                    thew_anas[ww].cla = envw_ana[w_l][e_id].cla
                elif t_wo in dics[0]:
                    thew_anas[ww].syn = dics[0][t_wo]
                    thew_anas[ww].cla = dics[1][t_wo]
                    env_ws[w_l].append(thew_anas[ww].wo)
                    envw_ana[w_l].append(thew_anas[ww])

            ww = ww + 1

        thesen_ana = sen_ana(sen_in=tsen_in.strip(' '), sen_mean=logic_sens[-1], w_anas=thew_anas)
        phsen_ana.append(thesen_ana)
    logsen_fix(logic_sens)
    time1 = str(time.time())

    sp_cla_gen(phsen_ana)
    set_phsen(ph=phsen_ana)
    return phsen_ana


def logsen_fix(sens=[]):  # 在这里做些修正
    fix_dic = {'后附加=了': '时态=完成', '。”': '】', '！”': '】', '标点= ': ''}
    for se in range(0, len(sens) - 1):
        t_se = sens[se].replace('“', '【')
        for fix in fix_dic:
            t_se = t_se.replace(fix, fix_dic[fix]).strip(',')
        phsen_ana[se].sen_mean = t_se


def cla_search(wos=[]):  # 测试了词林分类表.txt搜索的有效性和速度，同时给出组内第一个作为同义词输出，大约40个词/秒。
    time1 = time.time()
    f = ''
    if platform.system() == 'Windows':
        f = open("d:/YYY/cilin_syn.txt", 'r', encoding='UTF-8')
    else:
        f = open("/home/ubuntu/DaiMeng/data/xmlData/cilin_syn.txt", 'r', encoding='UTF-8')

    lines = f.readlines()
    cc1 = 'ABCDEFGHIJKL'  # 词林原分类首字母
    cc7 = '0123456789'  # 词林原分类末位
    this_cl = '社会.人.人群'  # 当前大分类
    Sen = ''
    syndic = {}  # 返回同义词和分类字典
    cladic = {}
    wos_bak = wos
    for w in wos:
        w_l = min(2, len(w) - 1)  # 区分1,2，3以上字数的词
        Sen += w
        if w in env_ws[w_l]:  # 留下了备份，大胆删除环境池里重复的w_ana数据
            wos.remove(w)

    for line in lines:
        line = line.strip('\n').strip(' ') + ' '
        sing_cl = ''
        if line.find('*') > -1:
            continue
        if len(line) < 3:
            continue

        if cc1.find(line[0]) == -1:
            line = line.strip(' ')
            sp_line = line.split(' ')

            if cc7.find(sp_line[0][-2]) > -1:
                this_cl = sp_line[0]
            else:
                sing_cl = sp_line[0]
        cl_len = len(line.split(' ')[0])
        ii = 0
        for wo in wos:
            wo_rela = []  # 单组同义词替换比较
            sen_rela = []  # 二维数组，用于同义词替换后的句子相似度比较
            mulwo = []

            sp_line = line.split(' ')

            if line[cl_len:].find(' ' + wo + ' ') > -1:  #
                rr = 0
                syn_str = sp_line[0][-1] + line[len(sp_line[0]):]  # 送出井号/等号 + 第一个词，可以区分同义词还是同类词
                if len(wo) == 1:  # 词的字数做开关
                    mul_ind = -1  # 临时多义词序号
                    relas = []
                    if wo not in mulwo:
                        mulwo.append(wo)
                        mul_ind = len(mulwo) - 1
                    else:
                        mul_ind = mulwo.index(wo)  # 其实都用不着搜集起来，直接标到每个分类后边啦，只是还没下决心删除

                    for sp in sp_line[1:1]:   # 第0个空格前是分类，后边是展开同义词 gensim现在不用了，保留
                        rela_max = 0
                        for w in wos_bak:  # 每个同义词都要和局子里除自己之外的词算距离
                            if w == wo:
                                continue
                            try:
                                rela_max = max(rela_max, model.similarity(w, sp))  # 调用词汇相似度计算，model60
                            except Exception:
                                continue  # 向量表里缺少太多的词，没词就终止，只能强行推进

                        relas.append(rela_max)
                        # 以下评分算法是只选三个大于.5的来平均，需要改进
                    if len(relas) > 0:
                        rs = 0
                        for r in relas:
                            rs += r
                        rr = int(rs / len(relas) * 100)
                if sing_cl == '':
                    cla_str = this_cl
                else:
                    cla_str = sing_cl  # 单行分类管一行，大分类管到下一个大分类之间

                if wo in syndic:
                    syndic[wo] += '+' + syn_str
                    cladic[wo] += '+' + cla_str
                else:
                    syndic[wo] = syn_str
                    cladic[wo] = cla_str

                # if rr > 0:
                    # cladic[wo] += str(rr)  # 记录每个分类的相似度评分，直接写两个字符
                # wos.remove(wo)       #只取一个分类的做法，注销后一词有多个分类

    result = [syndic, cladic]
    time2 = time.time()

    print(time2 - time1)
    return result  # 输出两字典

def sp_cla_gen(sen_lst=phsen_ana):
# 分析整段语句，生成词汇阵列
    if(not sen_lst):
        return
    for sen_obj in sen_lst:
        sen_lst = []
        semantic_lst = []
        for w_obj in sen_obj.w_anas:
            if(w_obj.wo == '='):
                w_obj.sp_cla = '标点'
                continue
            if(sen_obj.sen_mean.find(w_obj.wo) > 0 ):
                word_index = sen_obj.sen_mean.index(w_obj.wo) #在逻辑语义串中找出单词所在的位置
                equal_index = sen_obj.sen_mean.rindex('=', 0, word_index) #往前找出“=”位置
                pre_index = 0
                if(sen_obj.sen_mean[0:equal_index].find(',') > 0):
                    comma_index = 0
                    colon_index = 0
                    comma_index = sen_obj.sen_mean.rindex(',', 0, equal_index) #往前找出“,”位置
                    if(sen_obj.sen_mean[0:equal_index].find('::') > 0):
                        colon_index = sen_obj.sen_mean.rindex('::', 0, equal_index) #往前找出“::”位置
                    if(comma_index >= colon_index):
                        pre_index = comma_index + 1 #词语前是“，”的情形
                    else:
                        pre_index = colon_index + 2 #词语前是“::”的情形
                if (w_obj.wo == '，' or w_obj.wo == '“'):
                    w_obj.sp_cla = '标点'
                else:
                    w_obj.sp_cla = sen_obj.sen_mean[pre_index:equal_index]
            else:
                w_obj.sp_cla = w_obj.pos

def walk_mat(root_node, read_list, qqq):  # 遍历xml节点的循环调用过程,修改read_list就是返回值
    global tag_mat  # 做记录，不让tag重复匹配上
    if len(tag_mat) > 1:
        return
    cd_node = root_node.getchildren()  # 继续遍历每个子节点
    f_t2 = ''  # 第二个tag被发现的标签
    ii = 0
    for cd in cd_node:
        if cd.tag.split('.')[-1] in stop_list:  # 跳过一些内部小库，先搜正常的<内涵>、<概念>标签，即概念模板自身的结构
            continue
        m_wo = cd.tag.split('.')[-1]

        if qqq.find('=' + m_wo) > -1:
            if m_wo not in tag_mat:
                tag_mat.append(m_wo)
                 # print('tag::' + cd.tag + str(tag_mat))
            if len(tag_mat) > 1:
                temp_list = [cd.tag, cd.attrib, '']
                read_list.append(temp_list)

                if len(cd.getchildren()) == 0:
                    f_t2 = m_wo
                    for tt in range(ii, len(cd_node)):
                        if cd_node[tt].tag.split('.')[-1] == m_wo:
                            read_list[-1][-1] += cd_node[tt].text
                    return

                else:  # 不是叶节点，就P出下一级的tag
                    An_xml = ' '
                    for sun in cd.getchildren():
                        An_xml += sun.tag + '；'
                    read_list[-1][-1] = An_xml.strip(' ')
                    tag_mat.append('ok')
                    return
            else:
                walk_mat(cd, read_list, qqq)

        if f_t2 != '':
            if cd.tag == f_t2:
                read_list[-1][-1] += '：' + cd.text
            else:
                print('eeeeeeeeee' + read_list[-1][-1])
                return

    for child in cd_node:
        walk_mat(child, read_list, qqq)
    return

def Gn_audit(Key=None,log=''):   # 审核预备概念节点里的知识，转移归类到概念分类文档
    if not Key:
        return
    syn_dic = {}   # 生成一个概念名的同义词或者分类词典出来，用于归类。
    p_xml = '/home/ubuntu/DaiMeng/data/xmlData'
    fs = os.listdir(p_xml)
    files = []
    root = None
    wr_node = (None, None)

    cla_no = ['分类', '同义词']   # 这两节点是同义词的标签

    for f1 in fs:
        t_path = os.path.join(p_xml, f1)
        if os.path.isdir(t_path):
            continue
        if f1[-4:] == '.xml':  # 依次打开xml概念文档。
            print(f1)
            if f1.find('概念.') > -1:
                files.append(f1)
                tree0 = ET.parse(t_path)
                root = tree0.getroot()
        else:
            continue
        if root == None:
            continue
        elif f1.find(Key.wo) > -1:
            wr_node[0] = f1
        else:
            for chi in root:
                if chi.tag in stop_list:
                    continue
                syn_str = ''
                for cl_n in cla_no:
                    for syn_no in chi.iter(cl_n):  # 同义词和分类都可以作为这一类的标志。
                        if syn_no.text:
                            if syn_no.text.find(Key.wo) > - 1:
                                wr_node = (t_path, chi.tag)
                                break
                            elif Key.cla != '':
                                sp_cla = Key.cla.replace('_', '.').split('.')
                                sp_cla.reverse()
                                for c_n in sp_cla:
                                    if syn_no.text.find(c_n) > -1:
                                        wr_node = (f1, chi.tag)      # 试试分类第一个的最后一截是否配得上
                                        t_path = os.path.join(p_xml, wr_node[0])
                                        print('写入' + t_path)
                                        wr_n = re.sub(r':+','',Key.wo)
                                        wr_newgn(wr_n, log, t_path)  #这个等级高，不要再搜了
                                        return
                            elif syn_no.text.find(cat_str('上分类=', log, '\'')) > -1:
                                wr_node = (f1, chi.tag)      # 再试试匹配log里面的上分类是否匹配
                            syn_str += ',' + syn_no.text
                if syn_str != '':
                    syn_dic[chi.tag] = syn_str
    print('写入' + str(wr_node))
    t_path = os.path.join(p_xml, t_path)
    if wr_node[0]:   # 匹配上的写入相关概念文档
        wr_newgn(Key.wo, log, t_path)

    else:    # 没匹配上的写入缺省文档库.预备概念.xml
        wr_newgn(Key.wo, log)

def wr_newgn(gn='no', log='', file='/home/ubuntu/DaiMeng/data/xmlData/库.预备概念.xml'):  # 写入预备概念的临时知识库，参数一概念名，参数二为写入内容，必须是逻辑句式的格式（字符串）。
    global thinking_str
    tree0 = ET.ElementTree(file=file)  # xml读写的模板，标签写入、模板插入方式大不相同，就分头写算了
    tree0.getroot()
    root = tree0.getroot()
    par_node = root.find('简易概念')
    if not par_node:
        par_node = SubElement(root, '简易概念')
        par_node.tail = '\n\t'
    gnsn = par_node.find('汇总串')

    if gnsn == None:
        gnsn = SubElement(par_node, '汇总串')
        gnsn.text = ''
        gnsn.tail = '\n\t'
    gn_str = gnsn.text
    if (gn_str + ',').find(',' + gn + ',') == -1:
        new_gn = SubElement(par_node, gn)
        new_gn.text = log
        new_gn.tail = '\n\t'
        par_node.find('汇总串').text += ',' + gn
        thinking_str += '写入新概念::' + log + '\n'
    else:
        t_gn = par_node.find(gn)
        if t_gn:
            ele_log = log.split(',')
            for ele in ele_log:
                if t_gn.text.find(ele) == -1:
                    t_gn.text += ele
                    '添加新内容::' + ele + '\n'
    tree0.write(file, encoding='UTF-8')


def cat_str(key, long_str, sym=','):
    if len(long_str) <= len(key):
        return ''
    cat_str = ''
    leb = long_str.find(key)
    if leb > -1:
        cc = leb + len(key)
        while long_str[cc] != sym[0]:
            cat_str += long_str[cc]
            cc += 1
            if cc == len(long_str):
                break
    return cat_str



if __name__ == '__main__':
    # trans_json(request_('今天怎么回事呢'))
    # input_choice()

    # cla_search(['绿叶'])
    # cilin_class()

    # cilin_class ()
    pass
