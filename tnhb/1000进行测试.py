#!/usr/bin/python3
# coding=utf-8
import requests
import json
import time
import re

#uri_base = "http://caai.natapp1.cc/api/query"
uri_base = "http://192.168.1.17:8111/api/query"

# 发request申请post
def req_ans(question):
    # url_base = "http://192.168.0.70:8111/api/query"
    #question = "{拜占庭帝国灭亡的时间是________年。}"

    content = {"question": question}
    response = requests.get(url=uri_base, params=content)

    rdata = response.json()
    return rdata






'’‘现有的4000'''
file_read = open('这回变成4000问.txt', 'r', encoding='UTF-8').read()
file_read=file_read.replace('\ufeff','')
file_read_list=eval(file_read)
print('len(file_read_list)==',len(file_read_list))
#
for ddd in range(0,len(file_read_list)):
#Ж朝地理学家徐霞客的著作是《徐霞客游记》
#法国的国庆日是Ж月14日。
    if 1>ddd >=0:
    #if ddd%4==0 and ddd<40:
        #dddd='法国的国庆日是Ж月14日。'
        print(ddd)
        que=file_read_list[ddd].replace('\ufeff','').replace('inurl:zybang ','').strip()
        que='今天的天气就像Ж'
        que = '今天早饭你吃了一碗Ж的羊肉泡馍'
        que=re.sub('_+','Ж',que)
        print(que)
        answer = req_ans(que)

        print(answer['answer'].replace('##','\n'))
        print('-' * 32)




