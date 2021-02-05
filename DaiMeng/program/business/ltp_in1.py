##import tkinter as tk
##from tkinter import *
import random
import business.trans_ltp as trans_ltp
from business.trans_ltp import *

import business.get_explanation as get_explanation
import business.hownet_get_db as hownet_get_db
from business.get_explanation import *
from business.phframe_ana import *
from business.hownet_get_db import *

ssi = 0
ti = 0
ra = 0
pa = 0
t_nlu = cla_NLU(cla_dic={'类型': '段落', 'len': 0},)
t_nlu.features={}  # 0号特征就是ph_und

def clickMe():
    global ti
    global ssi
    ti += 1
    inp = e.get()
    ssi += len(re.split(r'[，。！？；]|\.\.\.',inp)) -1
    trans_json(request_(inp))
    t_nlu.member.append(inp)   # 做输入/对话的记录

    phsen_ana = get_phsen()
    act.configure(text = str(ti) + '段:' + str(len(phsen_ana)) + '句')

    t0.delete('1.0','end')
    t1.delete('1.0','end')
    t_A.delete('1.0','end')
    t0.mark_set(INSERT , '2.1')
    t1.mark_set(INSERT , '2.1')
    t_A.mark_set(INSERT , '2.1')
    
    i = 0
    Has_Qu = False
    sn = 0
    for sen in phsen_ana:
        if sn == 0:
            set_d_key(wo = sen.w_anas[0].wo ,pos = sen.w_anas[0].pos,syn=sen.w_anas[0],cla = sen.w_anas[0].cla)  
        sen_result = sentence_match_result(sen.w_anas)
        exp_result = experience_mean_result(sen)
        dsent_list = []
        lsent_list =[]
        if (sen_result):
            trans_ltp.thinking_str += '这句注意=' + sen.sen_in + '意味着=' + str(sen_result[-1])
            dsent_list.append(sen_result.pop(0))
            lsent_list.append(sen_result.pop(0))
            phsen_ana[i].l_form = lsent_list
            phsen_ana[i].d_form = dsent_list

        if exp_result:
            phsen_ana[i].exp_mean = exp_result
        t0.insert(INSERT,sen.sen_mean + '\n')
        t0.insert(INSERT,str(lsent_list) + '\n')
        t0.insert(INSERT,str(dsent_list) + '\n')
        t0.insert(INSERT,str(exp_result) + '\n')
        sn += 1
    Ds_scan()
    fast_scan()

    for sen in phsen_ana:
        disp_wo = ''
        if_Q =False
        Q_if =False
        disp_wo += sen.sen_in
        for w in sen.w_anas:
            if len(disp_wo) < 1200:
                disp_wo +=(w.wo + '::' + w.yuf + '::'+w.pos + '::' + w.wgr + ' :: ' +w.cla + '::' +  w.rel  + '\n')
            if w.pos=='疑问词':
                if_Q = True
                phsen_ana[i].sen_mean = phsen_ana[i].sen_mean.replace('='+ w.wo,'=疑问='+w.wo) #做上疑问标记,=号方便劈开
            elif w.wo == '？':
                Q_if = True
        t1.insert(INSERT,disp_wo)


        if if_Q and Q_if:
            phsen_ana[i].env_mean += ',句式=疑问'
            t0.insert(INSERT,'句式=疑问')
            Has_Qu = True
        i += 1
    ph_und = trans_ltp.get_thisund()


    if Has_Qu:
        Q_res = Query_ana(phsen_ana)
        t_A.insert(INSERT, str(Q_res) + '\n')

    for key in ph_und.Semdic:
        t1.insert(INSERT, key + '扫描：：' + str(ph_und.Semdic[key]) +'\n')
    phase_ana()
    if len(phsen_ana) > 0:
        t_A.insert(INSERT, Thlog_ana())
        t_A.insert(INSERT, Thlog_ana(myexp_ana()))
        t_A.insert(INSERT, Thlog_ana(myexp_ana(no='我的日记')))

    if 'UND' not in t_nlu.features:
        t_nlu.features['UND'] = {}
    t_nlu.features['UND'][inp] = ph_und  # 等完成后，一起收了，注意这是个二维队列，与ph_und平行的还能添加更多的后续分析
    print('ssi' * 5 + '    ' + str(ssi))
    if ssi > 4:
        t_A.insert(INSERT, Thlog_ana(rep_ph_ana(t_nlu)))    # 对话段落每5句再做一次分析。
        ssi = 0


def clickcc():
    e.delete('0','end')
    t0.delete('1.0','end')
    t1.delete('1.0','end')
    t_A.delete('1.0','end')


def clickIt():
    global d_key
    global ra
    ra += 1
    act.configure(text = '随机' + str(ra) +'词')
    if e.get() == '':
        ra_wo = test_random()
    else:
        ra_wo = [e.get().split(' ')[0],get_explans(e.get().split(' ')[0])[0]]
    t1.delete('1.0', 'end')
    t1.mark_set(INSERT , '2.1')
    wo_ex = (ra_wo[0] + ':' + ra_wo[1].strip(' ')).replace('.','=').replace('，','！').replace("|",'').replace(',','！')
    trans_json (request_(wo_ex))
    t1.insert(INSERT, wo_ex + '\n')
    phsen_ana = get_phsen()
    Ds_scan()
    fast_scan()

    hownet_words_list = get_hownet_words(r'/home/ubuntu/DaiMeng/data/xmlData/整理.txt')


    b = [i for i in hownet_words_list if i.word == ra_wo[0]]
    for c in b:
        t_A.insert(INSERT,c.word + c.gc + c.DEF + '\n')
        print(c.word, c.gc, c.DEF)

    sn = 0  #字典返回解释后，0句0词的信息加载为d_key
    wr_in =''
    for sen in phsen_ana:
        print(sen.sen_mean)
        if sn == 0:
            set_d_key(wo = sen.w_anas[0].wo ,pos = sen.w_anas[0].pos,syn=sen.w_anas[0],cla = sen.w_anas[0].cla)  
        sen_result = sentence_match_result(sen.w_anas,js_cla='字典')
        if sen_result:
            t1.insert(INSERT, '内涵知识：' + str(sen_result[-1]) + '\n')
            if ra_wo[0].find(':') == -1:
                wr_in += ',' + str(sen_result[-1])
        sn += 1
    if wr_in != '':
        formatok = True
        cc = 0
        while cc < len(ra_wo[0]):    #检查节点名，不能有特殊字符
            if '._!|/'.find(ra_wo[0][cc]) > -1:
                formatok = False
                break
            cc += 1
        if formatok:
            d_key = get_d_key()
            Gn_audit(d_key, wr_in.strip(','))
    ph_und = trans_ltp.get_thisund()
    for key in ph_und.Semdic:
        t1.insert(INSERT, key + '扫描：：' + str(ph_und.Semdic[key]) + '\n')


def clickThey():
    global d_key
    global pa
    rep_talk()
    return
    pa += 1
    act.configure(text='批刷' + str(pa) + '词')
    f = ''
    if platform.system() == 'Windows':
        f = open("d:/YYY/词林动物1.txt", 'r', encoding='UTF-8')
    else:
        f = open("/home/ubuntu/DaiMeng/data/xmlData/词林动物1.txt", 'r', encoding='UTF-8')

    words = f.readlines()
    for word in words:

        word = word.strip('\n').replace('\ufeff','')
        trans_json(request_(words))
        phsen_ana = get_phsen()
        Ds_scan()
        fast_scan()

        ph_und = trans_ltp.get_thisund()
        for key in ph_und.Semdic:
            t1.insert(INSERT, key + '扫描：：' + str(ph_und.Semdic[key]) + '\n')

        

##inp_ = ''

##in_ = tk.Tk()
##in_.title('输入段落')
##in_.geometry('1200x800')
##e = Entry(in_,width=90,textvariable=inp_)
##e.pack()
##act = tk.Button(in_, text="句子匹配",width=20,   command=clickMe)
##act.place(x=1000, y=20, anchor='nw')
##act_ra = tk.Button(in_, text="查/翻词典", width=20,  command=clickIt)
##act_ra.place(x=1000, y=50, anchor='nw')

##act_cl = tk.Button(in_, text="清除",width=20,  command=clickcc)
##act_cl.place(x=100, y=20, anchor='nw')
##act_go = tk.Button(in_, text="刷",width=20, command=clickThey)
##act_go.place(x=100, y=50, anchor='nw')


#r4=tk.Radiobutton(in_)
#r4.pack(fill=X)

 
##t0=tk.Text(in_,width=100,height=6)
##t0.pack()

##t1=tk.Text(in_,width=100,height=20,font=('Courier New', 11))
##t1.pack()

##t_A=tk.Text(in_,width=100,height=10,font=('Courier New', 11))
##t_A.pack()

     #这里设置文本框高，可以容纳两行



def rep_talk(input='我们出门买橡皮呗'):
    trans_json (request_(input))
    phsen_ana = get_phsen()

    for sen in phsen_ana:
        sen_result = sentence_match_result(sen.w_anas)
        exp_result = experience_mean_result(sen)
        dsent_list = []
        lsent_list =[]
        if (sen_result):
            trans_ltp.thinking_str += '这句注意=' + sen.sen_in + '意味着=' + str(sen_result[-1])
            dsent_list.append(sen_result.pop(0))
            lsent_list.append(sen_result.pop(0))
            phsen_ana[i].l_form = lsent_list
            phsen_ana[i].d_form = dsent_list

        if exp_result:
            phsen_ana[i].exp_mean = exp_result
        break    # 这里干啥忘了，不敢删除那就跑一轮吧
    Ds_scan()
    fast_scan()
    test_dic = {}
    ss = 0
    ph_und = trans_ltp.get_thisund()
    Has_Qu = False # 疑问句指示
    print(trans_ltp.thinking_str)



    for sen in phsen_ana:
        disp_wo = ''
        if_Q = False
        Q_if = False
        disp_wo += sen.sen_in

        for w in sen.w_anas:
            if len(disp_wo) < 500:
                disp_wo += (w.wo + '::' + w.yuf + '::' + w.pos + '::' + w.wgr + ' :: ' + w.rel + '\n')
            if w.pos == '疑问词':
                if_Q = True
                phsen_ana[ss].sen_mean = phsen_ana[ss].sen_mean.replace('=' + w.wo, '=疑问=' + w.wo)  # 做上疑问标记,=号方便劈开
            elif w.wo == '？':
                Q_if = True
        test_dic['句子sn=' + str(ss)] = sen.sen_in + '\n' + sen.sen_mean + '\n'
        test_dic['词汇sn=' + str(ss)] = disp_wo

        if if_Q and Q_if:
            phsen_ana[ss].env_mean += ',句式=疑问'
            Has_Qu = True
        ss += 1



    if len(phsen_ana)>1:
        phase_ana()    # 这里是段落理解的演示，单句无效
        ph_und = trans_ltp.get_thisund()
        print('tttttttttt'+ thinking_str)
        if '回复' in test_dic:
            test_dic['回复'] += Thlog_ana(ph_und.rec[1])
        else: test_dic['回复'] = Thlog_ana(ph_und.rec[1])
    else:    # 这里是分类知识库的搜多，仅限单句


        Thlog_ana(myexp_ana())
        ph_und = trans_ltp.get_thisund()
        if '回复' in test_dic:
            test_dic['回复'] += Thlog_ana(myexp_ana())
        else: test_dic['回复'] = Thlog_ana(myexp_ana())


        if '回复' in test_dic:
            test_dic['回复'] += Thlog_ana(myexp_ana(no='我的日记'))
        else: test_dic['回复'] = Thlog_ana(myexp_ana(no='我的日记'))



    test_dic['扫描'] = str(ph_und.Semdic)
    if len(test_dic['回复']) < 3 :
        ph_und = trans_ltp.get_thisund()
        for key in ph_und.Semdic:
            if key == 'V' :
                for vv in ph_und.Semdic[key]:
                    if vv.find('sn='):
                        continue
                    thinking_str += '重要的'+ vv + '\n'
        test_dic['回复'] += Thlog_ana()
        print(ph_und.Semdic)

    print('***************')
    print(test_dic['回复'])


    test_dic['回复']=test_dic['回复'].replace('\n\n','\n').replace('\n','\nΨ').strip('Ψ')
    test_dic['回复']=test_dic['回复'].replace('\n\n','\n').replace('\n','\nΨ').strip('Ψ')
    return test_dic


    #####从某文件提取一个模板，加上一个根节点a，再写入指定文档
        
        
       # xx=ET.tostring(root.find('阅读场景'),encoding='UTF-8',method="xml")   
        #yy= ET.fromstring(xx)
    
       # yy.find('句式语义').text=wr_logic
       # yy.find('原文').text = wr_sen
       # yy.find('依存句法').text = json_str 
    
       # root.insert(1,yy)
       # tree0.write('d:/xml/预备概念.xml', encoding='UTF-8')

##in_.mainloop()


