#!/usr/bin/python3 
# coding=utf-8


# http服务本身用接口
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import unquote
import urllib
import run_mrc
from run_mrc import *
import bdzdqa
import bdzdym
import gqsavetojson
from Grammatical_correction import correction
import jieba
import jieba.posseg as pseg
import re
import xml.etree.cElementTree as ET


# 清理字符，将长度不一的_改为统一字符Ж。
def clear_input(input_in):
    # 如果开头包含\ufeff'
    if input_in.startswith(u'\ufeff'):
        # 清理开头和末尾字符
        input_in = input_in.encode('utf8')[3:].decode('utf8').strip('\n')
        # 返回结果

        # 将----转为 Ж ，这个词最好不跟前后字发生任何关系
    #print(input_in)
    re_que = '为什么|多少|什么|[哪几何][个一里儿天年月岁时些]|[谁啥哪]'
    if '_' in input_in:
        input_in = input_in.replace('_' * (input_in.count('_')), 'Ж').strip()
    else:
        que_w = re.search(re.compile(re_que), input_in)  # 用头尾的正则匹配，来确定喻体的区间
        if que_w:
            input_in = input_in.replace(que_w.group(),'Ж')
            print('Ж'*8,que_w,que_w.group(),que_w.span())

    #print(input_in)
    # qd装入qd['qsen']={'qr':'修正后的句子'}


    return input_in



def biyu_ana(re_biyu=None, big_sent=None):
    if not (re_biyu and big_sent):
        return None
    biyu_ele = ['', '', '', '', big_sent]  # 要找出比喻的四个元素，比喻句、喻体、主体、类似的性质，字面上不一定都有
    re_head = '(好似|如同|好比|仿佛|[好俨]?([象像跟和同]|如[^果今]))'
    re_tail = '[一那这模][样般么]|样子|似的|般'
    stop_ws = ['是', '能够', '可以', '可能', '不能', '在于', '极', '能', '有着', '就', '虽然', '完全']
    last_ss = ''  # 上个小句子
    ccc = 0  # 对小句子的首字位置计数
    for small in re.split(r'[，,;；！!？?|]', big_sent):

        if len(small) < 6:
            if len(last_ss) < 7:
                ccc += len(last_ss)
            last_ss = big_sent[ccc:min(len(big_sent), ccc + len(small) + 1)]
            continue
        if len(last_ss) < 7:
            small = (last_ss + small)
        if small.find(re_biyu.group()) > -1:
            head = re.search(re.compile(re_head), small)  # 用头尾的正则匹配，来确定喻体的区间
            if head:
                if head.group().find('如') > -1 and head.group().find('如同') == -1:  # 处理这个正则带来的位置混乱
                    sma = small.replace(head.group(), '如同' + head.group()[1:])
                    biyu_ele[4] = biyu_ele[4].replace(small, sma)
                    small = sma
                    head = re.search(re.compile(re_head), small)
            tail = re.search(re.compile(re_tail), small)  # 没找到尾部，小句子的尾部就是喻体的尾部
            if not (head or tail):
                continue
            biyu_ele[0] = small  # 小句子作为比喻句

            ws = pseg.cut(small)  # 引入词性，形容词很可能是相似属性
            part = 0
            w_p = [[], [], -1]  # 分词和词性排好队,最后的int是当前词语的位置累进(尾部)
            e_b = ['', '']  # 元素搜索时对上一截备份，如果最后为空则还原

            for word, flag in ws:
                w_p[0].append(flag)
                w_p[1].append(word)
                w_p[2] += len(word)
                if head and tail:
                    if (w_p[2] - len(word) + 1 >= head.span()[0] and w_p[2] - len(word) + 1 < head.span()[1]) or (
                            w_p[2] >= head.span()[0] and w_p[2] < head.span()[1]):  # head和tail切成三块
                        if small.find('利息') > -1:
                            print('h_t_head', word, flag, head.span())
                        part = 1
                        continue
                    if word == tail.group():
                        part = 2
                        continue
                    if part == 0 and flag[0] in 'nrvi':  # 各部分通常对应
                        if len(w_p[0]) > 1:
                            if (flag[0] == 'u' and (w_p[0][-2][
                                                        0] not in 'av')) or flag in 'xjv' or word in '还就也都':  # 这些符号或副词介词的那个往往在语句中切分语块
                                e_b[1] = biyu_ele[2]
                                biyu_ele[2] = ''
                                if flag == 'v' and w_p[0][-2] != 'v':
                                    biyu_ele[2] += word + ' '
                                continue
                        biyu_ele[2] += word + ' '

                    if part == 1:
                        biyu_ele[1] += word + ' '

                    if part > 0 and flag[0] in 'az':
                        biyu_ele[3] += word + ' '
                        biyu_ele[1].replace(word + ' ', '')
                    if part == 2 and flag[0] in 'nv' and len(w_p[1]) > 2:  # 本体后置
                        if w_p[1][-3] == tail.group() and w_p[1][-2] == '的':
                            part == 0
                            biyu_ele[2] = word + ' '

                elif not tail:
                    if (w_p[2] - len(word) + 1 >= head.span()[0] and w_p[2] - len(word) + 1 < head.span()[1]) or (
                            w_p[2] >= head.span()[0] and w_p[2] < head.span()[1]):  # head和tail切成三块
                        # print('head::',word, flag)
                        part = 1
                        continue
                    if part == 0:
                        if (flag[0] in 'u' and (w_p[0][-1][
                                                    0] not in 'adv')) or flag in 'xjv' or word in '还就也都':  # 这些符号或副词介词的那个往往在语句中切分语块
                            e_b[1] = biyu_ele[2]
                            biyu_ele[2] = ''
                            if len(w_p[0]) > 1:
                                if flag == 'v' and (w_p[0][-2][0] != 'v'):  # 非连续动词，也抛弃前边
                                    biyu_ele[2] += word + ' '

                                continue
                        biyu_ele[2] += word + ' '
                    if small.find('利息') > -1:
                        print('sssssssssss', head.span(), w_p[2], part)
                    if part > 0:  # 只有头部标志时，贴近头部后边的是喻体
                        if flag[0] in 'nvri':
                            biyu_ele[1] += word + ' '

                            if flag[0] in 'az':
                                biyu_ele[3] += word + ' '


                elif not head:
                    # 此时本体喻体可能混在一起，如果多个n，尝试从喻体中分出本体
                    if word == tail.group():
                        part = 2
                        continue

                    if part == 0:
                        if (flag[0] == 'u' and (w_p[0][-1][
                                                    0] not in 'av')) or flag in 'xjv' or word in '还就也都':  # 这些符号或副词介词的那个往往在语句中切分语块
                            e_b[0] = biyu_ele[1]
                            biyu_ele[1] = ''
                            if len(w_p[0]) > 1:
                                if flag == 'v' and (w_p[0][-2][0] != 'v'):
                                    biyu_ele[1] += word + ' '
                            continue
                        biyu_ele[1] += word + ' '

                    if part > 0 and flag[0] in 'rnv':
                        biyu_ele[2] += word + ' '
                    if flag[0] in 'az':
                        biyu_ele[3] += word + ' '
                        biyu_ele[1].replace(word + ' ', '')
            if small.find('利息') > -1:
                print('bbbbbbbbbb', word, flag, biyu_ele)

            for st in stop_ws:
                biyu_ele[2] = (' ' + biyu_ele[2]).replace(' ' + st + ' ', '').strip(' ') + ' '  # 既要清理空格又需要后边有一个空格
                e_b[0] = (' ' + e_b[0]).replace(' ' + st + ' ', '')
                e_b[1] = (' ' + e_b[1]).replace(' ' + st + ' ', '')
            if biyu_ele[1] == '':
                biyu_ele[1] = e_b[0]
            if biyu_ele[2] == '':
                biyu_ele[2] = e_b[1]

        last_ss = big_sent[ccc:min(len(big_sent), ccc + len(small) + 1)]  # 本体很可能留在上一小句子，留下备用
        ccc += len(small) + 1

        if biyu_ele[1] != '':  # 完成第一个比喻句就撤退，避免混乱
            if biyu_ele[1][0] in ',，"“':
                print(biyu_ele[1])
            break

    return biyu_ele


# 提取当前日期，作为保存日志的名称的时间部分
day = str(time.strftime('%Y-%m-%d', time.localtime()))
re_list = ['([象像跟]|如[^果今]).{1,12}([一那这模][样般么]|样子)','[又还就好][象像]|[^现大雕石塑][象像][一个根把杯只]|好似|如同|好比|仿佛|[^类相近形]似的']
re_list = []
# 日志保存目录
# record_file=
# 新建测试文件
gqsavetojson.gqto()
# 加载模型
run_mrc.main(args)
# mrc计算经常错误的结果
mrc_p = ['', '（）', 'Ж', 'empty','》','[','《','？']

def riji_test(que='你喜欢唱歌跳舞吗',f1='概念.我.xml',no='我所知'):   #本模块没用
    p_xml = 'D:/YYY/'
    tree0 = ET.parse(p_xml + f1)
    root = tree0.getroot()

    exp_my = []
    ws = list(jieba.cut(que))
    for exp in root.iter(no):  #找到节点参数的大XML
        myexp = exp
        break
    for ex in myexp:
        sco = 0
        if not ex.text:
            continue
        topic = ex.tag
        if topic == '日记':
            topic += '+' + ex.attrib['标题']
        if topic == '象声词':  # 先放过
            continue
        sp_text = re.split(r'[。；！\n]',ex.text)
        ssp = ''
        for sp in range(len(sp_text)):
            if len(sp_text[sp]) < 3:
                continue
            ssp += sp_text[sp] +'。'
            if len(ssp) < 300 and sp!=len(sp_text)-1:
                continue
            mw = []
            for w in ws:
                if w in ['是','有','了','在','的','，','？']:    #排除太常见的词
                    continue
                if topic.find(w) > -1:
                    sco +=10
                if ex.text.find(w) > -1:
                    if w not in mw:
                        mw.append(w)
                        sco += len(w)

            if sco > 3:
                eee = (topic + '\n' + ssp,sco,mw)
                exp_my.append(eee)
            ssp = ''
            sco = 0

    exp_my= sorted(exp_my, key=lambda x: (x[1]),  # 多个段落的两个答案，重新按可能性排序
                 reverse=True)
    print('exp_my::',exp_my[:3])

    ans = []
    for ex in exp_my[:min(3,len(exp_my))]:
        gqsavetojson.gqtojson(ex[0], que)
        an, an1 = run_mrc.abc()
        an['text'] = an['text'].strip().replace('\'', '').replace('\r', '').replace('\n', '').replace('\"', '')
        if an not in ans:
            ans.append(an)
            ans.append(an1)
    ans = sorted(ans, key=lambda x: (x["probability"]),  # 多个段落的两个答案，重新按可能性排序
                 reverse=True)
    print('ans::',len(ans),ans)
    return ans[0]['text']



# 与现有题库进行相似度匹配
def similar(question):
    # 保存的文件。开始应该初始化为空list文件[],

    # print('file_save_list', file_save_list)

    file_save = open('data/newlist.txt', 'r', encoding='UTF-8').read()
    file_save_list = eval(file_save.replace('\ufeff', ''))
    s_q = question
    same = []
    s_q = s_q.strip('\n')
    for qu in file_save_list:
        qu = qu.strip('\n')
        cut = s_q[0:3]
        if cut.find('Ж') > -1:
            cut = s_q[-4:]
        if qu.find(cut) == -1:
            continue

        if qu == s_q:
            same.append(qu)


        else:
            part = [None, None, None]
            p0 = s_q.find('Ж')
            p1 = qu.find('Ж')
            ques = [None, None]  # ‘Ж’位置在前的放0位，在后放1
            if p0 > p1:
                ques[0] = qu
                ques[1] = s_q
            else:
                ques[1] = qu
                ques[0] = s_q
            part[0] = ques[0][:min(p0, p1)]  # 两个问句靠前那个Ж之前那部分
            part[2] = ques[1][max(p0, p1) + 1:]  # 两个问句靠后那个Ж之后那部分
            p2 = ques[0].find(part[2])  # Ж靠前的句子，找到靠后Ж之后部分位置
            if p2 > -1:
                part[1] = ques[0][min(p0, p1) + 1:p2]
            else:
                # print(part[2], ques[0])
                continue

            p3 = ques[1].find(part[0])
            if p3 == -1:
                # print(part[0],ques[1])
                continue
            p3 = p3 + len(part[0])  # Ж靠后的句子，找到靠前Ж之后部分位置

            part1_2 = ques[1][p3:max(p0, p1) - 1]

            cc_mat = len(part[0]) + len(part[2])
            cc = 0

            while cc in range(0, len(part[1])):
                if part1_2.find(part[1][cc]) > -1:
                    cc_mat += 1
                cc += 1
            if cc_mat > len(qu) * 0.66:
                same.append(qu)
    #如果所问问题不在题库里，则讲新问题存入题库
    if question not in file_save_list:
        file_save_list=list(file_save_list)
        file_save_list.append(question)
        file_save2 = open('data/newlist.txt', 'w+', encoding='UTF-8')
        file_save2.write(str(file_save_list))
        file_save2.close()

    # print('len(file_save_list)', len(file_save_list), file_save_list)
    # if len(Qus)>len(file_save_list):
    if 0 < len(same) :
        #print('len(same)', question, len(same), same)

        # if len(same)==0:

        # 进行模型计算newlist.txt
        try:
            if question in same:
                same.remove(question)
            papa = same[0]
            #print('same第一个==',papa)
            gqsavetojson.gqtojson(str(papa), question)  # 保存test1.json 计算
            three_a = run_mrc.abc()['text'].strip().replace('\'', '').replace('\r', '').replace('\n', '').replace('\"', '')
            print('相似度计算结果==',three_a)
            three_par = papa
        except:
            three_a = ''
            three_par = ''
    else:
        three_a = ''
        three_par = ''

    if three_a in mrc_p or 'Ж'in three_a:
        three_a = ''
        three_par = ''

    # print('lastsame=same',same,len(same))

    #print('three_a=three_par', three_a, three_par)
    return three_a, three_par


# 保存日志
def daily(question, paqu, aa, a, fromwhere):
    dayly = day + '日志.txt'
    record_file = open(dayly, 'a+', encoding='UTF-8')
    record_file.write(question + '\n')
    record_file.write(paqu + '\n')
    record_file.write(str(aa) + '\n')
    record_file.write(str(a) + '\n')
    record_file.write('-' * 50 + fromwhere + '\n')
    record_file.close()


# 百科知道问答的爬取和计算
def baike_js(question):
    question = question.replace('Ж', '_')
    bdzd_rus = bdzdqa.Query(question)

    papa = (bdzd_rus['Answer']).strip().replace('\ufeff', '').replace('\u3000', '').replace(
        '\xa0', '').replace('\n', '').replace('\r', '').replace('\\', '')
    bdzd_par = papa
    bdzd_a = ''
    return bdzd_a, bdzd_par
# 百科知道界面爬取和计算
def bd_ym(question):
    question = question.replace('Ж', '_')
    bdzd_rus = bdzdym.sim_baidu(question)

    papa = bdzd_rus.strip().replace('\ufeff', '').replace('\u3000', '').replace(
        '\xa0', '').replace('\n', '').replace('\r', '').replace('\\', '')
    bdzd_par = papa
    bdzd_a = ''
    return bdzd_a, bdzd_par

# 百科界面爬取和计算
def baidu_ym(question):
    question = question.replace('Ж', '_')
    baidu_rus = bdzdym.baiduyemian(question)

    papa = baidu_rus.strip().replace('\ufeff', '').replace('\u3000', '').replace(
        '\xa0', '').replace('\n', '').replace('\r', '').replace('\\', '')
    print('页面::',papa)
    gqsavetojson.gqtojson(papa, question)
    aresult,b_b = run_mrc.abc()
    baidu_a = aresult['text'].strip().replace('\'', '').replace('\r', '').replace('\n', '').replace('\"', '')
    baidu_par = papa[0:1000]#太长就留1000字吧
    if baidu_a in mrc_p:
        baidu_a = ''
    return baidu_a, baidu_par


# 模拟请求答案函数。
def test_zyb(question):
    print('question::::::::::',question)
    a1 = time.time()  # 初始计时
    #time.sleep(0.3)  # 设置问题间隔时间
    # 1、清理问题
    question = question.strip('+').replace('+', '')
    question = clear_input(question)  # 将问题疑问部分转换为Ж
    print('清理过字符的问题==', question)

    # 2、 与现有问题库进行相似度计算
    similar_a, similar_par = similar(question)

    if similar_a != '':  # 在3000中有相似并成功计算的的则不为空，直接返回答案

        aa = similar_a
        paqu = similar_par
        fromwhere = '从相似度计算得来'
        a = correction(question, aa)  # 修正后答案
        daily(question, paqu, aa, a, fromwhere)  # 保存日志
        a2 = time.time()
        print('相似度计算计算耗时==', str(a2 - a1), a)
        return a
    elif re.search(r'喻体|比喻句|本体',question):
        gqsavetojson.gqtojson(re.split(r'[,，]',question)[0], question)
        an, an1 = run_mrc.abc()
        return an['text']
    else:

        # 3、百度知道计算
        bdzd_aa, bdzd_para = bd_ym(question)
        bdzd_ab, bdzd_parb = baike_js(question)
        bzz=bdzd_para+bdzd_parb
        sp_bzz = re.split(r'[。；！]',bzz)
        print(len(sp_bzz),'个大句子   ',len(bzz),'字！')
        print(bzz)
        len_pa = max(len(bzz)/3,350)
        sp_b = ''
        ans = []
        biyu_talk = ''
        qas_texts = ['本文中的比喻句是:Ж', '@key，这句话中的喻体是Ж', '@key,这句话的本体是Ж', '@key，这个比喻中的类比属性是Ж']
        for sb in range(0,len(sp_bzz)):
            big_s = re.split(r'[。！\n]|\.\.\.', sp_bzz[sb])  # 大句子切割
            if re_list !=[]:
                for big in big_s:
                    for r_b in re_list:
                        biyu = re.search(re.compile(r_b),big)
                        if biyu:
                            b_ana = biyu_ana(biyu,big)
                            if b_ana[0] == '':
                                continue
                            if biyu_talk.find(b_ana[0])>-1:
                                print('break重复')
                                break
                            evals = ['', '', '', '']

                            for ii in range(0,4):
                                b_ana[ii]=b_ana[ii].strip(' ')
                                if b_ana[ii]!= '':
                                    qii = qas_texts[ii].replace('@key',b_ana[0])
                                    gqsavetojson.gqtojson(b_ana[-1], qii)
                                    an, an1 = run_mrc.abc()
                                    evals[ii]=an['text']
                            if biyu_talk.find(evals[0]) > -1:
                                print('break2......')
                                break
                            biyu_talk += '本文中的比喻句有:Ж' + evals[0] + '\n'
                            if b_ana[1]!='' and b_ana[2]!='':
                                bytk = '把@k1比作@k2'.replace('@k1',evals[2]).replace('@k2',evals[1])
                                if b_ana[3]!='':
                                    bytk += '，同样@k3'.replace('@k3',evals[3])
                                biyu_talk += bytk + '\n'
                            print('evals[2]::b_ana[2]',evals[2],len(b_ana[2]),b_ana[2])


            try:
                sp_b += sp_bzz[sb]+'。'
                if len(sp_b) > len_pa or sb==len(sp_bzz)-1:
                    gqsavetojson.gqtojson(sp_b, question)
                    an,an1 = run_mrc.abc()
                    print('ananananana',an,an1)
                    an['text'] = an['text'].strip().replace('\'', '').replace('\r', '').replace('\n', '').replace('\"', '')
                    if an not in ans:
                        ans.append(an)
                        ans.append(an1)
                    sp_b = ''

            except:
                continue

        ans = fix_prob(ans,question,sp_bzz)  # 检查答案所在的每个大句子，包含多少个问题的字词和顺序，调整probability评分
        ans = sorted(ans, key=lambda x: (x["probability"]),  # 多个段落的两个答案，重新按可能性排序
                            reverse=True)
        print(len(ans),'ans::++',ans)

        if len(ans)>0:
            bdzd_a = ans[0]['text']
        else:bdzd_a = ''

        bdzd_par=bzz
        if bdzd_a in mrc_p:
            bdzd_a = ''

        if bdzd_a != '':
            aa = bdzd_a
            paqu = bdzd_par
            fromwhere = '从知道计算得来'
            a = correction(question, aa)  # 修正后答案

            daily(question, paqu, aa, a, fromwhere)  # 保存日志

            a2 = time.time()
            print('知道计算耗时', str(a2 - a1), a)
            return '小呆的查询：' + a + '##'

        else: #4、百度知道没有结果，则进行百度页面爬取
            print('爬百度页面::', question)
            baidu_a, baidu_par=baidu_ym(question)

            if baidu_a in mrc_p:
                baidu_a = ''

            if baidu_a != '':  # 百度页面成功解析并输出答案
                aa = baidu_a
                paqu = baidu_par
                fromwhere = '从baidu页面得来'

                a = correction(question, aa)  # 修正后答案
                daily(question, paqu, aa, a, fromwhere)  # 保存日志
                a2 = time.time()
                print('baidu页面计算耗时', str(a2 - a1), a)
                return a
            else:
                aa = '算了半天还是没有答案'
                a = '算了半天还是没有答案'
                paqu = '瞅瞅爬到啥' + str(baidu_par)
                fromwhere = '哪儿都没找到'
                daily(question, paqu, aa, a, fromwhere)  # 保存日志
                a2 = time.time()
                print('计算耗时', str(a2 - a1), a)
                return a

def fix_prob(ans=[],que='',sp_b=[]):
    ws={}
    for an in ans:  #多个段落中*2个答案，剔重，保留最大的可能性
        if an['text'] not in ws:  #建立备份中计算
            ws[an['text']]=an["probability"]
        else:
            ws[an['text']]=max(an["probability"],ws[an['text']])
    for w in ws:
        sss = 0  # 答案总评分，选多句最大值
        for sb in sp_b:
            ss = 0   # 单句评分
            if sb.find(w) > -1:
                f_c=[]  # 记录所有每句包含问题的连续字符
                t_c=''  # 正在计算被包含的词
                for cc in que:
                    if sb.find(cc)>-1:  # 发现一个包含的字符，就计算连续匹配
                        t_c += cc
                        if sb.find(t_c)==-1:
                            f_c.append(t_c)
                            t_c = ''
                    else:
                        f_c.append(t_c)
                        t_c=''
                for fc in f_c:
                    ss += len(fc) * min(max(1,int(len(fc)/2)),3) #对连续匹配上的字词或词组给与最高为3的加倍
            sss = max(sss,ss)   #挑选包含积分最高的句子

        ws[w] += sss*0.02   #

    r_ans = []

    for w in ws:   # 重新组装答案和评分，返回原格式
        r_ans.append({})
        r_ans[-1]['text'] = w
        r_ans[-1]["probability"] = ws[w]
    return r_ans
# 获取回答文本
# 输入参数：get请求串，POST请求数据（结构为字典）
# 返回输出的html编码字符串。格式为json：{"rc": 0 | 1 | 4,"answer": "1453"}
#
def getAnswer(queryString, queryForm):
    # 提问格式：question={中国}  。获取“中国”
    answer = ""
    # 定义问题变量，默认值为空
    question = ""
    # 返回json格式串。设默认值
    htmlString = '{"rc": 4,"answer": "没有答案"}'
    # 尝试获取问题
    try:
        question = queryString['question']
    except BaseException:
        # 请求参数出错
        htmlString = '{"rc": 2,"answer": "没有发现请求参数question"}'
    else:
        # 去掉请求问题的头尾大括号｛｝
        question0 = CutBeginEndChar(question)
        try:  # 先爬作业帮 没有了就爬百度知道
            # 调用引擎函数，获取答案。编码
            if question0[:2]=='??':
                question0 = question0[2:]
                answer = riji_test(question0)
                print('421::',answer)
            else:
                answer = test_zyb(question0)
            if answer == "":
                htmlString = '{"rc": 4,"answer": "无结果"}'
            else:
                htmlString = '{"rc": 0,"answer": "' + answer + '"}'
        except BaseException as e:
            htmlString = '{"rc": 2,"answer": "请求答案时出错"}'

            print('except:', e)

        else:
            pass


    return htmlString


# 去掉字符串的头尾字符
# 输入格式：{中国}
# 返回格式：中国
def CutBeginEndChar(AllString):
    if AllString[0] == "{":
        AllString = AllString[1:]
    else:
        pass

    if AllString[-1] == "}":
        AllString = AllString[:-1]
    else:
        pass
    return AllString


# 对话请求业务，根据请求路径，分解处理请求。如路径错误，返回错误信息
# 输入参数：get请求串，POST请求数据（结构为字典）
# 返回输出的html编码字符串
def getPage(path, queryString, queryForm):
    # 返回的页面代码
    htmlString = ""
    if path == "/api/query":
        htmlString = getAnswer(queryString, queryForm)
    else:
        # 错误请求路径，回复4。{"rc": 4,"answer": "请求路径错误"}
        htmlString = '{"rc":2,"answer": "请求路径错误"}'
    return htmlString


'''
http服务类
响应GET、POST请求
输出页面代码

'''


class HttpServer_RequestHandler(BaseHTTPRequestHandler):
    '''
    GET请求响应函数。
    先解析页面请求参数。获取请路径、query参数串
    把query参数串转换为dict结构
    调用函数，获取页面代码
    输出页面代码
    '''

    def do_GET(self):
        # 解析网页输入参数
        # url解析。结果：ParseResult(scheme='', netloc='', path='/interface', query='key=ssss', fragment='')
        # 结构为元组
        queryPath = urlparse(self.path)
        # 访问路径。。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        path = unquote(queryPath.path, 'utf-8')
        # query请求数据串。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        # 把串转换成字典格式。输入：key=ssss& 输出：{'key': 'ssss'}
        queryString = self.__queryStringParse(unquote(queryPath.query, 'utf-8'))
        # 由于是GET提交。其POST请求的数据为空。仅用于调用参数
        queryForm = {}
        # 获取输出html代码
        responseText = getPage(path, queryString, queryForm)
        # 输出页面代码
        self.__responseWrite(responseText)

    '''
    POST请求响应函数。
    先解析页面请求参数。获取请路径、FORM参数（dict结构）
    调用函数，获取页面代码
    输出页面代码
    '''

    def do_POST(self):
        # 解析网页输入参数
        # url解析。结果：ParseResult(scheme='', netloc='', path='/interface', params='', query='', fragment='')
        # 结构为元组
        queryPath = urlparse(self.path)
        # 访问路径。。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        path = unquote(queryPath.path, 'utf-8')
        # 由于是POST提交。其GET请求的数据为空。仅用于调用参数
        queryString = {}
        # 获取POST提交的数据
        # {'key': ['aaaaa'], 'key2': ['aaaaa2222']}
        # 结构为字典
        length = int(self.headers['Content-Length'])
        queryForm = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        # 获取输出html代码
        responseText = getPage(path, queryString, queryForm)
        # 输出页面代码
        self.__responseWrite(responseText)

    # 网页输出函数
    # 参数：输出的页面HTML代码，字符串
    def __responseWrite(self, responseText):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(bytes(responseText, encoding="utf8"))
        except IOError:
            self.send_error(404, 'File Not Found: ')

    # queryString解析。
    # 输入参数：queryString串。"key=ssss&key2=ssss222&key3=ssss333"
    # 返回结果：{'key': 'ssss', 'key2': 'ssss222', 'key3': 'ssss333'} 结构为：dict
    def __queryStringParse(self, queryString):
        querstr = queryString.replace("=", "':'")
        querstr = querstr.replace("&", "','")
        if querstr == "":
            querstr = "{}"
        else:
            querstr = "{'" + querstr + "'}"
        dict = eval(querstr)
        return dict


# http服务启动函数

def startHttpServer():
    path1 = os.path.abspath('.')  # 表示当前所处的文件夹的绝对路径
    print("httpServer.py绝对路径：" + path1)
    # 获取参数
    # 临时注释
    # httpConfig=aC.getHttpServerConfig()

    # print(httpConfig.ip)
    # print(httpConfig.port)
    # 端口号
    # port = httpConfig.port  #8000
    port = 8111
    # IP地址
    # address= httpConfig.ip #"192.168.15.138"
    address = "192.168.1.17"
    # address="192.168.1.70"
    # 合成地址
    server_address = (address, port)
    httpd = HTTPServer(server_address, HttpServer_RequestHandler)
    print("http服务已启动..." + address + ":" + str(port))
    httpd.serve_forever()




startHttpServer()
