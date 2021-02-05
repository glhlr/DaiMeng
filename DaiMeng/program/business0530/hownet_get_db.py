# coding=utf-8

"""
@time: 2019/3/27 13:49
@auther: shaohua

"""

import pyodbc
import re
import chardet
from itertools import permutations, product, combinations, chain
import business.trans_ltp as trans_ltp
import random
from business.structure import *

# from itertools import chain
pos_dic ={'N':'名词','V':'动词','ADV':'副词','ADJ':'形容词','PRON':'代词','CONJ':'连词','COOR':'连词','PUNC':'标点','STRU':'助词','PREP':'介词',
    'AUX':'副词','ECHO':'象声词','NUM':'数词','CLAS':'量词','EXPR':'习语','CHAR':'字符'}
s_dic = {'$': '被', '?': '做成', '+': '可以','%':'属于', '！': '有', '*': '能', '#': '涉及', '^': '不', '~': '或', '[': '属于'}

def is_chinese(uchar):  # 是否中文
    if '\u4e00' <= uchar <= '\u9fff':
        return True
    else:
        return False


# 获取文件编码类型
def get_encoding(file):
    # 二进制方式读取，获取字节数据，检测类型
    with open(file, 'rb') as f:
        return chardet.detect(f.read())['encoding']


# 多个逻辑值的and运算
def and_func(*bools):
    # print(bool)
    if False in bools:
        return False
    else:
        return True


# 逐行打印list
def l_print(list_x):
    if type(list_x) == str:
        list_x = [list_x]
    for i in list_x:
        print(i)


# 计算字符串内的括号是否成对
def brackets_count(str_x):
    L_brackets = [('(', ')'), ('[', ']'), ('{', '}'), ('<', '>')]  # 知网使用的括号对
    brackets_count_list = [[str_x.count(i), str_x.count(j)]
                           for i, j in L_brackets]
    brackets_count_list[3][0] = brackets_count_list[3][0] - str_x.count(
        '<--')  # 剔除括号外的'<--'的数量
    brackets_count_list[3][1] = brackets_count_list[3][1] - str_x.count(
        '-->')  # 剔除括号外的'-->'的数量
    brackets_count_list2 = sum([(i - j) for i, j in brackets_count_list])
    return brackets_count_list2


# 在words_list中查找含有关键词的words
def find_words(word='', gc='', *def_x):
    if len(def_x) == 0:
        def_x = ["|"]
    if gc.upper() == 'A':
        gc = 'ADJ'

    if word == '' and gc == '':
        __words_list = hownet_words_list
    elif word != "" and gc == "":
        __words_list = [i for i in hownet_words_list if i.word == word]
    elif word == "" and gc != "":
        __words_list = [i for i in hownet_words_list if i.gc == gc.upper()]
    else:
        __words_list = [i for i in hownet_words_list if i.word == word and i.gc == gc.upper()]

    x = [i for i in __words_list if and_func(*map(i.is_def, def_x))]
    return x


# 从access的hownet_words中查找含有关键词的words，用于不初始化hownet_words_list的情况，以减少内存占用。
def find_words_db(word='', gc='', *def_x):
    if len(def_x) == 0:
        def_x = ["|"]
    if gc.upper() == 'A':  # A表示ADJ
        gc = 'ADJ'
    if word == '' and gc == '':
        __sql = "select word,gc,def,example,def_cn from hownet_words "
    elif word != "" and gc == "":
        __sql = "select word,gc,def,example,def_cn from hownet_words where word ='{}'".format(word)
    elif word == "" and gc != "":
        __sql = "select word,gc,def,example,def_cn from hownet_words where gc ='{}'".format(gc.upper())
    else:
        __sql = "select word,gc,def,example,def_cn from hownet_words where word ='{}' and gc ='{}'" \
            .format(word, gc.upper())

    __con = pyodbc.connect('DRIVER={};DBQ={};'.format(_DRV, _MDB))
    __hw_line_list = __con.execute(__sql).fetchall()
    __words_list = [line_hw(line) for line in __hw_line_list]

    x = [i for i in __words_list if and_func(*map(i.is_def, def_x))]
    return x


# 在分类树种查找某个词的分类，找到第一个就返回
def find_group(xx):
    return next((i for i in hownet_group_tree if xx in re.split('[.]', i)),
                None)

# 在分类树种查找分类，根据amount返回结果，分类可以有多个值，有多个值时需同时包含在分类树中
def find_groups(amount=0, *groups):
    if type(amount) is not int:  # 第一个参数不是整数的时候，amount当作分类，返回所有符合条件的分类。
        groups = groups + (amount,)
        amount = 0
    groups = set(chain(*[i.split(".") for i in groups]))
    if amount > 0:  # amount 大于0，返回list，list含有amount个分类
        groups_list = [i for i in hownet_group_tree if groups <= set(re.split('[.]', i))]
        if amount < len(groups_list):
            groups_list = groups_list[:amount]
    elif amount < 0:  # amount 小于0，返回list，分类不包含Converse.txt、Antonym.txt、Secondary Feature.txt
        groups_list = [i for i in hownet_group_tree if groups <= set(re.split('[.]', i))
                       and re.split('[.]', i)[0] not in ["Converse", "Antonym", "Secondary"]]
    else:  # amount 等于0，返回list，list含有所有符合条件的分类
        groups_list = [i for i in hownet_group_tree if groups <= set(re.split('[.]', i))]

    return groups_list


# 在stru_tree中查找含有关键词的stru,前两个参数是sn和是否精确匹配，后面的可变参数是SYN_S和SEM_S的查询参数。
def find_stru(sn='', accurate=True, *args):
    args = [i for i in args if i != '']
    if len(args) > 0:
        syn_list = [i.upper() if i.upper() != "ADJ" else "A" for i in args
                    if i.isalpha() and not is_chinese(i)]  # 取字母出来作为syn（词性）查询关键字
        sem_list = [i for i in args if is_chinese(i[-1])]  # 取中文出来作为sem（分类）查询关键字
    else:
        syn_list = []
        sem_list = []

    if len(syn_list) == 0:
        x_list = hownet_stru_tree
    elif len(syn_list) == 1:  # 修正只有一个syn参数的时候出现的问题。
        x_list = [i for i in hownet_stru_tree if syn_list[0] in i.syn_sem_format["syn"]]
    else:
        x_list = [
            i for i in hownet_stru_tree
            if True in map(lambda j: list(j) == i.syn_sem_format["syn"],
                           permutations(syn_list))
        ]

    if sn == "":  # sn为''时，查询时忽略sn
        x = [i for i in x_list if i.is_sem(*sem_list)]
    else:
        if accurate:  # accurate为true时，sn精确匹配，false时，sn左边匹配
            x = [i for i in x_list if i.serial == sn]
        else:
            x = [
                i for i in x_list
                if i.serial[:len(sn)] == sn and i.is_sem(*sem_list)
            ]
    return x

    # 按照syn和sem分割的位置依次


def find_stru_2(sem0='', syn0="", sem1="", syn1=""):
    return [i for i in hownet_stru_tree if
            i.is_sem_p(0, sem0) and i.is_sem_p(1, sem1) and
            i.is_syn_p(0, syn0) and i.is_syn_p(1, syn1)]

    # 顺便找一个词，找到适配的HownetStru


# 从数据库读取words的数据
# 类定义
class HownetWords(object):
    def __init__(self, word='', gc='', de='', example=''):
        self.word = word  # 单词
        self.gc = gc  # 词性
        self.DEF = de  # 分类
        self.example = example  # 例词
        self.def_cn = []  # 按,分割，并去掉英文字母。保留前缀

    def def_find(self, word):  # 在词的分类中查询，不包括前缀。已经弃用
        if self.DEF.find(word) != -1:
            return self.DEF
        else:
            return None

    def is_def(self, def_x):  # 在词的分类中查询，是否包含相应的分类。
        if def_x == "|":
            return True
        if def_x in self.def_cn:
            return True
        else:
            return False

    # DEF去分隔符，并去掉英文，返回list,保留前缀，例如*付。
    def def_trans_list(self):
        x = [re.sub("[A-Za-z|)}{(]", "", i) for i in re.split('[,]', self.DEF)]
        return x

    # DEF_list转为group tree的内容，有包含关系的去重复
    def def_trans_groups(self):
        if self.def_cn == [""]:
            return []

        x = [
            find_group(i) if is_chinese(i[0]) else find_group(i[1:])
            for i in self.def_cn
        ]
        if len(x) == 0:
            x = [self.DEF.split('|')[-1]]
        elif len(x) == 1:
            return x


        while None in x:
            x.remove(None)
        return x

    def __str__(self):
        return f"HownetWords({self.word}：{self.gc}，{self.DEF})"

    __repr__ = __str__


# 知网-中文信息结构库.txt
class HownetStru(object):
    # 初始化
    def __init__(self, serial='', syn='', sem='', example=''):
        self.serial = serial  # 序号
        self.syn = syn  # 词性搭配
        self.sem = sem  # 分类搭配
        self.example = example  # 例词
        self.qa = {
            'Query1': '',
            'Answer1': '',
            'Query2': '',
            'Answer2': '',
            'Query3': '',
            'Answer3': '',
            'Query4': '',
            'Answer4': '',
            'Query5': '',
            'Answer5': '',
        }  # query和answer成对出现。
        self.syn_sem_format = {"syn": [], "sem": []}  # 格式化之后的syn和sem

    # 打印HownetClass
    def print_stru(self):
        print('serial：', self.serial)
        print('SYN：', self.syn)
        print('SEN：', self.sem)  # 逗号是要求同时满足，/是并列的意思（或）
        # self.print_qa()
        print('例子：', self.example)

    def print_qa(self):
        if self.qa['Query1'] != '':
            print('Query1：', self.qa['Query1'])
            print('Answer1：', self.qa['Answer1'])
        if self.qa['Query2'] != '':
            print('Query2：', self.qa['Query2'])
            print('Answer2：', self.qa['Answer2'])
        if self.qa['Query3'] != '':
            print('Query3：', self.qa['Query3'])
            print('Answer3：', self.qa['Answer3'])
        if self.qa['Query4'] != '':
            print('Query4：', self.qa['Query4'])
            print('Answer4：', self.qa['Answer4'])
        if self.qa['Query5'] != '':
            print('Query5：', self.qa['Query5'])
            print('Answer5：', self.qa['Answer5'])

    #  sem的分割方法,以<--为主分隔符进行分割，只分割一层
    def sem_split_1(self):
        x_list = re.split('(<--)|(-->)', self.sem)
        y_list = []
        for k, y in enumerate(x_list):
            if y is None or y == '':
                continue
            if k == 0:
                y_list.append(y)
                x_count = 0 if y == '<--' or y == '-->' else brackets_count(
                    y_list[-1])
                continue
            if x_count == 0:
                z = brackets_count(y)
                y_list.append(y)
                x_count = 0 if y == '<--' or y == '-->' or z == 0 else z
            else:
                y_list[-1] = y_list[-1] + y
                x_count = brackets_count(y_list[-1])
        return y_list

    #  syn的分割方法,以<--为主分隔符进行分割，只分割一层
    def syn_split_1(self):
        x_list = re.split('(<--)|(-->)', self.syn)
        y_list = []
        for k, y in enumerate(x_list):
            if y is None or y == '':
                continue
            if k == 0:
                y_list.append(y)
                x_count = 0 if y == '<--' or y == '-->' else brackets_count(
                    y_list[-1])
                continue
            if x_count == 0:
                z = brackets_count(y)
                y_list.append(y)
                x_count = 0 if y == '<--' or y == '-->' or z == 0 else z
            else:
                y_list[-1] = y_list[-1] + y
                x_count = brackets_count(y_list[-1])
        return y_list

    # 对HownetStru.sem进行简单的分割
    def split_sem_simple(self):
        a = re.split('[{}(), < -/]',
                     self.sem.replace('[', '').replace(']', ''))
        b = [i for i in a if i != '']
        return b

    # 格式化syn和sem ，
    def syn_sem_formating(self):

        # 取两个字符串之间的内容返回list
        def get_words(str_beg, str_end, string):
            xxx = re.findall(r'{}([^{}]+)'.format(str_beg, str_end), string)
            return xxx

        b = re.split('<--|-->', self.syn)
        self.syn_sem_format['syn'] = [
            ''.join([i.replace('{', '').replace('}', '').strip() for i in c])
            for c in b
        ]

        d = re.split('<--|-->', self.sem)
        for j, sem_i in enumerate(d):
            if sem_i.find('“') != -1:  # 如果有“”，只保留“”内的内容。
                d[j] = ['“' + l for l in get_words('“', '”', sem_i)]
                continue
            if sem_i.find('[') != -1 or sem_i.find('《') != -1:  # 去掉[],《》及其内部的东西
                sem_i = re.sub(u"\\[.*?]|\《.*?》", "", sem_i)
            sem_i = sem_i.replace("}", "").replace("{", "").replace("<", "").replace(
                ">", "").strip()  # 去掉{}，不去掉内部的内容。
            # i = re.split('[/()]', i)
            sem_i = re.split('[,()]', sem_i)  # 以,()这3个符号分割，并去掉分割之后的空元素""。
            for k in sem_i:
                if k == '':
                    sem_i.remove('')
            for n, k in enumerate(sem_i):
                if "/" in k:
                    sem_i[n] = sem_i[n].split("/")  # /分割为list，表示其中的内容并列。
                else:
                    sem_i[n] = [sem_i[n]]  # 转为1个元素的list
            d[j] = sem_i
        self.syn_sem_format['sem'] = d
        # 我/你/他 这种情况要单独列出来

    # 判断group_x是否在类的sem中同时存在。sem中用/分割的分类，同时只取其中1个，不算同时存在。
    def is_sem(self, *group_x):
        sem_list = self.syn_sem_format["sem"]
        for sem_x in sem_list:
            # l_print(sem_x)
            for sem_y in product(*sem_x):
                if set(list(group_x)) <= set(sem_y):
                    return True
        else:
            return False

    # 判断group_x是否在类的sem中存在。sem中用/分割的分类，同时只取其中1个，不算同时存在。
    # 如果第一个参数是数字n，则分类中提取n个参数，查询同时存在的可能，否则只取其中1个参数）
    def is_sem_n(self, amount=1, *group_x):
        if type(amount) == int:
            if amount <= 0:
                amount = 1
            else:
                amount = min(amount, len(group_x))
            group_y = group_x
        else:
            group_y = group_x + (amount,)
            amount = 1
        sem_list = self.syn_sem_format["sem"]
        for sem_x in sem_list:
            for sem_y in product(*sem_x):
                for group_z in combinations(group_y, amount):
                    if set(list(group_z)) <= set(sem_y):
                        # print(group_z, sem_y)
                        return True
        else:
            return False

    # position表示在sem中的第几位,*group_x中的分类要同时存在于某个sem分割块中。
    def is_sem_p(self, position=0, *group_x):
        if len(self.syn_sem_format["sem"]) - 1 < position:  # 如果位置大于sem分割后的长度，返回否
            return False
        sem_list = self.syn_sem_format["sem"][position]
        for sem_y in product(*sem_list):
            for group_z in permutations(group_x):
                if set(list(group_z)) <= set(sem_y):
                    return True
        else:
            return False

    # position表示在syn中的第几位,pos_x是词性。
    def is_syn_p(self, position=0, pos_x=""):

        if len(self.syn_sem_format["syn"]) - 1 < position:  # 如果位置大于syn分割后的长度，返回否
            return False
        if pos_x.upper() == "ADJ":
            pos_x = "A"
        if pos_x.upper() in self.syn_sem_format["syn"][position].split("/"):
            return True
        else:
            return False

    def __str__(self):
        return f"HS({self.serial})({self.syn})(sem:{self.sem})"

    __repr__ = __str__


# 连接数据库
_MDB = r'/home/ubuntu/DaiMeng/data/accessDB/DaiMeng.mdb'  # 绝对路径
#_DRV = '{microsoft access driver (*.mdb, *.accdb)}'  # odbc数据源
_con = pyodbc.connect('DRIVER=MDBTools;DBQ=/home/ubuntu/DaiMeng/data/accessDB/DaiMeng.mdb;')

_con.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
# 从数据库读取groups的数据
_sql = "select groups,remarks from hownet_groups"
_group_list = _con.execute(_sql).fetchall()

hownet_group_tree = [i[0] for i in _group_list]
#print('hownet_group_tree',hownet_group_tree)
hownet_group_dict = {i[0]: i[1] for i in _group_list}   #  if i[1] != ''
#print('hownet_group_dict',hownet_group_dict)
ii=0
while ii<len(hownet_group_tree):
    hownet_group_tree[ii] =hownet_group_tree[ii].replace('\x00','')

    ii+=1
_new={}
for key in hownet_group_dict:
    if hownet_group_dict[key]:
        _new[key.strip('\x00')]=hownet_group_dict[key].strip('\x00')
    else:_new[key.strip('\x00')]=''

hownet_group_dict=_new
#print(len(_new))
# 从数据库读取word
def line_hw(word_line):  # 数据库的一行转为HownetWord类
    hw = HownetWords(*word_line[:4])
    #print(word_line[4])
    if word_line[4]:
        hw.def_cn = (word_line[4]).split(",")
    return hw


# 读取数据库hownet_words的所有记录，初始化hownet_words_list
_sql = "select word,gc,def,example,def_cn from hownet_words"
_word_list = _con.execute(_sql).fetchall()
hownet_words_list = [line_hw(line) for line in _word_list]
ii=0
while ii<len(hownet_words_list):
    hownet_words_list[ii].word =hownet_words_list[ii].word.replace('\x00','')
    hownet_words_list[ii].gc=hownet_words_list[ii].gc.replace('\x00','')
    ii+=1


# 从数据库读取stru
def line_hs(stru_line):  # 数据库的一行转为HownetStru类
    hs = HownetStru(*stru_line[:4])
    keys = "Query1,Query2,Query3,Query4,Query5,Answer1,Answer2,Answer3,Answer4,Answer5".split(",")
    values = stru_line[4:]
    for key, value in zip(keys, values):
        hs.qa[key] = value
    hs.syn_sem_formating()
    return hs

_con.setdecoding(pyodbc.SQL_CHAR, encoding='ISO-8859-1')
# 读取数据库hownet_strus，初始化hownet_stru_tree
_sql = "select serial,syn,sem,example,Query1,Query2,Query3,Query4,Query5,Answer1,Answer2,Answer3,Answer4,Answer5 from hownet_strus"
_stru_list = _con.execute(_sql).fetchall()

hownet_stru_tree = [line_hs(line) for line in _stru_list]
#print('hownet_stru_tree',hownet_stru_tree[:4000])

_con.close()



def hn_walk(key='时间'):  # hn漫游，输入一个词，就能P出Hn体系中尽可能多的知识。
    if key == '':
        return None
    means = find_words(key)
    Wo_nlu = cla_NLU(cla_dic={'类型': '概念'})

    Wo_nlu.features['语义树'] = {}
    Wo_nlu.features['词性'] = {}
    Wo_nlu.features['举例'] = {}
    for hw in means:
        Wo_nlu.member.append(str(hw.def_cn))  # 在dic里已经str了，这里是否应该保持list呢？
        Wo_nlu.features['语义树'][str(hw.def_cn)] = hw.def_trans_groups()
        Wo_nlu.features['词性'][str(hw.def_cn)] = hw.gc
        if hw.example:
            Wo_nlu.features['举例'][str(hw.def_cn)] = hw.example

    f_tr = False  # 本key是不是一条分类树，只做一次
    for kk in hownet_group_dict:  # 现在概念树里搜索，查找带有该词语的概念和关联   如禽能飞，飞行器能飞
        if key in kk.split('.'):   # 先做子树，统一处理常识
            s_tree = kk
            if hownet_group_dict[kk]:   # 本子树涉及关联的常识吧
                s_tree += '    包含常识:' + hownet_group_dict[kk]
                for hw in means:
                    if kk == hw.def_trans_groups()[0]:
                        if '树关联' not in Wo_nlu.features:
                            Wo_nlu.features['树关联'] = {}
                        Wo_nlu.features['树关联'][str(hw.def_cn)] = hownet_group_dict[kk]
            s_tree += '\n'
            if key == kk.split('.')[-1]:
                if 'hn树' not in Wo_nlu.cla_dic:
                    Wo_nlu.cla_dic['hn树'] = ''
                Wo_nlu.cla_dic['hn树'] += s_tree
            else:
                if 'hn子树' not in Wo_nlu.cla_dic:
                    Wo_nlu.cla_dic['hn子树'] = ''
                Wo_nlu.cla_dic['hn子树'] += s_tree
            continue
        if hownet_group_dict[kk]:
            cs_i = hownet_group_dict[kk].find('|'+key)  # 其它子树可能涉及自己（本树）作为常识
            if cs_i > -1:
                add = ''
                cs_str = hownet_group_dict[kk]
                while cs_i > -1:
                    if cs_str[cs_i] in s_dic:
                        add = s_dic[cs_str[cs_i]]
                        if cs_str[cs_i-1] in ['^','~']:  # 双操作符
                            add = s_dic[cs_str[cs_i-1]] + add
                        break
                    cs_i += -1
                if '关联树' not in Wo_nlu.cla_dic:
                    Wo_nlu.cla_dic['关联树'] = ''
                Wo_nlu.cla_dic['关联树'] += kk + add + key + '\n'

    syn = {}  # 同义词字典
    cla = {}  # 同级以下分类字典
    sfc = []  # 首字相同的词
    inc = []  # 包含了这个词的词
    rela = {} # 关联词字典
    syn_hn_list = {}  # 近义词很重要，保存list，后续甄别。

    for hn in hownet_words_list:   #进入每一词条查找，搜索近义词、同类词、关联词
        ds = []  # 每个义项的内涵
        if hn.word[0] == key[0]:
            if hn.word not in sfc:
                sfc.append(hn.word)
        if hn.word.find(key) > -1:  # 包含它的词
            if hn.word not in inc:
                inc.append(hn.word)

        for hw in means:
            s_d = str(hw.def_cn)
            if hw.def_cn == hn.def_cn:
                if s_d not in syn:
                    syn[s_d] = []
                syn[s_d].append(hn.word)
                if hn.word not in syn_hn_list:
                    syn_hn_list[hn.word] = []
                syn_hn_list[hn.word].append(hn)

            elif len(hw.def_cn) > 1:  # 如果直接对不上，去掉最后一个内涵来对
                if hw.def_cn[:-1] == hn.def_cn[:-1]:
                    s_d = str(hw.def_cn[:-1])
                    if s_d not in cla:
                        cla[s_d] = []
                    cla[s_d].append(hn.word)
            else:  # 以下看hn的内涵树能否对上key
                for f in hn.def_cn:
                    ds.append(f)
                    if hn.def_cn.index(f) > 0:  # 注意这里故意不取第一位
                        if re.match(r'[*#]', f):
                            ds.append(f[1:])
                if f_tr:
                    gn = key
                    if gn in ds:
                        if ds.index(gn) > 0:  # 注意这里故意不取第一位
                            if (hw.def_cn[0] + '+' + hn.def_cn[0]) not in rela:
                                rela[hw.def_cn[0] + '+' + hn.def_cn[0]] = []
                            rela[hw.def_cn[0] + '+' + hn.def_cn[0]].append(hn.word)
    for kk in syn:
        if kk not in cla:
            cla[kk] = []
        k_tr = Wo_nlu.features['语义树'][kk]
        if len(k_tr) > 1:   # 当def_cn的内涵较多，或者第一树较长（.多）的时候，近义词相对可信，处理一下。
            continue
        if len(k_tr[0].split('.')) > 3:
            continue
        if re.sub(r'[\'\[\]]', '', kk) == key:
            cc = []
            for kw in syn[kk]:
                if kw in sfc:
                    continue
                elif kw[-1] in key:
                    continue
                else: cc.append(kw)
            for c in cc:    # 出来才能删
                syn[kk].remove(c)
                if c not in cla[kk]:
                    cla[kk].append(c)
        else:
             cla[kk] = syn[kk]

    groups = {}
    for st in hownet_stru_tree:  # 搭配的例子和关联的例子大不相同
        t_re = ''
        for sdp in st.example.split('，'):
            if ('-' + sdp + '-').find('-' + key + '-') > -1:
                t_re += sdp + '，'

        if t_re != '':
            groups[st.sem] = t_re.strip('，') + '\n'
    Wo_nlu.features['近义词'] = syn
    Wo_nlu.features['同类词'] = cla
    Wo_nlu.cla_dic['关联词'] = rela
    Wo_nlu.cla_dic['包含词'] = inc
    Wo_nlu.cla_dic['搭配'] = groups
    Wo_nlu.cla_dic['首字词'] = sfc

    print(Wo_nlu.features)

    return (Wo_nlu.cla_dic)


def hnrel_ana(sem_str=[], s_ele=''):
    hn_ws = []
    if len(sem_str) > 0:
        dp_str = sem_str
    elif s_ele.find('=') > -1:
        dp_str = s_ele.split('=')[-1].split('+')
    else: return
    w_s = '' # 用-把词连起来
    for ww in dp_str:
        means = find_words(ww)
        hn_ws.append(means)
        w_s += '-' + ww
    w_s = w_s.strip('-')
    rel_info = ''
    stsems = []
    M_st = []
    max_no = 0  # 记录最大节点数，用于参考搭配数的具体程度
    for st in hownet_stru_tree:
        m_no = 0
        if w_s in st.example.split('，'):
            rel_info += '发现实例位于:' + st.sem + '\n'
            continue
        sp_sem = re.split(r'-->|<--',st.sem) # 271种hn分类搭配,按箭头分开
        sp_cx = re.split(r'-->|<--',st.syn) # 词性也分一下，也做匹配因素
        if len(sp_sem) != len(hn_ws):
            continue
        i = 0
        for hhh in hn_ws:
            sem_i = trans_ltp.cat_str('(',sp_sem[i],')')
            dps = sem_i.split(',')[-1].split('/')  # 搭配分类中的多个可能的树节点
            cxs = re.sub(r'[{}]','',sp_cx[i].strip()).split('/')  # 整理格式，得到可能的词性
            mat1 = False
            for hw in hhh:
                if hw.gc not in cxs:  # 词性不对跳过
                    continue
                for ss in dps:
                    gr = hw.def_trans_groups()
                    if not gr:
                        continue
                    if ss in hw.def_trans_groups()[0].split('.'):
                        t_no = hw.def_trans_groups()[0].split('.').index(ss)
                        if t_no >= max_no:
                            m_no = max(t_no,m_no)
                            max_no = t_no
                        mat1 = True
                        break
                if mat1:
                    break
            if mat1:
                if i == len(hn_ws)-1:
                    stsems.append(st.sem)
                    if m_no == max_no:
                        M_st.append(st.sem + '。   例子有:' + st.example)
                    sp_exa = re.split(r'[-，]]',st.example)
                    for ww in dp_str:
                        if ww in sp_exa:
                            rel_info += ww + '位于:' + st.sem + '  的实例中\n'
                        break
                    break
                else:
                    i += 1
                    continue
            else: break
    print(str(len(stsems)) + '个搭配')
    print(stsems)
    print(str(len(M_st)) + '个具体搭配')
    return(stsems)

def load_dmset():
    p_xml = '/home/ubuntu/DaiMeng/data/xmlData/'
    tree0 = ET.parse(p_xml + f1)
    root = tree0.getroot()
    myset = None
    for t_s in root.iter(no):  #找到节点参数的大XML
        myset = t_s
    if myset:
        for sen in re.split(r'[。！”？\n]|\.\.\.*',myset.text):
            for info in ['','','']:
                pass


def ph_hn_ana(ph_w=[], ph_d={}):  # 从hn知网的角度，找出两颗最多的分类树,也分析关联树
    if ph_d == {}:
        ph_d = {'1': '1'}
    if ph_w == [] or ph_d == {}:  # ph_d并未用上
        return
    w_p = ['标点','符号','助词']  # 跳过这些
    meanings = {}
    ph_trees = {}
    Shn_ana = {'树对词': None, '内涵': None, '搭配': None, '最多分类': None, '好概念': None, '坏概念': None}  # 两层字典
    good = {}
    bad = {}
    for hn in hownet_words_list:  # 查找内涵0分类树的重复
        for ws in ph_w:
            if ws.pos in w_p:
                continue
            hn.word = hn.word.replace('\x00','')
            if hn.word == ws.wo:
                print(ws.wo)
                t_p = ws.pos  # 处理一下词林和hn词性的差异
                if t_p.find('名') > -1:
                    t_p = '名词'
                if t_p == '数量词':
                    t_p = '数词+量词'
                if pos_dic[hn.gc] not in t_p:  #
                    if pos_dic[hn.gc] not in ws.cla:
                        continue
                for nn in hn.def_cn:
                    nn = re.sub(r'[\?#~&!*$%=]','',nn)
                    if nn not in meanings:
                        meanings[nn] = hn.word
                    else:
                        meanings[nn] += '+' + hn.word

                tree = hn.def_trans_groups()

                if not tree:
                    continue                
                if not tree[0]:
                    continue
                tree = hn.def_trans_groups()[0]

                if tree.split('.')[-1] in ['部件','属性值']:  # 语义修订，因为部件的语义不够独立
                    if len(hn.def_trans_groups())>1:
                        tree = hn.def_trans_groups()[1] + '_' + tree.split('.')[-1]
                for gr in range(0,len(hn.def_trans_groups())):
                    if gr == 0:
                        continue
                    defss = hn.def_trans_groups()[gr].split('.')
                    if defss[-1] in S_trees['坏']:
                        tree += '._' + defss[-1]
                        if hn.word in bad:
                            bad[hn.word] += '\n' + tree
                        else:
                            bad[hn.word] = tree
                    elif defss[-1] in S_trees['好']:
                        tree += '._' + defss[-1]
                        if hn.word in good:
                            good[hn.word] += '\n' + tree
                        else:
                            good[hn.word] = tree
                if tree not in ph_trees:
                    ph_trees[tree] = hn.word
                else:
                    ph_trees[tree] += '+' + hn.word
                    print('ph_trees[tree]',ph_trees[tree])
    for gg in hownet_group_dict:
        if hownet_group_dict[gg]:
            for me in hownet_group_dict[gg].split(','):
                mea = re.sub(r'[\?#&~!*%$=]','',me)
                if mea in meanings:
                    meanings[mea] += '+' + gg
    Shn_ana['内涵'] = meanings
    Shn_ana['树对词'] = ph_trees

    Shn_ana['好概念'] = good
    Shn_ana['坏概念'] = bad
    absdic = {}  # 从ma出发的抽象树
    abtree = {}  # ma：实际比ma具体的树
    atrees = {}  # 树的交集：词汇
    for key in ph_trees:  # 太抽象无意义从ma这个等级启动分类树整理
        for cla in S_trees['常识抽象']:     # 知网对物质的分类
            if cla in key.split('.'):
                if cla in absdic:
                    if ph_trees[key] not in absdic[cla].split('+'):  # 重复的不计
                        absdic[cla] += '+' + ph_trees[key]
                    k2 = ''     # 取原树的交集
                    for k in key.split('.'):
                        if k in abtree[cla]:
                            k2 += '.' + k
                    abtree[cla] = k2.strip('.')
                else:    # 两个字典暂存ma类型的树的交集，还有交集树的概念（词汇）
                    absdic[cla] = ph_trees[key]
                    abtree[cla] = key

    tr_ti1 = {}  # 统计树出现的次数，与成员数不同
    m_ti = [0, 0]
    for kk in absdic:
        atrees[abtree[kk]] = absdic[kk]
        ti = len(absdic[kk].split('+'))

        if ti > min(m_ti[0],m_ti[1]):
            m_ti.remove(min(m_ti[0],m_ti[1]))
            m_ti.append(ti)
        tr_ti1[abtree[kk]] = ti

    tr_ti = {}  # 取两个最大的分类树，注意并列的也算上了
    w_tr = []  # 需要搜索的词语，树的末端+
    for tr in tr_ti1:
        if tr_ti1[tr] in m_ti:
            tr_ti[tr] = atrees[tr]
            w_tr.append(tr.split('.')[-1])
            for w in atrees[tr].split('+'):
                if w not in w_tr:
                    w_tr.append(w)
    Shn_ana['最多分类'] = tr_ti

    group = {'关联搭配': '', '思维搭配': '', '验证搭配': ''}
    # hn中的stru库，有一个对上为关联搭配，两个对上为验证，与思维有关的搭配形成对话输出。
    for st in hownet_stru_tree:  # 搭配的例子和关联的例子大不相同
        t_re = ''
        for sdp in st.example.split('，'):
            for tw in sdp.split('-'):
                mt = 0
                if tw in w_tr:
                    t_re += sdp + '，'
                    mt += 1
                    if st.sem.find('精神') > -1:
                        group['思维搭配'] += '小萌:我们应该' + sdp + '吗？\n'
                        d_w = sdp.split('-')
                        d_w.remove(tw)
                        t_hn = find_words(d_w[0])
                        S_att = '看情况'
                        for hh in t_hn:  #  搜索搭配分类树的好/坏态度
                            if str(hh.def_trans_groups()).find('.好') > -1:
                                S_att = '应当'
                                break
                            elif str(hh.def_trans_groups()).find('.坏') > -1:
                                S_att = '不该'
                                break
                        S_exp = Exp_dic[S_att].split('+')
                        group['思维搭配'] += '小呆:' + S_exp[random.randint(0, len(S_exp) - 1)].replace('@S0',sdp) + '\n'
                if mt > 1:
                    group['验证搭配'] += '验证搭配' + sdp + '\n'

        if t_re != '':
            group['关联搭配'] += st.sem + '搭配包括' + t_re.strip('，') + '\n'
    Shn_ana['搭配'] = group
    print(Shn_ana)
    return(Shn_ana)

    pass


def hncc_ana(title='静夜思'):  # 拆开到字的详细内涵分析，扩展两层的概念关联，中间可讨论输出
    if title == '':
        return
    talk = ''
    mean_d = {}
    rel_gn = {}
    ti_c = title  # 剩下的
    for hn in hownet_words_list:
        if len(hn.word) == 1:  # 第一遍排除单字词。
            continue
        if hn.word in ti_c:
            ti_c = ti_c.replace(hn.word, '')
            if hn.word not in rel_gn:
                rel_gn[hn.word] = find_words(hn.word)
    if ti_c != '':
        cc = 0
        while cc <len(ti_c):
            rel_gn[ti_c[cc]] = find_words(ti_c[cc])
            cc += 1

    total = '看题目这首诗要讲的是,'
    tot = []
    for kk in rel_gn:
        f_e = {}   # 内涵元素，即def_cn的成员
        tot.append('')
        print(len(rel_gn[kk]))
        for se in rel_gn[kk]:
            tal = ''
            for ee in se.def_cn:
                if ee in ['属性','属性值']:  # 属性值是多余信息，后边的意思足够
                    continue
                if ee in ['文字']:  # 对姓氏，先去掉
                    break
                if ee[0] in s_dic:
                    ee = ee[1:]
                if len(rel_gn[kk]) == 1:
                    if kk not in f_e:
                        f_e[ee] = kk
                    elif kk not in f_e[ee].split('+'):
                        f_e[ee] += '+' + kk
                    tal += ee

                elif len(rel_gn[kk]) < 4:
                    tal += ee
                elif len(rel_gn[kk]) > 3:  # 项数很多的时候挑几种能理解的。
                    if ee in Tr_und_dic:
                        tal += ee
                if ee in Tr_und_dic:    # 对树的描述
                    ts = Tr_und_dic[ee].split('+')
                    tal = tal.replace(ee,ts[random.randint(0,len(ts)-1)])
            if tal != '' and len(rel_gn[kk]) > 1:
                if tal in Tr_und_dic:
                    ts = Tr_und_dic[tal].split('+')
                    tal = tal.replace(tal, ts[random.randint(0, len(ts) - 1)])
                else:
                    for kt in Tr_und_dic:
                        if len(kt) > 2 and tal.find(kt) > -1:
                            ts = Tr_und_dic[kt].split('+')
                            tal = tal.replace(kt, ts[random.randint(0, len(ts) - 1)])

                if tal not in tot[-1]:
                    tot[-1] += '+' + tal

            if len(rel_gn[kk]) == 1:
                te = se.def_cn
                while te[0] in ['属性','属性值']:  # 这里也不需要属性
                    te.remove(te[0])
                tot[-1] += (kk + '这' + se.def_cn[0])
                kkk = se.def_trans_groups()[0]
                tal = ''
                if not kkk:
                    continue
                while len(kkk.split('.')) > 2:
                    #print('kkk',hownet_group_dict)
                    if hownet_group_dict[kkk]:
                        tal = hownet_group_dict[kkk]
                        break
                    else:
                        kkk = kkk.replace('.' + kkk.split('.')[-1],'')   # 截掉最后一截
                if tal != '':
                    for s in s_dic:
                        tal = tal.replace(s,s_dic[s])
                    tal = '小萌觉得:' + kk + tal + '\n'
                    talk += tal
                    for rs in tal.split(','):
                        rn = rs.split('|')[-1]
                        for dd in hownet_group_dict:
                            if hownet_group_dict[dd]:
                                if rn == dd.split('.')[-1]:
                                    tal = '小萌的常识:因为' + kk + rs +'所以它又能' + hownet_group_dict[dd] + '\n'
                                    break
                        for s in s_dic:
                            tal = tal.replace(s, s_dic[s])
                    talk += tal

    print(tot)
    for t in tot:
        t = t.strip('+')
        st = t.split('+')
        if len(st) > 1:
            total += st[random.randint(0,len(st)-1)] + '，'
        else:
            total += t + '，'
    talk += '小呆的理解:' + total.strip('，') + '\n'
    print(talk)
    return (talk)






if __name__ == "__main__":
    hncc_ana('春夜喜雨')

    pass
