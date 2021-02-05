#!/usr/bin/python3 

'''
页面有JS加载项。使用Selenium抓取有JS加载的页面。

下载Chromedriver，下载后得到的是一个chromedriver.exe文件。
chromedriver下载地址:http://npm.taobao.org/mirrors/chromedriver/
chromedriver.exe要随着Chrome升级而升级。目录：C:\Program Files (x86)\Google\Chrome\Application

'''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import xlrd
import json
from bs4 import BeautifulSoup   #解析html页面代码
import jieba.posseg as pseg
# coding=utf-8

def Main():
    GetPageHtml();
    print("结束");


def GetPageHtml():
    word="辽宁"
    #请求的Url
    Url0="https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word="
    Url=Url0+word;
    #定义浏览器对象    
    Browser = webdriver.Chrome(options=GetChromeOptions())
    Browser.get(Url);  #初始访问，必须步骤。
    time.sleep(2)
    Browser.delete_all_cookies();    #删除上次访问的Cookie
    # 添加自己的cookie   。GetCookiesXlsx()
    c=1
    for i in GetCookiesXlsx():
        #print(i);        print(c);        c=c+1;
        Browser.add_cookie(cookie_dict=i)
    Browser.get(Url);   #预访问
    time.sleep(2)
    #要查找的单词
    words=['忽如一夜春风来','我爱玉兰','天天向上']
    for word in words:
        Url=Url0+word;
        print("请求的Url.........:",Url)

        #通过ChromeDriver正式请求页面。
        Browser.get(Url);
        time.sleep(2);      #等待5秒，用于前台的JS加载。时间要根据JS的复杂程度确定。
        #获取源码。[0:200]
        SourceData = Browser.page_source
        soup = BeautifulSoup(SourceData, 'html.parser')
        ws = pseg.cut(word)


        searchs = ''
        for a in soup.find_all('dd'):
            mat = True
            for w, f in ws:
                if a.get_text().find(w) ==-1:
                    mat = False
            if mat:
                searchs += a.get_text().replace(' ', '').replace('\r', '').replace('\n', '')

            #print(i, '|', qq)

            #print(qq)




        #print(SourceData);
        #保存源码
        HtmlPathName=word+".txt"
        print(searchs)
        SaveHtml(HtmlPathName,searchs)
    Browser.close()

#保存获取的页面代码
def SaveHtml(PathName,SourceData):
    #打开文件，若文件不存在系统自动创建。.encode('utf-8') 
    f = open(PathName,mode='wb')
    f.write(SourceData.encode('utf-8'))
    f.close()

#获取chrome_options
def GetChromeOptions():
    chrome_options = webdriver.ChromeOptions()
    #不使用Chrome的头部
    # 以最高权限运行
    #chrome_options.add_argument('--no-sandbox')
    # 浏览器不提供可视化页面.
    chrome_options.add_argument('--headless')
    # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--disable-gpu')

    #不知为什么换头不好用。最后用浏览器可视化界面方式，自动提供协议头好用。并且在界面上还能看到运行状况。
    #安装自定义头部。把头信息保存在文件中读取。从每行的第2个字符开始，把': '换成'='
    #for line in open("headers.txt", "r"):
        #chrome_options.add_argument(line[0:1]+line[1:].replace(': ','='))
        #print(line[0:1]+line[1:].replace(': ','='))
    #禁止加载图片。
    #prefs = {"profile.managed_default_content_settings":{"images": 2}}
    #chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options
#从excel中获取cookie
def GetCookiesXlsx():
    '''
        查找位置
        开发者工具>Network>Name>点击链接>Cookies
        CookiesExcel文件说明：
        1、全选文件头中的Cookies项。粘贴到excel文件中。
        2、注意单元格内容中，头尾不要增加空格。
        3、删除N/A项，内容为空即可。把对号✓改为true。
        4、注意数值型数据。一定要改成文本格式。有些被excel改为科学计数法的，一定要改回来。
            双击value列中的数字单位格，保证改为文本格式。
        5、一定要用最新的cookie。时间久了，session会失效。
        6、第一行字段名一定要保留。
    '''
    #读取EXCEL
    # 打开文件
    workbook = xlrd.open_workbook('Cookies.xlsx')
    # 获取所有sheet
    #print(workbook.sheet_names())  # [u'sheet1', u'sheet2']
    # 根据sheet索引或者名称获取sheet内容
    sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
    # sheet的名称，行数，列数
    #print(sheet1.name, sheet1.nrows, sheet1.ncols)
    #行数
    RowCount=sheet1.nrows
    i=1
    #组装Cookie格式的数据,格式：[{"Name":"","Value":"","Domain":"",	Path	Expires 	Size	HttpOnly	Secure	SameSite	Priority},{}]
    #
    CookiesList=[]
    while (i < RowCount):
        #print('The count is:', i)
        #print(sheet1.cell(i, 0).value.strip())
        CookieJsonStr='"'+sheet1.cell(0, 0).value.strip()+'":"'+sheet1.cell(i, 0).value.strip()+'",'            #name
        CookieJsonStr+='"'+sheet1.cell(0, 1).value.strip()+'":"'+str(sheet1.cell(i, 1).value.strip())+'",'      #value
        CookieJsonStr+='"'+sheet1.cell(0, 2).value.strip()+'":"'+str(sheet1.cell(i, 2).value.strip())+'",'      #domain
        CookieJsonStr+='"'+sheet1.cell(0, 3).value.strip()+'":"'+str(sheet1.cell(i, 3).value.strip())+'",'      #path
        #CookieJsonStr+='"'+sheet1.cell(0, 4).value.strip()+'":"'+str(sheet1.cell(i, 4).value.strip())+'",'     #expires
        CookieJsonStr+='"'+sheet1.cell(0, 6).value.strip()+'":"'+str(sheet1.cell(i, 6).value)+'",'          #httponly
        #CookieJsonStr+='"'+sheet1.cell(0, 7).value.strip()+'":"'+str(sheet1.cell(i, 7).value.strip())+'",'           #secure
        CookieJsonStr="{"+CookieJsonStr[:-1]+"}"
        CookieJsonDict=json.loads(CookieJsonStr, strict=False)
        #删除字典中值为空的元素。
        for k in list(CookieJsonDict.keys()):
            #print(k,"-----",CookieJsonDict[k])
            if (not CookieJsonDict[k]) & (k!="value"):
                del CookieJsonDict[k]
             #print(CookieJsonDict)
        CookiesList.append(CookieJsonDict)
        #print(CookieJsonStr)
        i=i+1
    #print(CookiesList)
    return CookiesList   

if __name__ == '__main__':
    Main()