import re
import sys
import collections
import json
import jieba.posseg as pseg
import random

qt_v = ['可以','能','能够','可能','不能','真的','骗人','可靠','不行','不会 ']


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


def s_c(str1,str2): #数相同的字数，两边重复也计入
    sa = ''
    for cc in range(0,len(str1)):
        p = str2.find(str1[cc])
        if p > -1:
            sa += str1[cc]
            try:
                str2 = str2[:p] + str2[p+1:]
            except:
                print(str2,p)
    return(sa)

def s_p(str1,str2): #数相同的字数，两边重复也计入
    if len(str1) < 6:
        if str2.find(str1) > -1:
            return(str1)
    sa = str2 [str2.find(str1[0]):str2.rfind(str1[-1])+1]
    if sa == "":
        print(str2,'\n*****************',str1)
    return(sa)






class du_to_du(object):

    def read_txt(i_f):  # 度鱼四分类改造
        same_s = [] #与问题高度相关的句子
        Du_dic = {}  # 度鱼的原dic
        Du_dic['data'] = []
        du_lines = ''
        with open(i_f, 'r', encoding='UTF-8') as f:

            js = [0, 0, 0, 0, 0]  # 各种计数
            fjs = [0, 0, 0]  # 循环计数
            lines = f.readlines()
            last_qu = ''
            documents = []
            answers = []
            for line in lines:
                case = json.loads(line)
                question = case['question'] #除了取出question与上一case对比之外，其它数据最后才取出并更新
                answers.append(case['answer'])
                if question != last_qu:  # 发现了新的问题，则为上一段添加类型4，无关的训练数据,这时在处理上一case的数据
                    t4_l = int((len(answers)+1) / 2)  # 按一半比例添加第四类(yn无关)的训练数据
                    cws = pseg.cut(last_qu)
                    ws = []
                    for w,f in cws:
                        ws.append((w,f))

                    add = 0
                    for doc in documents:
                        if add >= t4_l:
                            break
                        title = doc['title']
                        t_q = s_c(last_qu,title)

                        for sent in doc["paragraphs"]:
                            if add >= t4_l:
                                break

                            for sen in re.split(r'[。！!?]]',sent):
                                if add >= t4_l:
                                    break
                                if len(sen) < 5:
                                    sen = title + '：' + sen


                                if_vs = False  # 如果有相同的动词就跳过

                                if len(t_q)*100/len(last_qu) > 60:  # 当title和que高度接近时，句子中出现情态动词就很可能有关联，不选
                                    for qt in qt_v:
                                        if sen.find(qt) > -1:
                                            if_vs = True
                                            break
                                if if_vs:
                                    continue


                                for w, f in ws: #que中的主动词出现在sen中，很可能关联，不用

                                    if f=='v'or f =='d':
                                        if w in qt_v: #情态动词留下，可以，能这些
                                            continue
                                        else:

                                            if w in sen:
                                                if_vs = True
                                                break
                                if if_vs:
                                    continue

                                s_l = s_c(last_qu, sen)  # 数相同字数，最大公共子串

                                for an in answers:
                                    s_an = s_c(last_qu,sen)
                                    if len(s_an)*100/len(an) > 85: #排除与答案相似的
                                        if_vs = True
                                        break
                                    else:
                                        if len(s_l)*100/len(last_qu) < 30:
                                            if js[0] < 12:
                                                print(s_l,last_qu)
                                            case_a = {}

                                            case_a['answer'] = title + '：' + sen
                                            case_a['yesno_answer'] = 'no_op'
                                            case_a['question'] = last_qu
                                            case_a['id'] = js[0]
                                            Du_dic['data'].append(case_a)
                                            du_lines += json.dumps(case_a,ensure_ascii=False) + '\n'
                                            js[1] += 1
                                            js[0] += 1
                                            add += 1
                                            break
                                        elif len(s_l)*100/len(last_qu) > 60:
                                            same_s.append(title + ':' + sen)
                                            js[-1] += 1

                    documents = case['documents'] # 更新文档，清零重新记录回答
                    question = case['question']
                    answers = []
                    answers.append(case['answer'])
                    last_qu = question
                case['id'] = js[0]
                du_lines += line
                Du_dic['data'].append(case)
                js[0] += 1

                #if js[0] > 500:
                    #break
                if js[0] %100 == 0:
                    print(js[0])

            print(js[0],js[1],js[3])
            with open('du++train.json', 'w', encoding='UTF-8') as f1:
                f1.write(du_lines)
                f1.close()
            with open('du+_train.json', 'w', encoding='UTF-8') as f2:
                json.dump(Du_dic, f2, ensure_ascii=False, indent=1)
                f2.close()
            with open('same.txt', 'w', encoding='UTF-8') as f3:
                f3.write(str(same_s))
                f3.close()


    def words_dusts ():  #在训练集a和q中各抽取n和非n词汇个500个，共 2000，存入两文件

        with open("e:/个人赛数据集/train.json", 'r', encoding='UTF-8') as f:
            aw_dic = collections.OrderedDict()
            qw_dic = collections.OrderedDict()
            js = [0, 0, 0, 0, 0]  # 各种计数
            fjs = [0, 0, 0]  # 循环计数
            lines = f.readlines()
            answers = []
            last_qu = ''

            for line in lines:
                case = json.loads(line)
                question = case['question'] #除了取出question与上一case对比之外，其它数据最后才取出并更新
                answers.append(case['answer'])
                aaws = pseg.cut(case['answer'])
                for w, f in aaws:
                    if f == 'x':
                        continue
                    if w == '的':
                        continue
                    if w not in aw_dic:
                        aw_dic[w] = {}

                        aw_dic[w]['times'] = [1,0,0,0]
                        aw_dic[w]['flag'] = f
                    else:
                        aw_dic[w]['times'][0] += 1
                    ind = ['Yes', 'No', 'Depends'].index(case['yesno_answer']) + 1
                    aw_dic[w]['times'][ind] += 1


                if question != last_qu:  # 发现了新的问题，则为上一段添加类型4，无关的训练数据,这时在处理上一case的数据
                    qqws = pseg.cut(last_qu)
                    for w,f in qqws:
                        if f == 'x':
                            continue
                        if w == '的':
                            continue
                        if w not in qw_dic:
                            qw_dic[w] = {}
                            qw_dic[w]['times'] = [1,0,0,0]
                            qw_dic[w]['flag'] = f
                        else:
                            qw_dic[w]['times'][0] += 1
                        ind = ['Yes', 'No', 'Depends'].index(case['yesno_answer']) + 1
                        qw_dic[w]['times'][ind] += 1
                last_qu = case['question']
                fjs[0] += 1
                if fjs[0] % 100 ==0:
                    print(fjs[0])



            aw_dic = sorted(aw_dic.items(),key = lambda x:x[1]['times'],reverse=True)
            qw_dic = sorted(qw_dic.items(),key=lambda x:x[1]['times'],reverse=True)


            la = ''
            lq = ''
            la_n = ''
            lq_n = ''
            iiv = 0
            iin = 0
            for key in aw_dic:
                if iin > 100 and iiv > 300:
                    break
                if key[1]['flag'] == 'n':
                    if iin > 100:
                        continue
                    la_n += key[0]  + json.dumps(key[1]) + '\n'
                    iin += 1
                elif iiv > 300:
                        continue
                else:
                    la += key[0]  + json.dumps(key[1]) + '\n'
                    iiv += 1


            iiv = 0
            iin = 0
            for key in qw_dic:
                if iin > 100 and iiv > 300:
                    break
                if key[1]['flag'] == 'n':
                    if iin > 100:
                        continue
                    lq_n += key[0]  + json.dumps(key[1]) + '\n'
                    iin += 1
                elif iiv > 300:
                    continue
                else:
                    lq += key[0] + json.dumps(key[1]) + '\n'
                    iiv += 1

            with open('aw300.json', 'w', encoding='UTF-8') as f:
                # json.dump(aw_dic, f, ensure_ascii=False, indent=1)
                f.write(la +'\n' + la_n)
                f.close()
            with open('qw300.json', 'w', encoding='UTF-8') as f1:
                # json.dump(qw_dic, f1, ensure_ascii=False, indent=1)
                f1.write(lq + '\n' + lq_n)
                f1.close()


    def wm_dusts(): # 使用words_dusts获得的1000*2的常用词汇，进行搭配统计，构成一个简易的yn模型,在a中各种类型的词语搭配，分别对应的y-n-d答案
        w_list = [[], [], [], []]  # 四中类型top500词
        t_v = ['可以', '能', '是', '就是', '有', '会', '需要', '要', '应该', '能够', '喜欢', '只能', '只有']  # 肯定情态动词  TV-NV  不限于V
        f_v = ['不要', '不能', '不是', '没有', '不可', '不会', '骗子', '骗人', '错误', '不行', '不可', '不应']
        d_w = ['当然', '条件', '情况', '但是', '但']  # depends的标志词
        with open("aw300.json", 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            for line in lines:
                if len(line) < 5:
                    continue

                case= json.loads('{' + line.split('{')[1])
                if case['flag'] != 'n':
                    w_list[0].append((line.split('{')[0]))
                else:
                    w_list[1].append((line.split('{')[0]))
            f.close()

        with open("qw300.json", 'r', encoding='UTF-8') as f1:
            lines = f1.readlines()
            for line in lines:
                if len(line) < 5:
                    continue
                case = json.loads('{' + line.split('{')[1])
                if case['flag'] != 'n':
                    w_list[2].append((line.split('{')[0]))
                else:
                    w_list[3].append((line.split('{')[0]))
            f1.close()

        #生成a-q/n-非n各top500之后，统计数据集中的搭配
        with open("e:/个人赛数据集/train.json", 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            wm_dic = collections.OrderedDict()  #词语搭配（模型）字典

            YN_words = ''
            ii = 0
            for line in lines:
                case = json.loads(line)
                question = case['question'] #除了取出question与上一case对比之外，其它数据最后才取出并更新
                qqws = pseg.cut(question)
                qvnas = []  #记录q里的名词动词
                for w,f in qqws:
                    if w in f_v:
                        YN_words += 'FV+'
                    elif f[0]=='v' or f[0]=='n' or f=='a':
                        qvnas.append(w)
                if YN_words != '':
                    YN_words = YN_words[:-1] + '|'

                # YN_words = YN_words.strip('+') + '|'
                aaws = pseg.cut(case['answer'])
                for w,f in aaws:
                    if w in t_v:   # 一下识别情态动词
                        iw = 'TV'
                        if YN_words !='':
                            if YN_words[-2:] =='不+':
                                iw = 'FV'
                                YN_words = YN_words[:-2]
                        YN_words += iw + '+'
                    elif w in f_v:
                        YN_words += 'FV+'
                    elif w in d_w:
                        YN_words += 'D+'
                    elif f[0] == 'v':
                        if ('+++' +YN_words)[-2] != 'V':
                            YN_words += 'V+'
                    elif w in qvnas:  #如果对上q里的vna词性，都做分类
                        if ('+++' + YN_words)[-2] != 'Q':
                            YN_words += 'Q'  + '+'

                YN_words = YN_words.strip('+')
                if len(YN_words.split("+")) > 15:
                    YN_words = '15ws+'

                if YN_words not in wm_dic:
                    wm_dic[YN_words] = {}
                    wm_dic[YN_words]['times'] = [0,0,0]

                ind = ['Yes', 'No', 'Depends'].index(case['yesno_answer'])
                wm_dic[YN_words]['times'][ind] += 1
                ii += 1
                YN_words = ''
                if ii % 100 == 0:
                    print(ii)



            wma_dic = sorted(wm_dic.items(), key=lambda x: x[1]['times'][0]+x[1]['times'][1]+x[1]['times'][2], reverse=True)
            wmb_dic = sorted(wm_dic.items(), key=lambda x: max(x[1]['times'][0] , x[1]['times'][1] , x[1]['times'][2])/(x[1]['times'][0] + x[1]['times'][1] + x[1]['times'][2]),reverse=True)

            save_wma = ''
            save_wmb = ''
            ii = 0
            for wm in wma_dic:
                # if wm[1]['times'][0] + wm[1]['times'][1] + wm[1]['times'][2] < 5:
                    # continue
                save_wma += wm[0] + json.dumps(wm[1]) + '\n'
                if ii > 1000:
                    break
            ii = 0
            for wm in wmb_dic:
                if wm[1]['times'][0] + wm[1]['times'][1] + wm[1]['times'][2] < 5:
                    continue
                save_wmb += wm[0] + json.dumps(wm[1]) + '\n'
                if ii > 1000:
                    break

            test11k (save_wma)

            with open('wm1001.json', 'w', encoding='UTF-8') as f:
                # json.dump(aw_dic, f, ensure_ascii=False, indent=1)
                f.write(save_wma + '\n')
                f.close()
            with open('wm0+1001.json', 'w', encoding='UTF-8') as f1:
                # json.dump(qw_dic, f1, ensure_ascii=False, indent=1)
                f1.write(save_wmb + '\n')
                f1.close()

    def test11k(a=''):
        w_list = [[], [], [], []]  # 四中类型top500词
        t_v = ['可以', '能', '是', '就是', '有', '会', '需要', '要', '应该', '能够', '喜欢', '只能', '只有']  # 肯定情态动词  TV-NV  不限于V
        f_v = ['不要', '不能', '不是', '没有', '不可', '不会', '骗子', '骗人', '错误', '不行', '不可', '不应']
        d_w = ['当然', '条件', '情况', '但是', '但']  # depends的标志词
        if a=='':
            with open('wm1001.json', 'r', encoding='UTF-8') as f:
                lines = f.readlines()
                for line in lines:
                    a += line + '\n'
                f.close()

        with open('test-result.txt', 'r', encoding='UTF-8') as f:
            # json.dump(aw_dic, f, ensure_ascii=False, indent=1)
            lines = f.readlines()
            fix_lines = ''
            ft = [0,0,0]  #修改问答
            ii = 0
            for line in lines:
                YN_words = ''
                case = json.loads(line)
                question = case['question'] #除了取出question与上一case对比之外，其它数据最后才取出并更新
                wm = a.split('\n')
                qqws = pseg.cut(question)
                qvnas = []  # 记录q里的名词动词


                for w, f in qqws:  # 以下再次生成问题的搭配
                    if w in f_v:
                        YN_words += 'FV+'
                    elif f[0] == 'v' or f[0] == 'n' or f == 'a':
                        qvnas.append(w)
                if YN_words != '':
                    YN_words = YN_words[:-1] + '|'

                aaws = pseg.cut(case['answer'])

                for w, f in aaws:
                    if w in t_v:  # 一下识别情态动词
                        iw = 'TV'
                        if YN_words != '':
                            if YN_words[-2:] == '不+':
                                iw = 'FV'
                                YN_words = YN_words[:-2]
                        YN_words += iw + '+'
                    elif w in f_v:
                        YN_words += 'FV+'
                    elif w in d_w:
                        YN_words += 'D+'
                    elif f[0] == 'v':
                        if ('+++' + YN_words)[-2] != 'V':
                            YN_words += 'V+'
                    elif w in qvnas:  # 如果对上q里的vna词性，都做分类
                        if ('+++' + YN_words)[-2] != 'Q':
                            YN_words += 'Q' + '+'

                YN_words = YN_words.strip('+')
                if len(YN_words.split("+")) > 15:
                    YN_words = '15ws+'



                for m in wm:
                    if len(m) < 5:
                        continue

                    yndl = json.loads('{' + m.split('{')[1])['times']

                    if YN_words == m.split('{')[0]:
                        maxid = yndl.index(max(yndl[0],yndl[1],yndl[0]))
                        if yndl[maxid] < 2:
                            break

                        if yndl[maxid] * 100 / (yndl[0]+yndl[1]+yndl[0]) > case['probs'] * 100 -5:
                            ora = case['yesno_answer']
                            ft[0] += 1
                            print('check',ft[0])
                            if ora != ['Yes', 'No', 'Depends'][maxid]:
                                case['yesno_answer'] = ['Yes', 'No', 'Depends'][maxid]
                                ft[1] += 1
                                print('fix',ft[1])
                                break

                fix_lines += json.dumps(case) + '\n'
                ii += 1

                if ii % 100 == 0:
                    print(ii)



        with open('fixtest11k.txt', 'w', encoding='UTF-8') as f1:
            # json.dump(qw_dic, f1, ensure_ascii=False, indent=1)
            f1.write(fix_lines + '\n')
            f1.close()
        print(ft[0],ft[1])

class du_to_drcd(object):
    qas_texts = ['肯定的依据是Ж', '否定的依据是Ж', '看情况的依据是Ж','']

    def make_drcd():
        js = [0, 0, 0, 0, 0]  # 各种计数
        fjs = [0, 0, 0]  # 循环计数

        Dr_dic = {}  # drcd的dic
        Dr_dic['encoding'] = 'UFT-8'
        Dr_dic['data'] = []
        data_dic = {}   # 依次建立各级主干dic和列表值，在此汇总描述，后边反复新建
        data_dic['paragraphs'] = []
        Duodata = []
        with open('/home/lxz/阅读理解比赛/个人赛数据集/zhidao.train.json','r',encoding='UTF-8') as f:
            lines = f.readlines()
            for line in lines:
                if len(line) < 5:
                    continue
                try:
                    case = json.loads(line)
                    if case['question_type'][0:3]=='YES':
                        Duodata.append(case['question'])
                except:
                    print(line)
                    continue

            f.close()
        print(len(Duodata))

        ii = 0
        with open('/home/lxz/阅读理解比赛/个人赛数据集/train.json', 'r', encoding='UTF-8') as f1:
            lines = f1.readlines()
            act_qu = ''

            for line in lines:
                if len(line) < 5:
                    continue
                case = json.loads(line)
                if len(case['answer']) > 100:
                    continue
                if case['question'] != act_qu:
                    if_m = False
                    act_qu = case['question']
                    for o_q in Duodata: # 老度鱼数据
                        if o_q == case['question']:
                            if_m = True
                            break
                        elif len(s_c(o_q,case['question']))/len(case['question']) > 0.8:
                            if_m = True

                            break


                if not if_m:
                    ii += 1
                    continue


                max_sa = 0
                mcs = ''
                d_p = [0,0]  # doc-para循环位置
                tdp = [0,0]  # 指示最大相似所在的doc-para
                for doc in  case['documents']:
                    d_p[1] = 0
                    for pa in doc['paragraphs']:
                        if len(pa) < 8:
                            pa = doc['title'] +  ':' + pa
                        if len(case['answer']) < 6:
                            if case['answer'][-1] in '!！，,。':
                                case['answer'] = case['answer'][:-1]
                            if pa.find(case['answer']) > -1:
                                max_sa = 1
                                tdp[0] = d_p[0]
                                tdp[1] = d_p[1]
                                mcs = case['answer']
                                break
                            else:
                                d_p[1] += 1
                                continue

                        lcs = LCS(case['answer'],pa)
                        if len(lcs)/len(case['answer']) > max_sa:
                            max_sa = len(lcs)/len(case['answer'])
                            tdp[0] = d_p[0]
                            tdp[1] = d_p[1]


                            mcs = lcs
                        if max_sa > 0.9:
                            break
                        d_p[1] += 1
                    if max_sa > 0.9:
                        break
                    d_p[0] +=1

                if max_sa > 0.75:
                    para_dic = {}
                    para_dic['id'] = case['id']
                    para_dic['context'] = ''
                    para_dic['qas'] = []
                    try:
                        para_dic['context'] = case['documents'][tdp[0]]['paragraphs'][tdp[1]]
                    except Exception as e:
                        print(len(last_ds),tdp)
                        print(e)
                    if len(para_dic['context']) < 8:
                        para_dic['context'] =  case['documents'][tdp[0]]['title']  + para_dic['context']
                    thisan = s_p(mcs, para_dic['context'])
                    para_dic['context'] += '。回答(没有答案)。观点选项有(是的)，(不是)，(看情况)。'
                    js[0] += 1
                    for qu in du_to_drcd.qas_texts:
                        qu_dic = {}
                        qu_dic['id'] = str(para_dic['id']) + '-' + str(du_to_drcd.qas_texts.index(qu))

                        qu_dic['question'] = case['question'].strip('?') + '?' + qu
                        an_dic = {}
                        # if du_to_drcd.qas_texts.index(qu) == ['Yes','No','Depends'].index(case['yesno_answer']):
                            #an_dic["text"] = thisan
                        if qu =='':
                            an_dic["text"] = ['(是的)','(不是)','(看情况)'][['Yes','No','Depends'].index(case['yesno_answer'])]
                        else:
                            continue
                            an_dic["text"] = "(没有答案)"
                        an_dic["answer_start"] = para_dic['context'].find(an_dic["text"])
                        if an_dic["answer_start"] == -1:
                            print('wwwwwwww\n', qu_dic['question'],'::',an_dic["text"],'\n',para_dic['context'])
                            continue
                        qu_dic['answers'] = [an_dic]
                        para_dic['qas'].append(qu_dic)
                        js[1] += 1
                else:
                    continue

                data_dic['paragraphs'].append(para_dic)

                ii += 1
                if ii % 100 == 0:
                    print(ii)


        Dr_dic['data'] .append(data_dic)
        with open('dutodr_zhidao.dev.json', 'w', encoding='UTF-8') as f3:
            json.dump(Dr_dic, f3, ensure_ascii=False, indent=1)
            f3.close()
        print(ii,js)


#du_to_du.read_txt("e:/个人赛数据集/train.json")
#du_to_du.words_dusts()
# du_to_du.wm_dusts()
# du_to_du.test11k()
du_to_drcd.make_drcd()