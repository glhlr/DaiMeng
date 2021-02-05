
# -*- coding: utf-8 -*-
# import paddle.fluid as PF
import re
import sys
import collections
import json
import jieba.posseg as pseg
import random

def longSubStr(str1,str2):    #算最大公共子串
    len1 = len(str1)
    len2 = len(str2)
    longest,start1,start2 = 0,0,0
    c = [[0 for i in range(len2+1)]for i in range(len1+1)]
    for i in range(len1+1):
        for j in range(len2+1):
            if i == 0 or j == 0:
                c[i][j] = 0
            elif str1[i-1] == str2[j-1]:
                c[i][j] = c[i-1][j-1]+1
            else:
                c[i][j] = 0
            if (longest < c[i][j]):
                longest = c[i][j]
                start1 = i-longest
                start2 = j-longest
    return str1[start1:start1+longest],start1,start2

def LCS(s1, s2):   #
    size1 = len(s1) + 1
    size2 = len(s2) + 1
    # 程序多加一行，一列，方便后面代码编写
    chess = [[["", 0] for j in list(range(size2))] for i in list(range(size1))]
    for i in list(range(1, size1)):
        chess[i][0][0] = s1[i - 1]
    for j in list(range(1, size2)):
        chess[0][j][0] = s2[j - 1]
    # print("初始化数据：")
    # print(chess)
    for i in list(range(1, size1)):
        for j in list(range(1, size2)):
            if s1[i - 1] == s2[j - 1]:
                chess[i][j] = ['↖', chess[i - 1][j - 1][1] + 1]

            elif chess[i][j - 1][1] > chess[i - 1][j][1]:
                chess[i][j] = ['←', chess[i][j - 1][1]]
            else:
                chess[i][j] = ['↑', chess[i - 1][j][1]]
    # print("计算结果：")
    # print(chess)
    i = size1 - 1
    j = size2 - 1
    s3 = []
    while i > 0 and j > 0:
        if chess[i][j][0] == '↖':
            s3.append(chess[i][0][0])
            i -= 1
            j -= 1
        if chess[i][j][0] == '←':
            j -= 1
        if chess[i][j][0] == '↑':
            i -= 1
    s3.reverse()
    # return ("最长公共子序列：%s" % ''.join(s3),aa)
    return ''.join(s3)


def fix_du(i_f):   #天厨度鱼中的YSE_no问题，加上逗号才能被json.load读取
    add=''
    with open(i_f, "r", encoding='utf-8') as f:
        lines = f.readlines()
        print('open json as txt',len(lines),'行')
        la_li = ''  #如果不带},记录上一行
        ii = 0
        for li in lines:

            if li[-2]=='}':
                if la_li != '':
                    li += la_li
                    la_li = ''
                if li.find('YES_NO') > -1:
                    add += li[:-1] + ',\n'
                    ii += 1
                    print('YES_NO',ii)

            else:
                la_li += li
                continue
    with open('YN1.dev.json', 'w+', encoding='UTF-8') as f2:
        f2.write(add)
        f2.close()

def _read_json(input_file):   #在此研究度鱼训练集到drcd训练集的转换
    YN = []
    with open(input_file, "r", encoding='utf-8') as f:
        input_data = json.load(f)
        an_fix = 0
        l_sp = 0
        ans = 0
        dh = 0
        find0 = 0
        find = 0
        s_an = []
        s_title = []

        for QA in input_data['data']:
            for an in QA['answers']:
                if len(an) > 4:
                    continue
                elif an not in s_an:
                    s_an.append(an)
                    for doc in QA['documents']:
                        for p in doc['paragraphs']:
                            if p.find(an) > -1 and len(p) < len(an)*3:
                                if len(doc['title'])>0:
                                    if doc['title'][-1]=='吧':
                                        print(doc['paragraphs'])
                                        print(an)
                                        s_title.append(QA['question']+'::'+p +'::' + an)
        print(len(s_an),s_an)
        print(len(s_title),s_title)
        return
        for QA in input_data['data']:
            for an in QA['answers']:

                f_an = ''  # 准备修改an
                an.replace('，',',')
                if an[-1] in '。，！':
                    an = an[:-1]
                if len(an) < 5:
                    an = QA['question'] + an
                ans += 1
                an_p = ''
                for doc in QA['documents']:
                    for p in doc['paragraphs']:
                        if p.find(an) > -1:
                            an_p += p
                            find0 += 1
                if an_p =='':  #直接找不到就重新用最大公共子序列匹配一遍
                    l_sp += len(an)
                    # for sp in re.split('[,，!。？；的这]',an):
                    rec = [None,'',0,0,0] # 记录当前para,lcs最长的para号和小段序号,字符
                    for doc in range(len(QA['documents'])):
                        para = QA['documents'][doc]['paragraphs']
                        for p in range(len(para)):
                            if len(para[p]) < 5:
                                para[p] += QA['documents'][doc]['title']

                            lcs = LCS(an, para[p])  #最大公共子序列

                            if len(lcs) < 3 :
                                continue
                            if len(lcs) < len(rec[1]):  # 记录最大的lec字长，字长相等p短也胜出
                                continue

                            elif rec[0]:
                                if len(lcs) == len(rec[1]) and len(para[p]) >= len(rec[0][rec[4]]):
                                    continue
                            if not rec[0] or rec[3] != doc:  #更新para
                                rec[0] = para
                                rec[3] = doc
                            rec[4] = p  #更新P号
                            rec[1] = lcs
                    #暂且用lcs在小p中最前到最后一个字符来作为drcd答案
                    if not rec[0]:
                        an_fix += 1
                        continue
                    p_s = rec[0][rec[4]]
                    try:
                        f_an = p_s[p_s.find(rec[1][0]):p_s.rfind(rec[1][-1])+1]
                    except:
                        print('wrong!!!!!',p_s,rec[1],QA['answers'])
                    if f_an != '':
                        find += 1
                    else:
                        an_fix += 1
                    print(an)
                    print(rec[1],len(rec[1])*100/len(an))
                    # print(QA['question'], QA['answers'], QA['yesno_answers'])
                    print(p_s.find(f_an),f_an)
            print(ans,an_fix,find,find0)
            if ans > 500:
                break


def biyu_ana(re_biyu=None,big_sent=None):
    if not(re_biyu and big_sent):
        return None
    biyu_ele = ['','','','',big_sent]  # 要找出比喻的四个元素，比喻句、喻体、主体、类似的性质，字面上不一定都有
    re_head = '(好似|如同|好比|仿佛|[好俨]?([象像跟和同]|如[^果今]))'
    re_tail = '[一那这模][样般么]|样子|似的|般'
    stop_ws = ['是','能够','可以','可能','不能','在于','极','能','有着','就','虽然','完全']
    last_ss = '' #上个小句子
    ccc = 0  #对小句子的首字位置计数
    for small in re.split(r'[，,;；！!？?|]', big_sent):

        if len(small) < 6:
            if len(last_ss) < 7:
                ccc += len(last_ss)
            last_ss = big_sent[ccc:min(len(big_sent),ccc+len(small)+1)]
            continue
        if  len(last_ss) < 7:
            small = (last_ss + small)
        if small.find(re_biyu.group()) > -1:
            head = re.search(re.compile(re_head),small) #用头尾的正则匹配，来确定喻体的区间
            if head:
                if head.group().find('如')>-1  and head.group().find('如同')==-1:  #处理这个正则带来的位置混乱
                    sma=small.replace(head.group(),'如同'+head.group()[1:])
                    biyu_ele[4] = biyu_ele[4].replace(small,sma)
                    small=sma
                    head = re.search(re.compile(re_head), small)
            tail = re.search(re.compile(re_tail),small) #没找到尾部，小句子的尾部就是喻体的尾部
            if not(head or tail):
                continue
            biyu_ele[0] = small  #小句子作为比喻句
            
            ws = pseg.cut(small)  # 引入词性，形容词很可能是相似属性
            part = 0
            w_p= [[],[],-1]  # 分词和词性排好队,最后的int是当前词语的位置累进(尾部)
            e_b = ['','']  # 元素搜索时对上一截备份，如果最后为空则还原

            for word, flag in ws:
                # if small.find('利息') > -1:
                    # print('------------------', word, flag,biyu_ele[1])
                w_p[0].append(flag)
                w_p[1].append(word)
                w_p[2] += len(word)
                if head and tail:
                    if (w_p[2]-len(word)+1>=head.span()[0] and w_p[2]-len(word)+1<head.span()[1]) or (w_p[2]>=head.span()[0] and w_p[2]<head.span()[1]): # head和tail切成三块
                        if small.find('利息') > -1:
                            print('h_t_head',word,flag,head.span())
                        part = 1
                        continue
                    if word==tail.group():
                        part = 2
                        continue
                    if part==0 and flag[0] in 'nrvi':  #各部分通常对应
                        if len(w_p[0]) >1:
                            if (flag[0]=='u' and (w_p[0][-2][0] not in 'av')) or flag in 'xjv' or word in '还就也都':   #这些符号或副词介词的那个往往在语句中切分语块
                                e_b[1] = biyu_ele[2]
                                biyu_ele[2] = ''
                                if flag =='v' and w_p[0][-2] != 'v':
                                    biyu_ele[2] += word + ' '
                                continue
                        biyu_ele[2] += word + ' '

                    if part==1:
                        biyu_ele[1] += word + ' '

                    if part > 0 and flag[0] in 'az':
                        biyu_ele[3] += word + ' '
                        biyu_ele[1].replace(word+' ','')
                    if part==2 and flag[0] in 'nv' and len(w_p[1])>2:  #本体后置
                        if w_p[1][-3]==tail.group() and w_p[1][-2]=='的' :
                            part==0
                            biyu_ele[2] = word + ' '

                elif not tail:
                    if (w_p[2] - len(word) + 1 >= head.span()[0] and w_p[2] - len(word) + 1 < head.span()[1]) or (
                            w_p[2] >= head.span()[0] and w_p[2] < head.span()[1]):  # head和tail切成三块
                        # print('head::',word, flag)
                        part = 1
                        continue
                    if part==0:
                        if (flag[0] in 'u' and (w_p[0][-1][0] not in 'adv')) or flag in 'xjv' or word in '还就也都':   #这些符号或副词介词的那个往往在语句中切分语块
                            e_b[1] = biyu_ele[2]
                            biyu_ele[2] = ''
                            if len(w_p[0]) > 1:
                                if flag =='v' and (w_p[0][-2][0] != 'v'): #非连续动词，也抛弃前边
                                    biyu_ele[2] += word + ' '

                                continue
                        biyu_ele[2] += word + ' '
                    if small.find('利息') > -1:
                        print('sssssssssss', head.span(), w_p[2], part)
                    if part > 0:   #只有头部标志时，贴近头部后边的是喻体
                        if flag[0] in 'nvri':
                            biyu_ele[1] += word + ' '

                            if flag[0] in 'az':
                                biyu_ele[3] += word + ' '

                elif not head:
                 # 此时本体喻体可能混在一起，如果多个n，尝试从喻体中分出本体
                    if word==tail.group():
                        part=2
                        continue

                    if part==0:
                        if (flag[0]=='u' and (w_p[0][-1][0] not in 'av')) or flag in 'xjv' or word in '还就也都':   #这些符号或副词介词的那个往往在语句中切分语块
                            e_b[0] = biyu_ele[1]
                            biyu_ele[1] = ''
                            if len(w_p[0])>1:
                                if flag =='v' and (w_p[0][-2][0] != 'v'):
                                    biyu_ele[1] += word + ' '
                            continue
                        biyu_ele[1] += word + ' '

                    if part>0 and flag[0] in 'rnv':
                        biyu_ele[2] += word + ' '
                    if flag[0] in 'az':
                        biyu_ele[3] += word + ' '
                        biyu_ele[1].replace(word + ' ', '')
            if small.find('利息') > -1:
                print('bbbbbbbbbb', word, flag, biyu_ele)

            for st in stop_ws:
                biyu_ele[2]= (' ' + biyu_ele[2]).replace(' ' +st+' ' ,'').strip(' ') + ' ' # 既要清理空格又需要后边有一个空格
                e_b[0] =  (' ' + e_b[0]).replace(' '+st+' ' ,'')
                e_b[1] = (' ' + e_b[1]).replace(' ' + st + ' ', '')
            if biyu_ele[1] == '':
                biyu_ele[1] = e_b[0]
            if biyu_ele[2] == '':
                biyu_ele[2] = e_b[1]

        last_ss = big_sent[ccc:min(len(big_sent),ccc+len(small)+1)] #本体很可能留在上一小句子，留下备用
        ccc +=len(small)+1

        if biyu_ele[1] !='':   #完成第一个比喻句就撤退，避免混乱
            if biyu_ele[1][0] in ',，"“':
                print(biyu_ele[1])
            break


    return biyu_ele


def search_biyu(base_f='biyu1.json',add_f=''):
    # 从一个新的txt文档中找出比喻句子，存入json文件，将用于
    biyus = {}
    with open(base_f, 'r', encoding='UTF-8') as f0:
        biyus=json.load(f0)

    # gb18030
    try:
        with open(add_f,'r',encoding='gb18030') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(add_f, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
    re_list = ['([象像跟]|如[^果今]).{1,12}([一那这模][样般么]|样子)','[又还就好][象像]|[^现大雕石塑][象像][一个根把杯只]|好似|如同|好比|仿佛|[^类相近形]似的']


    for i in range(len(lines)):
        if len(lines[i])<3:
            continue
        big_s = re.split(r'[。！]|\.\.\.',lines[i])  #大句子切割
        for big in big_s:
            if_f = False
            big = big.strip('\n').replace(' ','').replace('\n','')
            for re_s in re_list:
                if if_f:
                    break
                ss = re.compile(re_s)
                biyu = re.search(re.compile(re_s),big)
                if biyu:
                    b_a = biyu_ana(biyu,big)  # 分析比喻句的主体喻体和相似属性。
                    if b_a[0]=='':
                        continue
                    if 2699 < len(biyus) < 2800:
                        print(b_a)
                    if b_a[0]=='':
                        print(biyu.group())

                    if b_a[0] != '':
                        by_v = [big,b_a[1]]
                        if b_a[0] in biyus:
                            if b_a not in biyus[b_a[0]]:
                                biyus[b_a[0]].append(b_a[1:])
                        else:
                            biyus[b_a[0]] = [b_a[1:]]
                        if_f =True

    with open('biyu.txt', 'w', encoding='UTF-8') as f2:
        f2.write(str(biyus).replace(']]',']]\n'))
        f2.close()
    with open('biyu1.json', 'w', encoding='UTF-8') as f3:
        json.dump(biyus,f3)
        f3.close()
    print(len(biyus))

def dytodrcd(YN=None,id=0): #转换度鱼到drcd的单个docment  to paragraphs
    if not YN:
        return None

    qas_texts = ['肯定的依据是Ж', '否定的依据是Ж', '看情况的依据是Ж']
    paras = []
    aa = 0
    for an in YN['answers']:  #多出一个问题训练yesno
        bb = 0
        yn_q = YN['question']

        # qus = [] 上一级是它，按照训练集构造字典的列表，['para']的value列表,
        q_a = {}  # 问答节点，本流程返回后添加到上一级
        q_a['id'] = str(YN['question_id']) + '-' + str(aa)
        q_a['context'] = ''
        q_a['qas'] = []

        qas_item = {}  # 为一个度鱼answer，准备一个回答的字典
        qas_item['id'] = q_a['id'] + '-' + str(aa)
        try:
            yn_i = ['Yes','No','Depends'].index(YN['yesno_answers'][aa])  # 用三种观点代号去提取文本,组成完整的问题
        except:
            continue

        qas_item['question'] = yn_q.strip('？') + '？' + qas_texts[yn_i]
        qas_item['answers'] = [{}]

        f_an = ''  # 准备修改的an
        an_p = ''  # 寻找drcd所在段落
        f_args = ['','',False]  # 打包答案修订，0修改的an，1用于drcd的段落，2是否找到
        an.replace('，', ',')  #答案和段落里的中英文逗号恰好相反
        if an[-1] in '。，！':
            an = an[:-1]
        if len(an) > 100:
            print(an)
            continue

        for doc in YN['documents']:
            p_list = doc['paragraphs']
            p_list.insert(0,doc['title'])
            for p in p_list:
                if p.find(an) > -1:
                    if len(an) < 5:
                        if len(p) > len(an) * 10:
                            continue
                        p = doc['title'] + '，' + an
                        an = p
                    f_args[0] = an
                    f_args[1] = p.strip('。') + '。回答是（没有答案）。观点选项（是的），（不是），（不一定）。'
                    break
        if f_args[0] != '':
            qas_item['id'] = q_a['id'] + '-' + str(bb)
            q_a['context'] = f_args[1]
            qas_item['answers'][0]['text'] = f_args[0]
            start = f_args[1].find(f_args[0])
            if start == -1:
                f_args[0] = f_args[0][:-1]
                start = f_args[1].find(f_args[0])
            qas_item['answers'][0]['answer_start'] = start

            bb += 1
        # 直接找不到就重新用最大公共子序列匹配一遍
        else:
            # for sp in re.split('[,，!。？；的这]',an):
            rec = [None, '', 0, 0, 0]  # 记录当前para,lcs最长的para号和小段序号,字符
            for doc in range(len(YN['documents'])):   #  注意这里的doc和p都不一样是数字
                pps = YN['documents'][doc]['paragraphs']
                pps.insert(0,YN['documents'][doc]['title'])
                for p in range(len(pps)):
                    if len(pps[p]) < 5:
                        pps[p] += YN['documents'][doc]['title']

                    lcs = LCS(an, pps[p])  # 最大公共子序列

                    if len(lcs) < 3:
                        continue
                    if len(lcs) < len(rec[1]):
                        continue

                    elif rec[0]: # 记录最大的lec字长，字长相等时p短也胜出
                        if len(lcs) == len(rec[1]) and len(pps[p]) >= len(rec[0][rec[4]]):
                            continue
                    if not rec[0] or rec[3] != doc:  # 更新para
                        rec[0] = pps
                        rec[3] = doc
                    rec[4] = p  # 更新P号
                    rec[1] = lcs
            # 暂且用lcs在小p中最前到最后一个字符来作为drcd答案
            if not rec[0]:
                continue

            p_s = rec[0][rec[4]].strip('。').strip('。').strip('。')
            try:
                f_args[0] = p_s[p_s.find(rec[1][0]):p_s.rfind(rec[1][-1]) + 1]
            except:
                print('wrong!!!!!', p_s, rec[1], QA['answers'])
            if f_args[0] != '':
                if len(rec[1]) * 100 / len(an) < 40:
                    continue
                if len(p_s) < 10:
                    p_s =  YN['documents'][doc]['title']
                q_a['context'] = p_s + '。回答是（没有答案）。观点选项（是的），（不是），（不一定）。'
                qas_item['id'] = q_a['id'] + '-' + str(bb)
                qas_item['answers'][0]['text'] = f_args[0]
                start =  q_a['context'].find(f_args[0])
                if start > -1:
                    qas_item['answers'][0]['answer_start'] = start
                else:
                    print(f_args[1],(f_args[0]))
                    break
                bb += 1
            else:
                continue

        q_a['qas'] .append(qas_item)
        for qq in qas_texts: #增加（找不到答案）的训练数据，注意为防止比例失衡，随机扔掉了一半
            if q_a['qas'][0]['question'].find(qq) > -1 :
                continue
            if   random.randint(0,1) ==0:
                continue
            no_an = {}
            no_an['id'] = q_a['id'] + '-' + str(bb)
            no_an['question'] = yn_q.strip('?') + '？' + qq
            no_an['answers']=[{}]
            no_an['answers'][0]['text'] = '（没有答案）'
            no_an['answers'][0]['answer_start'] = q_a['context'].find('（没有答案）')
            q_a['qas'].insert(random.randint(0,1),no_an)
            bb += 1


        YN_qa = {}   #增加（找不到答案）的训练数据，增加直接询问的问题
        YN_qa['id'] = q_a['id'] + '-' + str(bb)
        YN_qa['question'] = yn_q.strip('?') + '？'
        YN_qa['answers'] = [{}]
        try:
            YN_qa['answers'][0]['text'] = ['（是的）','（不是）','（不一定）'][yn_i]
            YN_qa['answers'][0]['answer_start'] = q_a['context'].find(YN_qa['answers'][0]['text'])
        except:
            print('eeeeeeeeeeeee','数组超标',aa)
            continue
        q_a['qas'].insert(random.randint(0,2),YN_qa)


        aa += 1

        if q_a['qas'] != []:
            paras.append(q_a)
    if paras !=[]:
        return paras,id+aa
    else: return None


def YN_train(sou_f = 'YN1.dev.json',tag_f='YN_dev0123.json'):  #从度鱼训练集改造为drcd训练集
    paras = []
    with open(sou_f, 'r', encoding='UTF-8') as f:
        YNS = json.load(f)
        ii=0
        for YN in YNS['data']:
            #try:
            drcd = dytodrcd(YN,ii)
            #except Exception as e:
                #print(e)
                #continue
            if drcd:
                ii = drcd[1]
                for dd in drcd[0]:  #返回的不止一个para
                    paras.append(dd)

            if ii % 100 < 3:
                # break
                print(ii)


    train = {}
    train['version']= 'v1.3'
    train['encoding'] = 'UTF-8'
    train['data'] = [{}]

    train['data'][0]["paragraphs"] = paras
    with open(tag_f, 'w', encoding='UTF-8') as f3:
        json.dump(train,f3,ensure_ascii=False,indent=1)
        f3.close()




def make_tran(sou_f = 'biyu1.json',tag_f='utrain.json'):  #制造比喻句训练集
    paras = []
    with open(sou_f, 'r', encoding='UTF-8') as f:
        biyus = json.load(f)
        ii = 0

        for key in biyus:
            if len(biyus[key][0])>20:
                print(biyus[key][0])
            qus = []  # 按照训练集构造字典的列表，['para']的value列表
            q_a = {}  # 问答节点
            q_a['id'] = '比喻-'+str(ii)
            q_a['context'] = biyus[key][0][3]
            q_a['qas'] = []

            qas_texts = ['本文中的比喻句是:Ж','@key，这句话中的喻体是Ж','@key,这句话的本体是Ж','@key，这个比喻中的类比属性是Ж']
            by_start = biyus[key][0][3].find(key)
            ans_span = (by_start, by_start + len(key))  # 比喻句在大句子中的首尾位置

            for jj in range(0,4):
                qas_item = {}  # 第0个问题
                qas_item['id'] = q_a['id'] + '-' + str(jj)
                qas_item['question'] = qas_texts[jj].replace('@key',key)
                qas_item['answers'] = [{}]
                if jj==0:
                    qas_item['answers'][0]['text'] = key
                    start0 = biyus[key][0][3].find(key)
                    if start0 ==-1:
                        start0 = biyus[key][0][3].find(key.split(',')[0])
                        print(start0,'0000000000',key,biyus[key][0][3])
                    qas_item['answers'][0]['answer_start'] = start0
                    q_a['qas'].append(qas_item)
                    continue
                if biyus[key][0][jj-1].strip() != '':
                    aw_l = biyus[key][0][jj-1].strip(' ').split(' ')
                    w_b = key.find(aw_l[0]) # 答案得用首尾两词重新拼起来
                    w_e = key.rfind(aw_l[-1])+len(aw_l[-1])
                    qas_item['answers'][0]['text'] = key[w_b:w_e]
                    qas_item['answers'][0]['answer_start'] = ans_span[0] + w_b
                    q_a['qas'].append(qas_item)
            paras.append(q_a)
            ii += 1

    par_dic = {}
    par_dic['paragraphs'] = paras
    par_dic['id']=0
    par_dic['title'] = '比喻'

    data = [ par_dic]
    tran_dic = {}
    tran_dic['version'] = 'v1.3'
    tran_dic['data'] = data

    with open('biyu1.txt', 'w', encoding='UTF-8') as f1:
        f1.write(str(tran_dic).replace(']}', ']}\n'))
        f1.close()
    with open(tag_f, 'w', encoding='UTF-8') as f3:
        json.dump(tran_dic,f3)
        f3.close()


def fftest_json(input_file):   #加逗号
    fix = ''
    with open(input_file, "r", encoding='utf-8') as f:
        lines = f.readlines()
        last = ''
        for li in lines:
            if li.strip()[0]=='}':
                if last.find('id') > -1:
                    li = li.replace('}','},')
                    print(li.strip())
            fix += li
            last = li
    with open('fix.json', 'w', encoding='UTF-8') as f3:
        f3.write(fix)
        f3.close()


def test_json(input_file):
    with open(input_file, "r", encoding='utf-8') as f:
        input_data = json.load(f)
        for QA in input_data['data']:
            abc()
            print ( QA['answer'])



# search_biyu(add_f='西游记.txt')
# make_tran()
# fix_du('E:\dureader_raw/raw/devset/zhidao.dev.json')
test_json('fix.json')
#_read_json('YN.train.json') #从度鱼原版先挑出是非问题，并为每行加了逗号，但改好后还要手工加['data']前的文件头
# YN_train('YN.dev.json') # 调用dytodrcd，计算最大公共子序列，改造成drcd

