#!/usr/bin/python3 
#coding=utf-8
'''
作者：张永涛    
编写时间：2018年11月29日

网络爬虫的获取页面代码包。
输入：请求参数。URL等http头参数
输出：响应状态及获取的数据

'''
from urllib import request as ur
from urllib import error
from urllib import parse

from bs4 import BeautifulSoup   #解析html页面代码

class getPage:
    #URL
    url=""
    #访问页面的头部属性。headers = {'Referrer':'no-referrer-when-downgrade'}
    headers = {}
    #数据。可以是GET、POST。data={'name':'zyt','pwd':'zyt'}
    data={}
    #提交数据的编码方式
    dataEncoding=""

    def __init__(self):
        #定义默认头部
        self.headers['Referrer'] ='no-referrer-when-downgrade'
        self.headers['Connection'] ='keep-alive'
        self.headers['User-Agent'] ='Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        self.dataEncoding="gbk"

    #GET请求
    #附加请求数据字符串。对原URL中是否已经包含了请求数据，做区分处理。
    def requestGet(self):
        #制作GET请求url串。把请求数据转码。附加请求数据。
        #data={'name':'中国','pwd':'zyt'}
        #制作后的URL   http://www.sy139.com?name=%E4%B8%AD%E5%9B%BD&pwd=zyt
        #此处转码格式为gbk。如果抓取的网页不是gbk格式，需要修改
        #判断是否有请求数据。有则附加数据
        if self.data :
            #请求数据不为空
            #判断原有URL串中是否已经附加了参数。以？为标识进行判断
            if self.url.find("?") ==-1 :
                #没有附加参数
                url=self.url+"?"+parse.urlencode(query=self.data,encoding=self.dataEncoding  )
            else:
                url=self.url+"&"+parse.urlencode(query=self.data,encoding=self.dataEncoding  )
            #print("data不为空"+url)
        else:
            #请求数据为空
            url=self.url
            #print("data为空"+url)    
        #print("URL:"+url)
        #return {'StatusCode':'', 'HtmlCode':''}
        #定义请求
        req = ur.Request(url=url,headers=self.headers)
        return self.__request(reqObj=req)



    #POST请求
    def requestPost(self):
        #把post请求数据转化成二进制码
        postData = parse.urlencode(self.data).encode('utf-8')
        #定义请求
        req = ur.Request(url=self.url,headers=self.headers,data=postData)
        return self.__request(reqObj=req)



    def __request(self,reqObj):
        #返回数据{'响应状态':'', '响应页面代码':''}
        r = {'StatusCode':'', 'HtmlCode':''}
        try:
            #打开网页
            httpResponse=ur.urlopen(reqObj,timeout=20)
            pageHtml=""
            if httpResponse.getcode()==200:
                pageHtml=httpResponse.read()
                #获取网页的编码类型
                #查找网页的编码方式<meta http-equiv="content-type" content="text/html;charset=gbk" />
                pageCodeType=self.__findCharset(pageHtml=pageHtml[0:700])
                #为提高效率，没有使用自动获取网页编码类型方法，在此直接写成gbk
                #pageCodeType="utf-8"
                #print("pageCodeType："+pageCodeType)
                r['StatusCode']="200"
                r['HtmlCode']= str(pageHtml, pageCodeType)
                #print(r['HtmlCode'])
            else:
                print("打开网页失败：" + httpResponse.getcode())
                r['StatusCode']=httpResponse.getcode()
                r['HtmlCode']=""
        except error.URLError as e:
            print("网络访问失败(__request(self,reqObj))。报错信息：" + str(e.reason))
            r['StatusCode']=str(e.reason)
            r['HtmlCode']=""
        return r

    #查找网页的编码方式。兼容两种格式的编码写法。
    #格式如下：
    #<meta http-equiv="content-type" content="text/html;charset=gbk" />
    #<meta charset="UTF-8">
    #从网页代码中找出charset=gbk中的gbk。用于网页的转码
    #输入网页代码
    #输出编码方式

    def __findCharset(self,pageHtml):
        #定义网页解析对象。
        #print("出错测试")
        #下面代码会报错：Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.
        #页面编码不一致导致的错误。
        soup = BeautifulSoup(pageHtml, 'html.parser')
        #print(str(soup))
        contentCharset=""
        charset="gbk"
        charset1=None
        charset2=None
        #查找meta遍历
        for content in soup.find_all('meta'):
            #解析第一种格式，如果发现content="text/html;charset=gbk" ，取出gbk
            try:
                if content.get('content').find("charset=") !=-1 :
                    contentCharset=content.get('content')
                    #把text/html;charset=gbk中的text/html;charset替换掉。去掉空格
                    charset1=contentCharset.replace('text/html','').replace(';','').replace('charset=','').strip() 
                if charset1 !=None:
                    break                
            except:
                pass #此句没有实际用处
            #解析第二种格式，如果发现<meta charset="UTF-8">。取出UTF-8
            try:
                charset2=content.get('charset')
                if charset2 !=None:
                    break
            except:
                pass #此句没有实际用处

        #判断编码类型
        if charset1 !=None:
            charset=charset1
        elif charset2 !=None:
            charset=charset2
        #返回gbk
        return charset

