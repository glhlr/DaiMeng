# !/usr/bin/python3
# coding=utf-8
'''
百度知道页面。
'''

import webbrowser
import getPage_bdzd as getPage  # 整个项目中，请用import business.getPage as getPage
from bs4 import BeautifulSoup  # 解析html页面代码
import re
import jieba.posseg as pseg


def sim_baidu(s_w):
    #print(111111111111)
    g = getPage.getPage()

    # g.url='https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word=%CE%AA%CA%B2%C3%B4'
    #g.url = 'http://www.baidu.com.cn/s?wd='
    g.url = 'https://zhidao.baidu.com'
    g.url = 'https://www.baidu.com/s'
    #g.url = 'https://www.so.com/s?'
    g.data = {'lm': '0', 'rn': '10', 'pn': '0', 'fr': 'search', 'ie': 'gb18030', 'word': ''}
    g.data['word'] = s_w
    g.dataEncoding = "gb18030"
    # g.data={}

    r = g.requestGet()

    soup = BeautifulSoup (r['HtmlCode'][0],'html.parser')

    par_by = '' #百度搜索到em节点及周边的中文
    i = 0
    wws = pseg.cut(s_w)
    ws = []
    for w, f in wws:
        ws.append((w,f))

    try:
        for br in ['br','em','div']:
            for a in soup.find_all(br):

                m = 0
                cis = []
                aa  = re.split(r'www|http',a.get_text())[0]
                aa = aa.replace(' ', '').replace('\r', '').replace('\n', '')
                if len(aa) < 10:
                    continue

                for w, f in ws:
                    ci = aa.find(w)
                    if ci  == -1:
                        m += 1
                    else:
                        cis.append(ci)  # 记录搜索内容在大句子中的位置 #
                cis.sort()
                print("cccccc",cis)

                aaa = aa[cis[0]:cis[-1]] + aa[cis[-1]]
                i = 0
                for cc in aa[cis[-1]]:
                    if chart < u'\u4e00' or chart > u'\u9fff':
                        i += 1
                    else:
                        i = 0

                    if i[0] > 10:
                        aaa = aaa[:-9]
                        break
                    aaa += cc

                if m < 2 :
                    print('aaaaaaaaaaa',aa)
                    par_by += '\n' + aa
                i += 1
                if len(par_by) > 600:
                    break


    except Exception as e:
        print('爬aidu出错', e, )
        par_by=''  # 此句没有实际用处。不添加异常处理语句，会出现语法错误
    #print(str(par_by))
    #answers[0:charsCount]
    print('soup_dl+++++++++***',i,len(par_by))
    return par_by


def baiduyemian(s_w):
    g = getPage.getPage()
    # g.url = 'https://cn.bing.com/search?q='
    # g.url = 'https://www.sogou.com/web?query='
    # g.url = 'https://www.baidu.com/s'
    g.url = 'https://www.so.com/s'
    g.data = {'cl':'3' }
    g.data = {}
    g.data['q'] = s_w
    g.dataEncoding = "gb18030"
    g.dataEncoding = "utf-8"
    r = g.requestGet()

    soup = BeautifulSoup (r['HtmlCode'][0],'html.parser')
    par_by = ''
    answers = ''
    ws = pseg.cut(s_w)
    i = 0
    for a in soup.find_all('div'):

        if '抱歉，暂时没有找到与' in a:
            continue
        m = 0
        try:
            if i > 27:

                qq = a.get_text().replace(' ', '').replace('\r', '').replace('\n', '').replace('...  - 百度快照','')
                if len(qq) < 10:
                    continue

                for w, f in ws:
                    if qq.find(w) == -1:
                        m  += 1
                if m < 2:
                    qq = re.split(r"www|http|百度|>>",qq)[0]
                    ql = min(12,int(len(qq)/2))
                    if par_by.find(qq[:ql]) > -1 and par_by.find(qq[-ql:]) > -1:
                        continue

                    if re.search(r'回答|答案',qq):

                        if qq.find("最佳答案") > -1:
                            print('dddddddd', qq)
                            answers += qq + "\n"
                            if len(answers) >200:
                                par_by = answers
                                break

                    par_by += '\n' + qq



                if len(par_by) > 1200:
                    break

        except Exception as e:
            print('爬页面出错',e,)
            continue
        i += 1

          # 此句没有实际用处。不添加异常处理语句，会出现语法错误

    print('360搜搜：：',par_by)
    return par_by



if __name__ == '__main__':
    #test()
    s_w='我爱毕竟天安门'
    baiduyemian(s_w)
