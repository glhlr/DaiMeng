#!/usr/bin/python3 
#coding=utf-8

import business.busiMaim as bM;
import accessData.accessConfig as aC;
import accessData.writeLog as wLog; #引入填写日志模块
import business.ltp_in as ltp
import business.trans_ltp_ZYT as trLtp
#from trans_ltp import business.trans_ltp as trLtp


from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
import os
from urllib.parse import urlparse
from urllib.parse import unquote
import urllib
import time
import requests
import random
import re

'''
作者：张永涛    
编写时间：2018年9月27日

模块说明
httpServer服务器提供模块。
包含：服务器提供及启动。get、post请求处理。路径分析。相应业务处理。

startHttpServer()：http服务启动及配置。包含IP及端口配置。
class HttpServer_RequestHandler:http服务类。包含get、post请求处理。页面代码输出。get请求字符串解析。
getPage(path,queryString,queryForm)：请求路径分析。根据请求路径，调用不同的处理函数。
getDialog(queryString,queryForm):/dialog请求路径处理函数。返回对话页面的html。
getInterface(queryString,queryForm):/interface请求路径处理函数。返回XML格式数据。

'''


'''


接口请求业务
输入参数：get请求串，POST请求数据（结构为字典）
返回输出的html编码字符串。返回的结果中包含两个信息。一个是“回话”文本，一个是测试信息。
两种信息组织到XML结果中。到客户端后解析。


'''

def getInterface(queryString,queryForm):
    #回答文本
    answerText=" "
    #测试信息
    testInfo=" "
    inp = queryForm['queryText'][0]
    T_rul = "http://127.0.0.1:8222"
    baidu_rul = "http://zzzai.natapp1.cc/api/query" 

    #print ("中华人民共和国")
    #根据请求命令处理返回变量
    if queryForm['queryCmd'][0]=="answerText":
        #如果仅要回话信息，则测试信息为空。
        testInfo=" " #必须加一个空格。否则客户端解析出错。
        #answerText="AJAX测试"+str(queryForm['queryText'])+str(queryForm['queryCmd'])
        #answerText=to_tuling(str(queryForm['queryText'][0]))
        #answerText="测试"
        #访问呆萌系统
        a=ltp.rep_talk(input=str(queryForm['queryText'][0]))
       
        answerText=a['回复']
       

    elif queryForm['queryCmd'][0]=="testInfo":
        #如果仅要测试信息，则回话信息为空。
        #answerText="你好 " #必须加一个空格。否则客户端解析出错。
        answerText=str(queryForm['queryText'][0])
        #模拟测试返回测试信息。一个分词结果。
        #获取分词结果，json格式
        #fc=ltp.fenCiJson(queryForm['queryText'][0])
        #fc="中华人民共和国测试"
        #testInfo="<p>"+fc+"<p>"+fc
        #访问呆萌系统
        a=ltp.rep_talk(input=str(queryForm['queryText'][0]))
    
        testInfo="<p>"+str(a)+"<p>"

    elif queryForm['queryCmd'][0]=="all":
        #访问呆萌系统 
        if random.randint(0,10) < 3 or str(queryForm['queryText'][0])[0]=='@':
            a=ltp.rep_talk(input=str(queryForm['queryText'][0]))
        #回复文本
     
            answerText=a['回复']
        #测试信息
            # testInfo="<p>"+str(a)+"<p>"
        h = {"question": inp}
        try:
            htmlString=requests.get(url=T_rul, params=h)  #.content.decode('utf-8','ignore')
            htmlString.raise_for_status()
        # print('hhhhhhhh\n',htmlString.encoding,htmlString.apparent_encoding,"\n!!!!!!",htmlString.text)
            htmlString.encoding = htmlString.apparent_encoding
            print("\n!!!!!!",htmlString.text)
            answerText  = '小萌::' + re.split('##',eval(htmlString.text)['answer'])[0] + '......' + answerText
		
            htmlString=requests.get(url=baidu_rul, params=h)
            answerText += "...小呆::" + re.split('##',eval(htmlString.text)['answer'])[0]
        except:
            pass
        #如果要全部信息。则分别获取回话信息和测试信息
        #answerText="AJAX测试"+str(queryForm['queryText'][0])+str(queryForm['queryCmd'])
        #获取测试信息。送入参数聊天问话

        #testInfo=trLtp.trans_ltp(queryForm['queryText'][0])
        #testInfo="中国共产党"
        #trans_json (request_(e.get()))
        #fc=ltp.fenCiJson(queryForm['queryText'][0])
        #testInfo="<p>"+str(fc)

    #填写测试时间
    localtime = time.localtime(time.time())
    #testInfo=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"<p>"+testInfo
    #转码。由于返回的结果是以XML方式组织的，所以要避免返回的信息中有“<>”字符。
    #在此的处理方式没有使用urllib提供的unquote()函数。把整个字符串都转码成URL格式（%E4%B8%AD%E5%8D%8E%E4）。
    #而是仅把"<>"两个字符做转换。这样做比较简单。
    #测试过。在服务器端用unquote()转码后，在客户端用unescape()转回后乱码。
    #把“<”替换为“%3C”，把“>”替换为“%3E”
    testInfo=testInfo.replace("<","%3C")
    testInfo=testInfo.replace(">","%3E")




    #返回信息为XML
    #其中包含“回话”文本和测试信息
    htmlString=             "<?xml version='1.0' encoding='utf-8'?>"
    htmlString=htmlString + "<root>"
    htmlString=htmlString + "        <answerText>"+answerText+"</answerText>"
    htmlString=htmlString + "        <testInfo>"+testInfo+"</testInfo>"
    htmlString=htmlString + "</root>"

    #htmlString="AJAX测试"+str(queryForm['queryText'])
    #htmlString="接口queryString:key--"+queryString['key']
    #htmlString  = htmlString+"接口queryData:key--"+queryForm['key']
    return htmlString

def getGPT2Interface(queryString,queryForm):
    answerText=" "
    testInfo=" "
    if queryForm['queryCmd'][0]=="answerText":
        #如果仅要回话信息，则测试信息为空。
        testInfo=" " #必须加一个空格。否则客户端解析出错。
    T_rul = "http://127.0.0.1:8222"
    h = {"question": queryForm['queryText'][0]}
    try:
        htmlString=requests.get(url=T_rul, params=h)  #.content.decode('utf-8','ignore')
        htmlString.raise_for_status()
	# print('hhhhhhhh\n',htmlString.encoding,htmlString.apparent_encoding,"\n!!!!!!",htmlString.text)
        htmlString.encoding = htmlString.apparent_encoding
        print("\n!!!!!!",htmlString.text)
        answerText  = '小萌::' + re.split('##',eval(htmlString.text)['answer'])[0] + '......' + answerText
         
    except:
        answerText  = 'GPT2服务器访问出错'
    testInfo=testInfo.replace("<","%3C").replace(">","%3E")

    #返回信息为XML
    #其中包含“回话”文本和测试信息
    htmlString=             "<?xml version='1.0' encoding='utf-8'?>"
    htmlString=htmlString + "<root>"
    htmlString=htmlString + "        <answerText>"+answerText+"</answerText>"
    htmlString=htmlString + "        <testInfo>"+testInfo+"</testInfo>"
    htmlString=htmlString + "</root>"

    #htmlString="AJAX测试"+str(queryForm['queryText'])
    #htmlString="接口queryString:key--"+queryString['key']
    #htmlString  = htmlString+"接口queryData:key--"+queryForm['key']	
    return htmlString	  
	
def getTianKongInterface(queryString,queryForm):
    answerText=" "
    testInfo=" "
    if queryForm['queryCmd'][0]=="answerText":
        #如果仅要回话信息，则测试信息为空。
        testInfo=" " #必须加一个空格。否则客户端解析出错。
    baidu_rul = "http://zzzai.natapp1.cc/api/query"
    h = {"question": queryForm['queryText'][0]}
    try:
        htmlString=requests.get(url=baidu_rul, params=h)  #.content.decode('utf-8','ignore')
        htmlString.raise_for_status()
	# print('hhhhhhhh\n',htmlString.encoding,htmlString.apparent_encoding,"\n!!!!!!",htmlString.text)
        htmlString.encoding = htmlString.apparent_encoding
        print("\n!!!!!!",htmlString.text)
        answerText  = '小呆::' + re.split('##',eval(htmlString.text)['answer'])[0]  
	
         
    except:
        answerText  = '百度搜索+MRC服务器访问出错'
    testInfo=testInfo.replace("<","%3C").replace(">","%3E")

    #返回信息为XML
    #其中包含“回话”文本和测试信息
    htmlString=             "<?xml version='1.0' encoding='utf-8'?>"
    htmlString=htmlString + "<root>"
    htmlString=htmlString + "        <answerText>"+answerText+"</answerText>"
    htmlString=htmlString + "        <testInfo>"+testInfo+"</testInfo>"
    htmlString=htmlString + "</root>"

    #htmlString="AJAX测试"+str(queryForm['queryText'])
    #htmlString="接口queryString:key--"+queryString['key']
    #htmlString  = htmlString+"接口queryData:key--"+queryForm['key']	
    return htmlString	  	
	
	

#对话请求业务
#输入参数：get请求串，POST请求数据（结构为字典）
#返回输出的html编码字符串
def getDialog(queryString,queryForm,htmlName):
    #htmlString="接口queryString:key--"+queryString['key']
    #htmlString  = "接口queryData:key--"+str(queryForm['key'])
    htmlString=""                
    #fileName="program/httpServer/Dialog2.html"
    #fileName="httpServer/Dialog2.html"   #原来的
    fileName="httpServer/"+htmlName  #program
    #htmlString=os.path.abspath('.')
    #读取Dialog2.html文件代码
    with open(fileName, "r",encoding='utf-8') as fo:
        htmlString = fo.read()
    return htmlString


#访问图灵机器人
def to_tuling(Q):
    tuling_url = 'http://openapi.tuling123.com/openapi/api/v2'

    data = {"reqType": 0,
        "perception": {
            "inputText": {
                "text": ""
            }
        }
    ,
        "userInfo": {
            "apiKey": "269d7ac416fa455db0bbd19fb99d1f08",
            "userId": "370612"
        }
        }
    data["perception"]["inputText"]['text'] = Q
    a = requests.post(url=tuling_url, json=data)
    res = a.json()
    print(res)
    return res.get("results")[0].get("values").get("text")


'''
路径解析，获取返回页函数。
根据不同请求路径调用不同的处理函数，返回页面字符串
参数：
    访问路径/interface
    GET提交数据--'key=ssss&key2=fffff'
    POST提交的数据--{'key': ['aaaaa'], 'key2': ['aaaaa2222']}

'''
def getPage(path,queryString,queryForm):
  
    #返回的页面代码
    T_rul = "http://127.0.0.1:8222"
    baidu_rul = "http://zzzai.natapp1.cc/api/query" 
    htmlString=""
    if path=="/interface":
        htmlString=getInterface(queryString,queryForm) 
    elif path=="/":   #全部叠加的路由
        htmlString=getDialog(queryString,queryForm,'Dialog2.html')
    elif path=="/GPT2":    #GPT2路由        
        htmlString=getDialog(queryString,queryForm,"dialogGPT2.html")
    elif path=="/GPT2Interface":
        htmlString=getGPT2Interface(queryString,queryForm)	
    elif path=="/dialog":
        htmlString= getDialog(queryString,queryForm,"dialogYuYi.html")	#生成式对话路由
		
		
    elif path=="/TianKong":
        h = {"question": queryString}
        htmlString=getDialog(queryString,queryForm,"dialogTianKong.html")	#百度搜索路由
    elif path=="/TianKongInterface":
        htmlString=getTianKongInterface(queryString,queryForm)	
		
    elif path.find('.cc') > -1:	
        hcontent = {"question": queryString}
        print('que',queryString)
        htmlString=requests.get(url="http://zssyr2.natappfree.cc/api/query", params=hcontent)
    else:
        htmlString="<p>无相应处理方法"
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
        #解析网页输入参数
        #url解析。结果：ParseResult(scheme='', netloc='', path='/interface', query='key=ssss', fragment='')
        #结构为元组
        queryPath = urlparse(self.path)
        #访问路径。。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        path=unquote(queryPath.path, 'utf-8')
        #query请求数据串。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        #把串转换成字典格式。输入：key=ssss& 输出：{'key': 'ssss'}
        queryString=self.__queryStringParse(unquote(queryPath.query, 'utf-8'))
        #由于是GET提交。其POST请求的数据为空。仅用于调用参数
        queryForm = {}
        #获取输出html代码
        responseText=  getPage(path,queryString,queryForm)
        #输出页面代码
        self.__responseWrite(responseText)

    '''
    POST请求响应函数。
    先解析页面请求参数。获取请路径、FORM参数（dict结构）
    调用函数，获取页面代码
    输出页面代码
    '''
    def do_POST(self):
        #解析网页输入参数
        #url解析。结果：ParseResult(scheme='', netloc='', path='/interface', params='', query='', fragment='')
        #结构为元组
        queryPath = urlparse(self.path)
        #访问路径。。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        path=unquote(queryPath.path, 'utf-8')
        #由于是POST提交。其GET请求的数据为空。仅用于调用参数
        queryString = {}
        #获取POST提交的数据
        #{'key': ['aaaaa'], 'key2': ['aaaaa2222']}
        #结构为字典
        length = int(self.headers['Content-Length'])
        queryForm = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        #获取输出html代码
        responseText=  getPage(path,queryString,queryForm)
        #输出页面代码
        self.__responseWrite(responseText)

    #网页输出函数
    #参数：输出的页面HTML代码，字符串
    def __responseWrite(self,responseText):
        try:
            self.send_response(200)
            self.send_header('Content-type','text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(bytes(responseText, encoding="utf-8"))
        except IOError:
            self.send_error(404,'File Not Found: ')

    #queryString解析。
    #输入参数：queryString串。"key=ssss&key2=ssss222&key3=ssss333"
    #返回结果：{'key': 'ssss', 'key2': 'ssss222', 'key3': 'ssss333'} 结构为：dict
    def __queryStringParse(self,queryString):
        querstr=queryString.replace("=","':'")
        querstr=querstr.replace("&","','")
        if querstr=="" :
            querstr="{}"
        else:
            querstr="{'"+querstr+"'}"
        dict=eval(querstr)
        return dict



#http服务启动函数

def startHttpServer():
    path1=os.path.abspath('.')   # 表示当前所处的文件夹的绝对路径
    print("httpServer.py绝对路径："+path1)    
    #获取参数
    httpConfig=aC.getHttpServerConfig()
    #print(httpConfig.ip)
    #print(httpConfig.port)
    #端口号
    port = httpConfig.port  #8000
    #IP地址
    address= httpConfig.ip #"192.168.15.138"
	
    #address="192.168.1.70"
    #address="192.168.1.70"
    #合成地址
    server_address = (address, port)
    httpd = HTTPServer(server_address, HttpServer_RequestHandler)
    print("http服务已启动..."+address+":"+str(port))
    httpd.serve_forever()







    #bM.busiMain()
    #wLog.writeLog("t","httpServer.py","test0001","http填写日志测试信息")


