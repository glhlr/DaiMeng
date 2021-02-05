# -*- coding: UTF-8 -*-
import json


'''将
train.json
test.json
dev.json
.strip().replace('\ufeff','')
ЖЖ'''
def gqtojson(context,question):
    jsonff= open('/home/lxz/tnhb/data/test1.json' ,'w+', encoding='utf-8')
    #context="健康减肥卡死的减肥就撒旦福建省地方叫撒地方就撒旦发的附近的萨芬撒大家附近撒旦福建师大犯贱撒娇范围进入文件认为我。"
    #question = "我国是世界上第Ж个能独立发射人造地球卫星的国家。"
    aaa={'version': '1.3', 'data': [{'paragraphs': [{'id': '9999-1', 'context':context , 'qas': [{'question':question, 'id': '9999-1-1', 'answers': [{'text': '答案', 'answer_start': 0, 'id': '1'}]}]}], 'id': '9999', 'title': '历史'}]}
    c=json.dumps(aaa,ensure_ascii=False,indent=4)
    jsonff.write(c)
    jsonff.close()

def gqto():
    jsonff= open('/home/lxz/tnhb/data/test1.json' ,'w+', encoding='utf-8')
    context="我国是世界上第5个能独立发射人造地球卫星的国家。撒地方就撒旦发的附近的萨芬撒大家附近撒旦福建师大犯贱撒娇范围进入文件认为我。"
    question = "我国是世界上第Ж个能独立发射人造地球卫星的国家。"
    aaa={'version': '1.3', 'data': [{'paragraphs': [{'id': '9999-1', 'context':context , 'qas': [{'question':question, 'id': '9999-1-1', 'answers': [{'text': '答案', 'answer_start': 0, 'id': '1'}]}]}], 'id': '9999', 'title': '历史'}]}
    c=json.dumps(aaa,ensure_ascii=False,indent=4)
    jsonff.write(c)
    jsonff.close()
    #print(c)