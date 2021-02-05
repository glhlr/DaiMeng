#!/usr/bin/python3 
# coding=utf-8
# http服务本身用接口
import paddle.fluid as fluid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse,unquote
import json
import urllib
import run_mrc
from run_mrc import *
import bdzdqa
import bdzdym
from Grammatical_correction import correction
import jieba.posseg as pseg
import re
import xml.etree.cElementTree as ET
import requests

def gqtojson(context,question):
    jsonff= open('/home/lxz/tnhb/data/test1.json' ,'w+', encoding='utf-8')
    #context="健康减肥卡死的减肥就撒旦福建省地方叫撒地方就撒旦发的附近的萨芬撒大家附近撒旦福建师大犯贱撒娇范围进入文件认为我。"
    #question = "我国是世界上第Ж个能独立发射人造地球卫星的国家。"
    aaa={'version': '1.3', 'data': [{'paragraphs': [{'id': '9999-1', 'context':context , 'qas': [{'question':question, 'id': '9999-1-1', 'answers': [{'text': '答案', 'answer_start': 0, 'id': '1'}]}]}], 'id': '9999', 'title': '历史'}]}
    c=json.dumps(aaa,ensure_ascii=False,indent=4)
    jsonff.write(c)
    jsonff.close()
day = str(time.strftime('%Y%m%d',time.localtime()))
run_mrc.main(args)   #加载模型
mrc_p = ['','（）','Ж','empty','》','[','》','?','？','。']
re_list = ['([象像跟]|如[^果今]).{1,12}([一那这模][样般么]|样子)','[又还就好][象像]|[^现大雕石塑][象像][一个根把杯只]|好似|如同|好比|仿佛|[^类相近形]似的']
# qas_texts = ['本文中的比喻句是:Ж', '@key，这句话中的喻体是Ж', '@key,这句话的本体是Ж', '@key，这个比喻中的类比属性是Ж']
YN_list = ['[吗么][？?]', ' [是能可]否|是不是|会不会|能不能|有没有|行不行|可以不可以|值不值|要不要|好不好']
YN_tails = ['肯定的依据是_', '否定的依据是_', '看情况的依据是_']  # Ж
YN_text = '。回答是（没有答案）。观点选项（是的），（不是），（不一定）。'
re_list = []

def LCS(s1, s2):   #最长公共子序列
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
            gqtojson(str(papa), question)  # 保存test1.json 计算
            three_a = run_mrc.abc()
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



R_t = 0 # 从主入口进入几次，就是摆渡几次
# 模拟请求答案函数。
def test_zyb(question):

    a1 = time.time()  # 初始计时
    #time.sleep(0.3)  # 设置问题间隔时间
    # 1、清理问题
    question = question.replace('+', '')
    question = clear_input(question)  # 将问题疑问部分转换为Ж
    print('清理过字符的问题==', question)

    # 2、 与现有问题库进行相似度计算
    similar_a, similar_par = similar(question)
    similar_a = ''

    if similar_a != '':  # 在3000中有相似并成功计算的的则不为空，直接返回答案

        aa = similar_a
        paqu = similar_par
        fromwhere = '从相似度计算得来'
        a = correction(question, aa)  # 修正后答案
        daily(question, paqu, aa, a, fromwhere)  # 保存日志
        a2 = time.time()
        print('相似度计算计算耗时==', str(a2 - a1), a)
        return a

    else:
        # 3、百度知道计算
        if question.find('Ж') == -1:
            question += ",_"
        print('qqqqqqqqqqqqq',question)
        # bdzd_para = bdzdqa.Query(question)['Answer']  # 百科知道问答的爬取和计算
        bdzd_para0 = bdzdym.sim_baidu(question)  # 百科知道问答的爬取和计算
        bzz = bdzd_para0.strip().replace('\ufeff', '').replace('\u3000', '').replace( '\xa0', '').replace('\n', '').replace('\r', '').replace('\\', '')
        fromwhere = '从百度知道得来'
        if len(bzz) < 100:
            bzz = bdzdym.baiduyemian(question.replace('Ж', '_')).replace('\ufeff', '').replace('\u3000', '').replace(
                '\xa0', '').replace('\n', '').replace('\r', '').replace('\\', '').strip()
            print('搜搜爬取', bzz[:1500])  # 太长就留1500字吧
            fromwhere = '从soso页面得来'
        sp_bzz = re.split(r'[。；！]',bzz)
        bdzd_a = ''
        print(bzz)
        print(len(sp_bzz), '个大句子   ', len(bzz), '字！')

        YNQ = None    #判别是非问题
        for YNR in YN_list:
            YNQ = re.search(re.compile(YNR), question)
            if YNQ:
                break

        if YNQ:  #对Yes_No问题，先找依据再回答，共四次预测
            for tail in YN_tails:

                gqtojson(bzz[:800]+YN_text, question +tail)
                an,an1 = run_mrc.abc(init_check='data/models/step_30000')  #换模型
                if an['text'].find('没有答案') == -1:
                    bdzd_a += '小呆找依据：' + an['text'] + '...'

            try:
                gqtojson(bzz[:min(800,len(bzz))]+YN_text, question)
                yn, yns = run_mrc.abc(init_check='data/models/step_30000')
                if yn['text'] in ['（是的）','（不是）','（不一定）']:
                    bdzd_a += '小萌说了算：' + yn['text'] + '##'
            except Exception as e:
                print (e)
            print(yn, yns)
            print('YN******', bdzd_a)


        else:
            gqtojson(bzz[:min(1500,len(bzz))], question)
            an,ans= run_mrc.abc()
            if len(re.split(r'[。；！]', an['text'])) > 2 or len(an['text']) > 100:
                gqtojson(an['text'], question)
                an, ans = run_mrc.abc()
            print(an, '\n', ans)
            bdzd_a += '小呆会翻书：' + an['text'] + '##'

            if an['text'] in mrc_p:
                wh = 0
                while an['text'] not in mrc_p or wh < len(ans):
                    print('whian::',ans[wh]['text'])
                    bdzd_a = ans[wh]['text']
                    wh += 1

            gqtojson(bzz[:min(1500,len(bzz))],  an['text'] + '_')
            an1, ans1 = run_mrc.abc()
            print(an1, '\n', ans1)
            bdzd_a = bdzd_a[:-2] + '...小萌插一句：'  + an1['text'] + '##'
            print("bdzd_a+++", bdzd_a)


        if bdzd_a != '':  # 百度页面成功解析并输出答案
            a = correction(question, bdzd_a)  # 修正后答案
            daily(question, bzz, bdzd_a, a, fromwhere)  # 保存日志
            a2 = time.time()
            print('baidu页面计算耗时', str(a2 - a1), a)
            return a
        else:
            a = '算了半天还是没有答案'
            baidu_par = '瞅瞅爬到啥' + str(baidu_par)
            fromwhere = '哪儿都没找到'
            daily(question, baidu_par, a, fromwhere)  # 保存日志
            a2 = time.time()
            print('计算耗时', str(a2 - a1), a)
            return a


def fix_prob(ans=[],que='',sp_b=[]):  #预测序列重新评分，有时用
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

            answer = test_zyb(question0)
            Gpt_url = "http://127.0.0.1:8222"
            GptString = requests.get(url=Gpt_url, params=queryString)  # .content.decode('utf-8','ignore')
            print("gptmmi_response::  ", GptString.text)
            an1 = "小萌嘴比脑快::" + eval(GptString.text)['answer'] + "  "

            if answer == "":
                htmlString = '{"rc": 4,"answer": "无结果"}'
            else:
                htmlString = '{"rc": 0,"answer": "' + an1 + answer + '"}'
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
        queryString = self.__queryStringParse(unquote(queryPath.query, 'UTF-8'))
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
            self.wfile.write(bytes(responseText, encoding="UTF-8"))
            print('rrrrrrrrrrrrrr\n',responseText)
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
    address = "192.168.1.51"
    # address="192.168.1.70"
    # 合成地址
    server_address = (address, port)
    httpd = HTTPServer(server_address, HttpServer_RequestHandler)
    print("http服务已启动..." + address + ":" + str(port))

    httpd.serve_forever()
startHttpServer()
