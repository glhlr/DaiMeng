# -*- coding:utf-8 -*-

from daimeng.trans_ltp import request_, trans_json
from daimeng.structure import w_ana, sen_ana, ph_ana
from daimeng.sentenceMatch import sentence_match_result
from daimeng.expMean import experience_mean_result

def words_array_gen(ph_obj):
# 分析整段语句，生成词汇阵列
    if(not ph_obj):
        return []
    ph_lst = [] # 词汇阵列
    ph_lst2 = [] # 语义阵列
    for sen_obj in ph_obj.sen_anas:
        sen_lst = []
        semantic_lst = []
        for w_obj in sen_obj.w_anas:
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
                if (w_obj.wo == '，'):
                    semantic_lst.append('标点')
                else:
                    semantic_lst.append(sen_obj.sen_mean[pre_index:equal_index])
            else:
                semantic_lst.append(w_obj.pos)
            sen_lst.append(w_obj.wo)
        ph_lst.append(sen_lst)
        ph_lst2.append(semantic_lst)
    ph_obj.set_words_array(ph_lst)
    ph_obj.set_semantic_array(ph_lst2)
    return ph_lst

def word_count(ph_obj):
    # 返回单词出现的次数及出现位置
    word_dict_count = {} # 词汇频次字典
    word_dict_position = {} # 词汇位置字典
    # 将段落出现的单词存入set集合
    for sen_obj in ph_obj.sen_anas:
        for w_obj in sen_obj.w_anas:
            word_dict_count[w_obj.wo] = 0
            word_dict_position[w_obj.wo] = ''
    # 将单词出现的次数和位置放入两个字典中
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            word_dict_count[word] = word_dict_count.get(word) + 1
            word_dict_position[word] = word_dict_position.get(word)+ '(' + str(i) + ',' + str(j) + ')'
    # 去掉标点符号
    if('：' in word_dict_count):
        word_dict_count.pop('：')
        word_dict_position.pop('：')
    if('！' in word_dict_count):
        word_dict_count.pop('！')
        word_dict_position.pop('！')
    if ('。' in word_dict_count):
        word_dict_count.pop('。')
        word_dict_position.pop('。')
    if ('？' in word_dict_count):
        word_dict_count.pop('？')
        word_dict_position.pop('？')
    if ('“' in word_dict_count):
        word_dict_count.pop('“')
        word_dict_position.pop('“')
    if ('，' in word_dict_count):
        word_dict_count.pop('，')
        word_dict_position.pop('，')
    print(word_dict_count)
    print(word_dict_position)
    return None

def subject_count(ph_obj):
    # 返回主语出现的次数及出现位置
    subject_dict_count = {} # 主语频次字典
    subject_dict_position = {} # 主语位置字典
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            if (ph_obj.get_semantic_array()[i][j] == '主语'):
                key_str = word + '=' + ph_obj.get_semantic_array()[i][j]
                subject_dict_count[key_str] = 0
                subject_dict_position[key_str] = ''
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            if(ph_obj.get_semantic_array()[i][j] == '主语'):
                key_str = word + '=' + ph_obj.get_semantic_array()[i][j]
                subject_dict_count[key_str] = subject_dict_count.get(key_str) + 1
                subject_dict_position[key_str] = subject_dict_position.get(key_str) + '(' + str(i) + ',' + str(j) + ')'
    print(subject_dict_count)
    print(subject_dict_position)
    return None

def object_count(ph_obj):
    # 返回宾语出现的次数及出现位置
    object_dict_count = {} # 宾语频次字典
    object_dict_position = {} # 宾语位置字典
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            if (ph_obj.get_semantic_array()[i][j].find('宾语')>=0):
                key_str = word + '=' + ph_obj.get_semantic_array()[i][j]
                object_dict_count[key_str] = 0
                object_dict_position[key_str] = ''
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            if (ph_obj.get_semantic_array()[i][j].find('宾语')>=0):
                key_str = word + '=' + ph_obj.get_semantic_array()[i][j]
                object_dict_count[key_str] = object_dict_count.get(key_str) + 1
                object_dict_position[key_str] = object_dict_position.get(key_str) + '(' + str(i) + ',' + str(j) + ')'
    print(object_dict_count)
    print(object_dict_position)
    return None

def verb_count(ph_obj):
    # 返回动词出现的次数及出现位置
    verb_dict_count = {} # 动词频次字典
    verb_dict_position = {} # 动词位置字典
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            if (ph_obj.get_semantic_array()[i][j].find('V') >= 0):
                key_str = word + '=' + ph_obj.get_semantic_array()[i][j]
                verb_dict_count[key_str] = 0
                verb_dict_position[key_str] = ''
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            if (ph_obj.get_semantic_array()[i][j].find('V') >= 0):
                key_str = word + '=' + ph_obj.get_semantic_array()[i][j]
                verb_dict_count[key_str] = verb_dict_count.get(key_str) + 1
                verb_dict_position[key_str] = verb_dict_position.get(key_str) + '(' + str(i) + ',' + str(j) + ')'
    print(verb_dict_count)
    print(verb_dict_position)
    return None

def time_count(ph_obj):
    # 返回时间出现的次数及出现位置
    time_dict_count = {}  # 时间词汇频次字典
    time_dict_position = {}  # 时间词汇位置字典
    for sen_obj in ph_obj.sen_anas:
        for w_obj in sen_obj.w_anas:
            if (w_obj.pos.find('时间') >= 0):
                time_dict_count[w_obj.wo] = 0
                time_dict_position[w_obj.wo] = ''
    for i, sen_obj in enumerate(ph_obj.sen_anas):
        for j, w_obj in enumerate(sen_obj.w_anas):
            if (w_obj.pos.find('时间') >= 0):
                time_dict_count[w_obj.wo] = time_dict_count.get(w_obj.wo) + 1
                time_dict_position[w_obj.wo] = time_dict_position.get(w_obj.wo) + '(' + str(i) + ',' + str(
                    j) + ')'
    print(time_dict_count)
    print(time_dict_position)
    return None

def postion_count(ph_obj):
    # 返回地点出现的次数及出现位置
    position_dict_count = {} # 地点词汇频次字典
    position_dict_position = {} # 地点词汇位置字典
    for sen_obj in ph_obj.sen_anas:
        for w_obj in sen_obj.w_anas:
            if(w_obj.cla.find('方位')>=0 or w_obj.cla.find('地理')>=0 or w_obj.cla.find('地域')>=0):
                position_dict_count[w_obj.wo] = 0
                position_dict_position[w_obj.wo] = ''
    for i,sen_obj in enumerate(ph_obj.sen_anas):
        for j,w_obj in enumerate(sen_obj.w_anas):
            if (w_obj.cla.find('方位') >= 0 or w_obj.cla.find('地理') >= 0 or w_obj.cla.find('地域')>=0):
                position_dict_count[w_obj.wo] = position_dict_count.get(w_obj.wo) + 1
                position_dict_position[w_obj.wo] = position_dict_position.get(w_obj.wo) + '(' + str(i) + ',' + str(j) + ')'
    print(position_dict_count)
    print(position_dict_position)
    return None

def verb_class_count(ph_obj):
    # 返回动词类型的次数及出现位置
    verb_class_dict = {}  # 动词频次字典
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            if (ph_obj.get_semantic_array()[i][j].find('V') >= 0):
                if(not verb_class_dict.get(ph_obj.sen_anas[i].w_anas[j].wo)):
                    verb_class_dict[ph_obj.sen_anas[i].w_anas[j].wo] = ph_obj.sen_anas[i].w_anas[j].cla
    print(verb_class_dict)
    return None

def pron_indicate(ph_obj):
# 代词指代内容替换
    for i, row in enumerate(ph_obj.get_words_array()):
        for j, word in enumerate(row):
            current_sign = 1  # 当前句标识，当前句才判断是否有“说”字，如果向上一句查找则不再看“说”字
            if(ph_obj.sen_anas[i].w_anas[j].pos == '代词'):
                if(word == '我' or word == '自己' or word == '本人'):
                    ii = i
                    while(ii>=0):
                        sign_index = -1 #“说”前为我
                        jj = 0
                        # 找到“说”字的位置
                        while(jj<len(row) and current_sign == 1):
                            if(ph_obj.get_words_array()[ii][jj] == '说' or ph_obj.get_words_array()[ii][jj] == '问'):
                                sign_index = jj
                                break
                            jj += 1
                        sign_index -= 1
                        # 从“说”字往前查找
                        while(sign_index>=0):
                            if((ph_obj.get_semantic_array()[ii][sign_index] == '主语'
                                    or ph_obj.get_semantic_array()[ii][sign_index] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '动词'
                                    and (ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('人')>=0
                                        or ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('动物')>=0)):
                                ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][sign_index]
                                ii = -1
                                break
                            sign_index -= 1
                            # 如果没有找到“说”或者“说”字前面没有查找到，则从当前单词开始往前查找
                            if (sign_index <= -1 and current_sign == 1):
                                sign_index = j - 1
                                while (sign_index >= 0 and current_sign == 1):
                                    if ((ph_obj.get_semantic_array()[ii][sign_index] == '主语'
                                         or ph_obj.get_semantic_array()[ii][sign_index] == '宾语')
                                            and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '代词'
                                            and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '动词'
                                            and (ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('人') >= 0
                                                 or ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('动物') >= 0)):
                                        ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][sign_index]
                                        ii = -1
                                        break
                                    sign_index -= 1
                        jj = 0
                        current_sign = 0
                        # 当前句没有查找到，则从前一句开始，从前往后查找
                        while (jj<len(ph_obj.get_words_array()[ii]) and sign_index < -1 and current_sign == 0):
                            if ((ph_obj.get_semantic_array()[ii][jj] == '主语'
                                    or ph_obj.get_semantic_array()[ii][jj] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos != '动词'
                                    and (ph_obj.sen_anas[ii].w_anas[jj].cla.find('人') >= 0
                                         or ph_obj.sen_anas[ii].w_anas[jj].cla.find('动物') >= 0)):
                                ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][jj]
                                ii = -1
                                break
                            jj += 1
                        ii -= 1
                    print(ph_obj.sen_anas[i].sen_in + ' ' + word +'：' + ph_obj.get_words_array()[i][j])
                elif (word == '你' or word == '您'):
                    ii = i
                    while (ii >= 0):
                        sign_index = len(row)  # “说”后为你
                        jj = 0
                        # 找出“说”字的位置
                        while (jj < len(row) and current_sign == 1):
                            if (ph_obj.get_words_array()[ii][jj] == '说' or ph_obj.get_words_array()[ii][jj] == '问'):
                                sign_index = jj
                                break
                            jj += 1
                        sign_index += 1
                        # 从“说”往后查找
                        while (sign_index < len(row)):
                            if ((ph_obj.get_semantic_array()[ii][sign_index] == '主语'
                                    or ph_obj.get_semantic_array()[ii][sign_index] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '动词'
                                    and (ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('人') >= 0
                                         or ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('动物') >= 0)):
                                ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][sign_index]
                                ii = -1
                                break
                            sign_index += 1
                        # 如果没有找到“说”或者“说”字后面没有查找到，则从当前单词开始往前查找
                        if(sign_index>len(row) and current_sign == 1):
                            sign_index = j-1
                            while(sign_index >= 0 and current_sign == 1):
                                if ((ph_obj.get_semantic_array()[ii][sign_index] == '主语'
                                     or ph_obj.get_semantic_array()[ii][sign_index] == '宾语')
                                        and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '代词'
                                        and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '动词'
                                        and (ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('人') >= 0
                                             or ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('动物') >= 0)):
                                    ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][sign_index]
                                    ii = -1
                                    break
                                sign_index -= 1
                        jj = 0
                        current_sign = 0
                        # 当前句没有找到，则从上一句开始，从前往后查找
                        while (jj < len(ph_obj.get_words_array()[ii]) and sign_index > len(row) and current_sign == 0):
                            if ((ph_obj.get_semantic_array()[ii][jj] == '主语'
                                    or ph_obj.get_semantic_array()[ii][jj] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos != '动词'
                                    and (ph_obj.sen_anas[ii].w_anas[jj].cla.find('人') >= 0
                                         or ph_obj.sen_anas[ii].w_anas[jj].cla.find('动物') >= 0)):
                                ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][jj]
                                ii = -1
                                break
                            jj += 1
                        ii -= 1
                    print(ph_obj.sen_anas[i].sen_in + ' ' + word +'：' + ph_obj.get_words_array()[i][j])
                elif(word == '他' or word == '她' or word == '它'):
                    # 当前句从代词开始往前搜，前一句从第一个词开始往后搜
                    ii = i
                    while (ii >= 0):
                        if(current_sign == 1):
                            sign_index = j-1  # 当前代词开始往前搜
                        else:
                            sign_index = -2
                        while (sign_index >= 0 and current_sign == 1):
                            if ((ph_obj.get_semantic_array()[ii][sign_index] == '主语'
                                 or ph_obj.get_semantic_array()[ii][sign_index] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '动词'
                                    and (ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('人') >= 0
                                         or ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('动物') >= 0)):
                                ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][sign_index]
                                ii = -1
                                break
                            sign_index -= 1
                        jj = 0
                        current_sign = 0
                        # 当前句没有搜索到则到前一句从开始进行搜索
                        while (jj < len(ph_obj.get_words_array()[ii]) and sign_index < -1 and current_sign == 0):
                            if ((ph_obj.get_semantic_array()[ii][jj] == '主语'
                                 or ph_obj.get_semantic_array()[ii][jj] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos != '动词'
                                    and (ph_obj.sen_anas[ii].w_anas[jj].cla.find('人') >= 0
                                         or ph_obj.sen_anas[ii].w_anas[jj].cla.find('动物') >= 0)):
                                ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][jj]
                                ii = -1
                                break
                            jj += 1
                        ii -= 1
                    print(ph_obj.sen_anas[i].sen_in + ' ' + word +'：' + ph_obj.get_words_array()[i][j])
                elif(word == '我们' or word == '你们' or word == '他们' or word == '她们' or word == '它们'):
                    # 当前句从代词开始往前搜，前一句从第一个词开始往后搜
                    ii = i
                    pron_count = 0 # 带“们”字的代词数量标识，每搜到一个则+1，搜到2为止
                    ph_obj.words_array[i][j] = ''
                    while (ii >= 0):
                        if (current_sign == 1):
                            sign_index = j - 1  # 当前代词开始往前搜
                        else:
                            sign_index = -2
                        while (sign_index >= 0 and current_sign == 1):
                            if ((ph_obj.get_semantic_array()[ii][sign_index] == '主语'
                                or ph_obj.get_semantic_array()[ii][sign_index] == '并列'
                                or ph_obj.get_semantic_array()[ii][sign_index] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[sign_index].pos.find('名') >=0
                                    and (ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('人') >= 0
                                         or ph_obj.sen_anas[ii].w_anas[sign_index].cla.find('动物') >= 0)):
                                if(ph_obj.words_array[i][j] == ''):
                                    ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][sign_index]
                                else:
                                    ph_obj.words_array[i][j] = ph_obj.words_array[i][j] + '和' + ph_obj.get_words_array()[ii][
                                        sign_index]
                                pron_count += 1
                                if(pron_count >=2 ):
                                    break
                            sign_index -= 1
                        jj = 0
                        current_sign = 0
                        # 当前句没有搜索到则到前一句从开始进行搜索

                        while (jj < len(ph_obj.get_words_array()[ii]) and sign_index < -1 and current_sign == 0):
                            if ((ph_obj.get_semantic_array()[ii][jj] == '主语'
                                or ph_obj.get_semantic_array()[ii][jj] == '并列'
                                or ph_obj.get_semantic_array()[ii][jj] == '宾语')
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos != '代词'
                                    and ph_obj.sen_anas[ii].w_anas[jj].pos.find('名') >= 0
                                    and (ph_obj.sen_anas[ii].w_anas[jj].cla.find('人') >= 0
                                         or ph_obj.sen_anas[ii].w_anas[jj].cla.find('动物') >= 0)):
                                if(ph_obj.words_array[i][j] == ''):
                                    ph_obj.words_array[i][j] = ph_obj.get_words_array()[ii][jj]
                                else:
                                    ph_obj.words_array[i][j] = ph_obj.words_array[i][j] + '和' + ph_obj.get_words_array()[ii][jj]
                                pron_count += 1
                                if(pron_count >= 2):
                                    break
                            jj += 1
                        ii -= 1
                        if(pron_count >= 2):
                            break
                    print(ph_obj.sen_anas[i].sen_in + ' ' + word + '：' + ph_obj.get_words_array()[i][j])
    return None


def logic_sen_count(ph_obj):
    # 返回逻辑句式出现的次数

    return None

def conjunction_search(ph_obj):
    # 返回连词搭配及出现的次数

    return None

