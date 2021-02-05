# 用于转换文本摘要数据集到GPT-2的训练格式
import re
import sys
import collections
import json
import jieba.posseg as pseg

def summary_gpt2(fn = "PART_I.txt"):
    gpttrain = ""
    item = ["",""]
    with open(fn, 'r', encoding='UTF-8') as f1:
        Sums = f1.readlines()
        ii = 0
        if_su = False
        for su in Sums:
            if su.find("sum") > -1:
                if_su = True
            elif su.find("sho") > -1:
                if_su = False
            elif su.find("<do") > -1:
                continue
            elif su.find("</do") > -1:
                gpttrain += item[0] + item[1] + "\n"
                item = ["",""]
                ii += 1
                if ii % 1000 ==0 :
                    print(ii)
            elif if_su:
                item[1] = su
            elif not if_su:
                item[0] = su

    print(ii,"个训练标注")

    with open('summarytrain.txt', 'w', encoding='UTF-8') as f3:
        f3.write(gpttrain)
        f3.close()

summary_gpt2()