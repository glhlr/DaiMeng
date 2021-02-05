# coding=utf-8

"""
@time: 2019/3/14 16:33
@auther: shaohua
"""

"""
hownet_words_list 读取(r'/home/ubuntu/DaiMeng/data/xmlData/整理.txt')，每个词转为类：HownetWords
        self.word = word  # 单词
        self.gc = gc  # 词性
        self.DEF = de  # 分类
        self.example = example  # 例词
hownet_group_tree 读取知网分类树下的各个文件，转为"syntax.副状.语气"这种形式的list
hownet_group_dict获取分类树中方括号内的内容
hownet_stru_tree 读取“知网-中文信息结构库.txt”，装为类HownetStru的list
HownetWord类，增加属性def_cn
HownetStru类，修改了属性syn_sem_format中的["sem"]的格式。修改了sem查询的规则，导致find_stru的查询规则的修改。
    增加了is_sem()，is_sem_n()两个类方法
find_words()函数，修改了参数的格式，改为word,gc,*def_x，例如：可以直接用find_words("我们")，具体见函数说明
find_stru()函数，修改了参数的格式，sn调整到最前，不定参数*args，根据中文英文分别判断为分类或者词性。

新增函数random_seek1\2,通过1或者2个词查找相应的HownetStru，然后通过speek1\2，提取相关的例词。


"""
import re
from itertools import chain, permutations, product, combinations
from random import choice, seed, shuffle
import chardet

# hownet文件列表
hownet_tree_files = [
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Syntax.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Secondary Feature.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Quantity数量.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Quantity Value数量值.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Event事件.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Event Role && Features.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Entity实体.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Attribute属性.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Attribute Value属性值.txt",
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Converse.txt",  # 反义词
    r"/home/ubuntu/DaiMeng/data/xmlData/hownet分类树\Antonym.txt"
]  # 反义词


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


# 逐行打印list
def l_print(list_x):
    if type(list_x) == str:
        list_x = [list_x]
    for i in list_x:
        print(i)


# 打印list中有重复的项目，及其重复次数
def repeat_print(list_x):
    from collections import Counter
    print([
        str(k) + ':' + str(v) for k, v in dict(Counter(list_x)).items()
        if v > 1
    ])


# y1 y2的交集
def jj(y1, y2):
    return [i for i in y1 if i in y2]


# 多个逻辑值的and运算
def and_func(*bool):
    # print(bool)
    if False in bool:
        return False
    else:
        return True


# 打印出第一组知网的信息。测试用的
def print_stru_firstline():
    for line in lines2:
        if line.find('SYN') != -1:
            stru_x = HownetStru()
            x = re.split(' ', line, 1)
            stru_x.serial = x[0].strip()
            stru_x.syn = re.split('=', x[1], 1)[1].strip()
        elif line.find('SEM') != -1:
            stru_x.sem = re.split('=', line, 1)[1].strip()
        elif line.find('Query') != -1:
            x = re.split(':', line, 1)
            stru_x.qa[x[0]] = x[1].strip()
        elif line.find('Answer') != -1:
            x = re.split(':', line, 1)
            stru_x.qa[x[0]] = x[1].strip()
        elif line.find('例子：') != -1:
            x = re.split('：', line, 1)
            stru_x.example = x[1].strip()
            stru_x.print_stru()
            break


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
        x = [
            find_group(i) if is_chinese(i[0]) else find_group(i[1:])
            for i in self.def_cn
        ]
        x = list(set(x))
        if None in x:
            x.remove(None)

        for j in x:  # 有包含关系的去重复
            for k in x:
                if j in k and j != k:
                    if j in x:
                        x.remove(j)
        return x

    def __str__(self):
        return f"HownetWords({self.word}：{self.gc}，{self.DEF})"

    __repr__ = __str__


# 还没有想好
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

    def __str__(self):
        return f"HS({self.serial})({self.syn})(sem:{self.sem})"

    __repr__ = __str__


# 知网的数据中换行的地方，改成不换行。
def hownet_format(file_lines):
    file_lines2 = []
    line_tag = 'EX'
    line_x = ''
    for line in file_lines:
        if line.find('SYN') != -1:
            line_tag = 'SYN'
            file_lines2.append(line)
        elif line.find('SEM') != -1:
            file_lines2.append(line)
            line_x = line
            line_tag = 'SEM'
        elif line.find('Query') != -1:
            line_tag = 'Que'
            file_lines2.append(line)
        elif line.find('Answer') != -1:
            line_tag = 'Ans'
            file_lines2.append(line)
        elif line.find('例子：') != -1:
            file_lines2.append(line)
            line_x = line
            line_tag = 'EX'
            # elif line_tag == 'EX':
        elif line[0].isdigit() and line_tag == 'EX':
            continue
        else:
            line_x = line_x.replace('\n', '') + line
            file_lines2[-1] = line_x
    return file_lines2


with open(r"/home/ubuntu/DaiMeng/data/xmlData/知网-中文信息结构库.txt", 'r', encoding='UTF-8') as f:
    lines = f.readlines()
lines = [line.strip() for line in lines if line.strip() != '']  # 去掉前后空格已经空行
lines2 = hownet_format(lines)  # 对知网的信息进行整理


# 打开hownet的字典列表，并转为元素为HownetWords的list
def get_hownet_words(file_name):
    # 把知网的一行变成HownetWords()的格式
    def line_trans_class(line):
        line_list = [
            i for i in re.split('(W_C=)|(G_C=)|(DEF=)', line)
            if i != '' and i is not None
        ]  # 按指定的分隔符分割
        # print(line_list)
        word_c = HownetWords(line_list[1].strip(' '), line_list[3].strip(' '))
        if len(line_list) > 4 and line_list[4] == 'DEF=':
            word_c.DEF = line_list[5].replace('\n', '').strip(' ')
        else:
            ls = line_list[3].replace('\n', '').strip(' ')
            ls1 = re.split(' ', ls)
            word_c.DEF = ls1[1]
            word_c.gc = ls1[0]
        if not word_c.gc.isalpha():  # 对gc有中文的部分进行处理，中文部分作为例子放入到example里面
            word_c.example = ''.join([i for i in word_c.gc if not i.isupper()])
            word_c.gc = ''.join([i for i in word_c.gc if i.isupper()])
        word_c.def_cn = word_c.def_trans_list()
        # print(line)
        # if line_list[2] != 'G_C=':
        #     print('xxxxxx')
        return word_c

    # with open(file_name, encoding=get_encoding(file_name)) as f:
    with open(file_name) as f:
        lines = f.readlines()
    return list(map(line_trans_class, lines))


def get_hownet_group(file_name):  # 获取知网的分类树
    # 用于发现group是从第几个自己开始的。
    def group_column(str_x):
        for j, i in enumerate(str_x):
            if i.isalpha():
                return j

    with open(file_name, encoding=get_encoding(file_name)) as f:
        lines = f.readlines()
    new_lines = []
    # 取当前行的分类
    dict_x = {i: [0, ""] for i in range(20)}
    for line in lines:
        # print(line)
        column_x = group_column(line)
        the_group = ''
        cn_break = 0
        for n, m in enumerate(line):
            if is_chinese(m):
                cn_break = n
                break
        for o in line[cn_break:]:
            if is_chinese(o):
                the_group = the_group + o
            else:
                break
        # 处理没有中文的行
        if line == '- Event Role and Features\n':
            the_group = 'EventR&F'
        elif line == '- Secondary Feature\n':
            the_group = "Secondary"
        elif line == "- Converse\n":
            the_group = "Converse"
        elif line == "- Antonym\n":
            the_group = "Antonym"
        elif line == "- syntax\n":
            the_group = "syntax"

        # 处理Converse和Antonym
        if dict_x[0][1] == 'Converse' or dict_x[0][1] == 'Antonym':
            the_group = re.split(
                " +", line)[2].split("|")[-1] + "." + re.split(
                " +", line)[3].split("|")[-1].replace("\n", "")

        # 合并上级分类
        for j in range(20):
            if dict_x[j][0] == 0:
                dict_x[j] = [column_x, the_group]
                # generation_x = j
                this_group = ''

                for k in range(j + 1):
                    this_group = this_group + dict_x[k][1] + "."
                else:
                    this_group = this_group[:-1]
                break
            elif dict_x[j][0] == column_x:
                for l in range(j + 1, 20):
                    dict_x[l] = [0, ""]

                dict_x[j] = [column_x, the_group]
                # generation_x = j
                this_group = ''

                for k in range(j + 1):
                    this_group = this_group + dict_x[k][1] + "."
                else:
                    this_group = this_group[:-1]
                break
        new_lines.append(this_group)
    return new_lines


#  按组把知网的信息，转为元素为HownetStru的list
def hownet_stru_all():
    stru_list = []
    for line in lines2:
        if line.find('SYN') != -1:
            stru_x = HownetStru()
            x = re.split(' ', line, 1)
            stru_x.serial = x[0].strip()
            stru_x.syn = re.split('=', x[1], 1)[1].strip()
        elif line.find('SEM') != -1:
            stru_x.sem = re.split('=', line, 1)[1].strip()
        elif line.find('Query') != -1:
            x = re.split(':', line, 1)
            stru_x.qa[x[0]] = x[1].strip()
        elif line.find('Answer') != -1:
            x = re.split(':', line, 1)
            stru_x.qa[x[0]] = x[1].strip()
        elif line.find('例子：') != -1:
            x = re.split('：', line, 1)
            stru_x.example = x[1].strip()
            stru_x.syn_sem_formating()
            stru_list.append(stru_x)
    return stru_list


#  获取分类树中方括号内的内容
def get_hownet_group_dict(file_name):  # 获取知网的分类树
    dict_x = {}
    with open(file_name, encoding=get_encoding(file_name)) as f:
        lines = f.readlines()
    # new_lines = []
    for line in lines:
        line_split = re.split(' ', line.replace('\n', ''))  # 先用空格分割
        count_x = line_split.count('│')  # '│'的数量
        if line_split[0] == '-':  # 第一行
            root_split = re.split('[|]', line_split[1])  # 第一行的有效部分 用|分割
            if len(root_split) == 1:
                root = root_split[0]  # 如果没有|就取整个内容
            else:
                root = root_split[1]  # 如果有|，取|后面的部分
            this_group = root + r'.'  # this_group准备作为一个常量
            # new_lines.append(root)
            key = root
        else:
            for i, j in enumerate(line_split):
                if j.find('|') != -1:  # 有|的行，取第一个有|的元素
                    child_split = re.split('[|]', j)[1]  # 取|后面的元素（中文的部分）
                    if child_split.find('{') != -1:
                        child_split = child_split[:child_split.find('{')]
                    break
            else:  # 没有|的行
                child_split = line_split[-1]  # 取最后一个元素
            child = ''.join(re.split(
                r'([.])', this_group)[:count_x * 2 + 1]) + '.' + child_split
            this_group = child + '.'
            # new_lines.append(child)
            key = child
        if line.find('[') != -1:
            value = line[line.find('[') + 1:-2]
            dict_x[key] = value
    return dict_x


# 在words_list中查找含有关键词的words
def find_words(word='', gc='', *def_x):
    if len(def_x) == 0:
        def_x = ["|"]
    words_list = hownet_words_list
    if word != '':
        words_list = [i for i in hownet_words_list if i.word == word]
    if gc == 'A':
        gc = 'ADJ'
    if gc != '':
        words_list = [i for i in words_list if i.gc == gc]
    x = [i for i in words_list if and_func(*map(i.is_def, def_x))]
    return x


# 在分类树种查找某个词的分类
def find_group(xx):
    # for i in hownet_group_tree:
    #     if xx in re.split('[.]', i):
    #         # return re.split('[.]', i)
    #         return i
    return next((i for i in hownet_group_tree if xx in re.split('[.]', i)),
                None)


# 在stru_tree中查找含有关键词的stru,前两个参数是sn和是否精确匹配，后面的可变参数是SYN_S和SEM_S的查询参数。
def find_stru(sn='', accurate=True, *args):
    syn_list = [i[0] for i in args
                if i.isalpha() and not is_chinese(i)]  # 取字母出来作为syn（词性）查询关键字
    sem_list = [i for i in args if is_chinese(i[-1])]  # 取中文出来作为sem（分类）查询关键字
    # print(syn_list)
    # print(sem_list)
    if syn_list == []:
        x_list = hownet_stru_tree
    else:
        x_list = [
            i for i in hownet_stru_tree
            if True in map(lambda j: list(j) == i.syn_sem_format["syn"],
                           permutations(syn_list))
        ]

    if sn == "":
        x = [i for i in x_list if i.is_sem(*sem_list)]
    else:
        if accurate:
            x = [i for i in x_list if i.serial == sn]
        else:
            x = [
                i for i in x_list
                if i.serial[:len(sn)] == sn and i.is_sem(*sem_list)
            ]
    return x


# 顺便找一个词，找到适配的HownetStru
def random_seek1(word='', pos=""):
    word_hw_list = find_words(word, pos.upper())
    if len(word_hw_list) == 0:
        print("未找到这个词")
        return None, None
    word_hw = choice(word_hw_list)  # 从查询到的词汇总随机取一个出来用
    # print(word_hw)

    word_stru_list = find_stru("", "", *word_hw.def_cn)
    for i in range(len(word_hw.def_cn), 0, -1):
        word_stru_list = find_stru("", "", *word_hw.def_cn[:i])
        if len(word_stru_list) == 0:
            pass
        else:
            word_hs = choice(word_stru_list)
            # print(word_hs)
            # speek1(word,word_hs)
            return word_hw, word_hs
    else:
        shuffle(word_hw.def_trans_groups())  # 分类list随机排序，完成目标后跳出
        for hs_shuffle in word_hw.def_trans_groups():
            stru_split = hs_shuffle.split(".")
            for i in reversed(stru_split):  # 按分类一级一级往上查询，找到匹配的stru后，随机取一个出来用
                word_stru_list = find_stru(syn1=word_hw.gc, sem1=i)
                if len(word_stru_list) == 0:
                    pass
                else:
                    # print(i)
                    word_hs = choice(word_stru_list)
                    # print(word_hs)
                    # speek1(word,word_hs)
                    return word_hw, word_hs
        else:
            word_hs = None
            print("没找到这个词的分类")  # 不应该出现此类情况
            return word_hw, word_hs


# 两个词,找到适配的HownetStru
def random_seek2(word1='', pos1='', word2="", pos2=""):
    hw1 = find_words(word1, pos1)
    hw2 = find_words(word2, pos2)
    hw_def1 = [i.def_cn for i in hw1]
    hw_def2 = [i.def_cn for i in hw2]
    def_list = list(chain(*[product(*i) for i in permutations([hw_def1, hw_def2], 2)]))
    hw_gc1 = [i.gc for i in hw1]
    hw_gc2 = [i.gc for i in hw2]
    gc_list = list(chain(*[product(*i) for i in permutations([hw_gc1, hw_gc2], 2)]))
    stru_list = []
    for def_x, gc_x in zip(def_list, gc_list):
        # l_print(gc_x)
        # l_print(def_x)
        # print(type(def_x[0]),print(*def_x[0]))
        gc_x1 = list(gc_x)
        if gc_x1[0] == "ADJ":
            gc_x1[0] = "A"
        if gc_x1[1] == "ADJ":
            gc_x1[1] = "A"
        x = [i for i in hownet_stru_tree
             if i.syn_sem_format["syn"][0] == gc_x1[0]
             and i.syn_sem_format["syn"][1] == gc_x1[1]
             and i.is_sem_n(*def_x[0])
             and i.is_sem_n(*def_x[1])
             ]
        stru_list = list(set(stru_list + x))

    return stru_list


def speek1(word_hw, word_hs):  # 和random_seek1配合使用，提取问题和例词
    if word_hw is None or word_hs is None:
        return
    print(word_hs.qa['Query1'])  # 问句1
    example_list = [
        j for j in word_hs.example.split("，") if word_hw.word in j
    ]  # 取的例子，尽量带有原词，如果实在没有的话，就随机选一个出来
    if len(example_list) == 0:
        example_list = [j for j in word_hs.example.split("，") if j != ""]
    print(choice(example_list).replace("-", ""))  # 随机取例句词汇


def speek2(word_hs):  # 和random_seek2配合使用，提取问题和例词
    if not isinstance(word_hs, HownetStru):
        print("需要输入HownetStru类")
        return False
    print(word_hs.qa['Query1'])  # 问句1
    example_list = [j for j in word_hs.example.split("，") if j != ""]
    print(choice(example_list).replace("-", ""))  # 随机取例句词汇
    return True


hownet_words_list = get_hownet_words(r'/home/ubuntu/DaiMeng/data/xmlData/整理.txt')
hownet_group_tree = list(chain(*map(get_hownet_group, hownet_tree_files)))
hownet_stru_tree = [i for i in hownet_stru_all()]
hownet_group_dict = {}
for i in hownet_tree_files:
    # hownet_group_dict.update(xxxx(i))
    hownet_group_dict.update(get_hownet_group_dict(i))


def hn_walk(key='时间'):  # hn漫游，输入一个词，就能P出Hn体系中尽可能多的知识。
    if key == '':
        return None
    means = find_words(key)
    trees = []
    express = ''
    s_dic = {'$': '被', '?': '做成', '+': '可以', '！': '有', '*': '能', '#': '涉及', '^': '不', '~': '或', '[': '属于', ',': '属于'}
    add = ''
    for hn in means:
        t_e = '可做' + hn.gc + '，表示' + str(hn.def_trans_groups())
        if len(hn.def_cn) > 1:
            t_e += '，还有属性:'
            for cn in hn.def_cn[1:]:
                if cn[0] in s_dic:
                    add = s_dic[cn[0]]
                t_e += add + cn + ','
                add = ''
        express += t_e.strip() + '\n'
        ees = []
        syn = []
        for kk in hownet_group_dict:   # 哪些概念与本概念的含义关联
           for tt in hn.def_trans_groups():
                if kk not in ees:
                    if kk.find(tt.split('.')[-1]) > -1:
                        defs = hownet_group_dict[kk].split(',')
                        express += kk
                        for dd in defs:
                            if dd[0] in s_dic:
                                add = s_dic[dd[0]]
                            express += ',' + add + dd
                            add = ''
                        express += '\n'
                        ees.append(kk)
        for sy in find_words('', '', *hn.def_cn):  # 找同类词或下一级概念。
            if sy.word not in syn:
                syn.append(sy.word)
        if len(syn) < 2 and hn.def_cn[-1] == key:
            if len(hn.def_cn) > 1:
                for sy in find_words('', '', *hn.def_cn[:-1]):
                    syn.append(sy.word)
        express += str(hn.def_cn) + '  的同类词共' + str(len(syn)) + '个，例如:' + str(syn[:min(len(syn) - 1, 10)]) + '\n'

        chi = []
        if len(hn.def_cn) > 4:
            for sy in find_words('', '', *hn.def_cn[:-1]):
                chi.append(sy.word)
            express += str(hn.def_cn[:-1])  + '相近词共' + str(len(chi)) + '个，例如::' + str(chi[:min(len(syn) - 1, 10)]) + '\n'

    f_tr = False  # 本key是不是一条分类树，只做一次
    for kk in hownet_group_dict:  # 查找带有该词语的概念   如禽能飞，飞行器能飞
        cs_i = hownet_group_dict[kk].find('|'+key)
        if cs_i > -1:
            cs_str = hownet_group_dict[kk]
            while cs_i > -1:
                if cs_str[cs_i] in s_dic:
                    add = s_dic[cs_str[cs_i]]
                    if cs_str[cs_i-1] in ['^','~']:  # 双操作符
                        add = s_dic[cs_str[cs_i]] + add
                    express += kk + add + key + '\n'
                    break
                cs_i += -1
            if kk not in trees:
                trees.append(kk)
        if kk.split('.')[-1] == key:
            express += key + '是一种hn分类，其分类是:'
            express += kk + '\n'
            f_tr = True
            break

    if f_tr:     #  如果key是分类，再查找这个词的关联词，即不属于key分类，在def_cn的第二项之后
        rela = []

        defs = ''
        for hn in hownet_words_list:
            ds = hn.def_cn
            for f in hn.def_cn:
                if ds.index(f) > 0:
                    if re.match(r'[*#]', f):
                        ds.append(f[1:])

            if key in hn.def_cn:
                if hn.def_cn.index(key) > 0:
                    if hn.word not in rela:
                        rela.append(hn.word)
                    if len(rela) < 10:   # 显示十个词的def_cn
                        defs += hn.word + '::' + str(hn.def_cn) + '\n'
        if len(rela) > 0:
            ex_s = min(len(rela), 10)   # 显示十个词
            express += '关联词共' + str(len(rela)) + '个，例如::' + str(rela[:ex_s]) + '\n'
            express += defs

    print(express)
    under = (means, trees, express)

    return (under)


def w2_rel(sem_str=[]):
    if len(sem_str) < 2:
        return
    m_dic = {}
    for ww in sem_str:
        means = find_words(ww)
        ms = []
        for hn in means:
            if hn.def_cn[0] not in ms:
                ms.append(hn.def_cn[0])
        m_dic[ww] = ms

    pass


def load_dmset(f1='概念.我.xml',no='小萌.设定'):
    p_xml = '/home/ubuntu/DaiMeng/data/xmlData/'
    tree0 = ET.parse(p_xml + f1)
    root = tree0.getroot()
    myset = None
    for t_s in root.iter(no):  #找到节点参数的大XML
        myset = t_s
    if myset:
        for sen in re.split(r'[。！”？\n]|\.\.\.*',myset.text):


    pass




if __name__ == "__main__":
    hn_walk()


    while False:
        # 随机选2个词，提取相关的HownetStru中的例词
        a = choice(hownet_words_list)
        b = choice(hownet_words_list)
        c = random_seek2(a.word, a.gc, b.word, b.gc)
        if len(c) > 0:
            print(a.word, a.gc, b.word, b.gc)
            print(c)
            speek2(choice(c))
        else:
            continue
        print("^" * 70)
        input("请随便输入")
    # l_print(hownet_group_tree)
