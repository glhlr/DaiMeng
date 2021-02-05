#!/usr/bin/python3 
#coding=utf-8

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
import os
from urllib.parse import urlparse
from urllib.parse import unquote
import urllib
import time
import requests
import platform 
import random
'''
作者：张永涛    
编写时间：2021年1月25日

模块说明
仅用于测试，在客户端增加回复时间功能。

httpServer服务器提供模块。
包含：服务器提供及启动。get、post请求处理。路径分析。相应业务处理。

startHttpServer()：http服务启动及配置。包含IP及端口配置。
class HttpServer_RequestHandler:http服务类。包含get、post请求处理。页面代码输出。get请求字符串解析。
getPage(path,queryString,queryForm)：请求路径分析。根据请求路径，调用不同的处理函数。
getDialog(queryString,queryForm):/dialog请求路径处理函数。返回对话页面的html。
getInterface(queryString,queryForm):/interface请求路径处理函数。返回XML格式数据。

'''

#填空对话模式
def getTianKongInterface(queryString,queryForm):
    '''
    简述：填空对话模式的聊天请求接口。根据问话，回复答话及测试信息。
    参数：
            queryString：get请求串，
            queryForm：POST请求数据（结构为字典）
    返回变量：结果中包含两个信息。一个是“回话”文本，一个是测试信息。两种信息组织到XML结果中。到客户端后解析。    
    作者：
    '''
    #回答文本
    answerText=" "
    #测试信息
    testInfo=" "
    #print ("中华人民共和国")
    #根据请求命令处理返回变量
    if queryForm['queryCmd'][0]=="answerText":
        #如果仅要回话信息，则测试信息为空。
        testInfo=" " #必须加一个空格。否则客户端解析出错。
        #访问呆萌系统
        #a=ltp.rep_talk(input=str(queryForm['queryText'][0]))
        answerText="填空回复信息_中华人_民共和国中华_人民_共和国"
    elif queryForm['queryCmd'][0]=="testInfo":
        #如果仅要测试信息，则回话信息为空。
        #answerText="你好 " #必须加一个空格。否则客户端解析出错。
        answerText=str(queryForm['queryText'][0])
        #模拟测试返回测试信息。一个分词结果。
        testInfo="<p>"+str("填空测试信息_中华人_共和国")+"<p>"
    elif queryForm['queryCmd'][0]=="all":
        #访问呆萌系统
        #回复文本
        answerText="填空回复信息_中华人_民共和国中华_人民_共和国"
        #测试信息
        testInfo="<p>"+str("填空测试信息_中华人_共和国")+"<p>"

    #填写测试时间
    localtime = time.localtime(time.time())
    testInfo=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"<p>"+testInfo
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
    return htmlString

#GPT2对话模式
def getGPT2Interface(queryString,queryForm):
    '''
    简述：GPT2对话模式的聊天请求接口。根据问话，回复答话及测试信息。
    参数：
            queryString：get请求串，
            queryForm：POST请求数据（结构为字典）
    返回变量：结果中包含两个信息。一个是“回话”文本，一个是测试信息。两种信息组织到XML结果中。到客户端后解析。    
    作者：
    '''
    #回答文本
    answerText=" "
    #测试信息
    testInfo=" "
    #print ("中华人民共和国")
    #根据请求命令处理返回变量
    if queryForm['queryCmd'][0]=="answerText":
        #如果仅要回话信息，则测试信息为空。
        testInfo=" " #必须加一个空格。否则客户端解析出错。
        #访问呆萌系统
        #a=ltp.rep_talk(input=str(queryForm['queryText'][0]))
        answerText="GPT2回复信息_中华人_民共和国中华_人民_共和国"
    elif queryForm['queryCmd'][0]=="testInfo":
        #如果仅要测试信息，则回话信息为空。
        #answerText="你好 " #必须加一个空格。否则客户端解析出错。
        answerText=str(queryForm['queryText'][0])
        #模拟测试返回测试信息。一个分词结果。
        testInfo="<p>"+str("GPT2测试信息_中华人_共和国")+"<p>"
    elif queryForm['queryCmd'][0]=="all":
        #访问呆萌系统
        #回复文本
        answerText="GPT2回复信息_中华人_民共和国中华_人民_共和国"
        #测试信息
        testInfo="<p>"+str("GPT2测试信息_中华人_共和国")+"<p>"

    #填写测试时间
    localtime = time.localtime(time.time())
    testInfo=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"<p>"+testInfo
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
    return htmlString
#语义串对话模式
def getInterface(queryString,queryForm):
    '''
    简述：语义串对话模式的聊天请求接口。根据问话，回复答话及测试信息。
    参数：
            queryString：get请求串，
            queryForm：POST请求数据（结构为字典）
    返回变量：结果中包含两个信息。一个是“回话”文本，一个是测试信息。两种信息组织到XML结果中。到客户端后解析。    
    作者：
    '''
    print(queryString)
    print(queryForm)
    #回答文本
    answerText=" "
    #测试信息
    testInfo=" "
    #print ("中华人民共和国")
    #根据请求命令处理返回变量
    if queryForm['queryCmd'][0]=="answerText":
        #如果仅要回话信息，则测试信息为空。
        testInfo=" " #必须加一个空格。否则客户端解析出错。
        #answerText="AJAX测试"+str(queryForm['queryText'])+str(queryForm['queryCmd'])
        #answerText=to_tuling(str(queryForm['queryText'][0]))
        #answerText="测试"
        #访问呆萌系统
        #a=ltp.rep_talk(input=str(queryForm['queryText'][0]))
        answerText="回复信息_中华人_民共和国中华_人民_共和国"
        #print(a)

    elif queryForm['queryCmd'][0]=="testInfo":
        #如果仅要测试信息，则回话信息为空。
        #answerText="你好 " #必须加一个空格。否则客户端解析出错。
        answerText=str(queryForm['queryText'][0])
        #模拟测试返回测试信息。一个分词结果。
        testInfo="<p>"+str("测试信息_中华人_共和国")+"<p>"
    elif queryForm['queryCmd'][0]=="all":
        #访问呆萌系统
        #回复文本
        answerText="回复信息_中华人_民共和国中华_人民_共和国"
        #测试信息
        testInfo="<p>"+str("测试信息_中华人_共和国")+"<p>"

    #填写测试时间
    localtime = time.localtime(time.time())
    testInfo=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"<p>"+testInfo
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

#获取聊天页面
def getDialog(queryString,queryForm,htmlName):
    '''
    简述：获取页面的HTML代码
    参数：
        queryString：get请求串，
        queryForm：POST请求数据（结构为字典）
        htmlName：要获取的html文件名
    返回变量：输出的html编码字符串
    作者：
    '''
    #htmlString="接口queryString:key--"+queryString['key']
    #htmlString  = "接口queryData:key--"+str(queryForm['key'])
    htmlString=""                
    fileName="httpServer/"+htmlName   #program/
    #htmlString=os.path.abspath('.')
    #读取Dialog2.html文件代码
    with open(fileName, "r",encoding='utf-8') as fo:
        htmlString = fo.read()
    return htmlString
#路由解析，获取返回页函数。
def getPage(path,queryString,queryForm):
    '''
    简述：路由解析，获取返回页函数。根据不同请求路径调用不同的处理函数，返回页面字符串
    参数：
        path：server获取的请求路由
        queryString：GET提交数据--'key=ssss&key2=fffff'
        queryForm：POST提交的数据--{'key': ['aaaaa'], 'key2': ['aaaaa2222']}
    返回变量：输出的html编码字符串
    作者：
    '''
    #返回的页面代码
    htmlString=""
    if path=="/interface":
        htmlString=getInterface(queryString,queryForm)
    elif path=="/dialog":
        htmlString=getDialog(queryString,queryForm,"dialogYuYi.html")
    elif path=="/GPT2":
        htmlString=getDialog(queryString,queryForm,"dialogGPT2.html")
    elif path=="/GPT2Interface":
        htmlString=getGPT2Interface(queryString,queryForm)
    elif path=="/TianKong":
        htmlString=getDialog(queryString,queryForm,"dialogTianKong.html")
    elif path=="/TianKongInterface":
        htmlString=getTianKongInterface(queryString,queryForm)
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


    def do_POST(self):
        '''
        POST请求响应函数。
        先解析页面请求参数。获取请路径、FORM参数（dict结构）
        调用函数，获取页面代码
        输出页面代码
        '''
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
            self.wfile.write(bytes(responseText, encoding="utf8"))
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
    '''
    简述：启动http服务。定义网址和端口。
    '''
    path1=os.path.abspath('.')   # 表示当前所处的文件夹的绝对路径
    print("httpServer.py绝对路径："+path1)    
    #获取参数
    #httpConfig=aC.getHttpServerConfig()
    #print(httpConfig.ip)
    #print(httpConfig.port)
    #端口号httpConfig.port  #
    port = 8000
    #IP地址
    #address= httpConfig.ip #"192.168.15.138"
    address="192.168.0.70"
    #合成地址
    server_address = (address, port)
    httpd = HTTPServer(server_address, HttpServer_RequestHandler)
    print("http服务已启动..."+address+":"+str(port))
    httpd.serve_forever()


#def dmMain():
#    print("===张永涛的测试启动模块===")
#    print("已启动...")
#    print("python版本号:"+platform.python_version())
#    path1=os.path.abspath('.')   # 表示当前所处的文件夹的绝对路径
#    print("dmMain.py绝对路径："+path1)
#    startHttpServer()
    
#if __name__ == '__main__':
#    dmMain()