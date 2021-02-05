# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
import re
import platform, os
from os import path
from lxml import etree
from business.structure import sen_ana

# 根据单句逻辑语义生成经验语义
def experience_mean_result(sen_anaa):
    # 找到xml的路径
    if platform.system() == 'Windows':
        dir = path.dirname(__file__)
        parent_path = path.dirname(dir)
    else:
        parent_path = ('/home/ubuntu/Daimeng')
    tree = ET.parse(parent_path + r'/home/ubuntu/DaiMeng/data/xmlData/库.预备概念.xml')
    root = tree.getroot()
    exp_mean = '' # 待返回的经验语义
    for node in root.iter('jy'):
        if(node.text):
            experience = node.text # 读每一条<jy>
            exp_list = re.split(r'[|]', experience) # |分隔符分隔，前半部分需匹配逻辑语义，后半部分为经验语义
            exp_pre = ''
            if(exp_list):
                exp_pre = exp_list[0]
            else:
                continue
            exp_pre_lst = re.split(r';', exp_pre)
            if(sen_mean_match(exp_pre_lst, sen_anaa.sen_mean)):
                exp_mean = experience
                # 补上经验内容
                exp_mean = exp_mean + ',经验内容=' +parent_node(exp_mean)
                print(exp_mean)
                break
    return exp_mean

# 根据单句逻辑语义与通用经验元素列表进行匹配
def sen_mean_match(exp_pre_lst, sen_mean):
    i = 0
    for exp_pre_element in exp_pre_lst:
        # 匹配主语
        if(re.search('主语', exp_pre_element)):
            result = re.search('.*?主语=(.*?)[,;].*?', exp_pre_element) # 找出经验语句中主语
            if (not result):
                result = re.search('.*?主语=(.*)', exp_pre_element)  # 找出经验语句中主语
            sen_mean_zhuyu = re.search('.*?主语=(.*?)[,:].*?', sen_mean) # 找出逻辑语义串中主语

            # 主语能匹配上，则继续循环匹配其他元素
            if(result and sen_mean_zhuyu):
                if(re.search(result.group(1), sen_mean_zhuyu.group(1))):
                    i += 1
                    continue

        # 匹配谓语
        elif(re.search('V', exp_pre_element)):
            result = re.search('.*?V=(.*?)[,;].*?', exp_pre_element)  # 找出经验语句中谓语
            if(not result):
                result = re.search('.*?V=(.*)', exp_pre_element)  # 找出经验语句中谓语
            sen_mean_v = re.search('.*?V=(.*?)[,:].*?', sen_mean)  # 找出逻辑语义串中谓语

            # 谓语能匹配上，则继续循环匹配其他元素
            if(result and sen_mean_v):
                if (result.group(1) == sen_mean_v.group(1)):
                    i += 1
                    continue

        # 宽松匹配=号后面的元素
        if(normal_match(exp_pre_element, sen_mean)):
            i += 1

    # 所有;分割的元素都匹配成功
    if(i == len(exp_pre_lst)):
        return True
    return False

# 按=后面内容一般匹配
def normal_match(exp_pre_element, sen_mean):
    exp_element__list = re.split(',', exp_pre_element) # 通用经验按,分割成列表元素
    sen_mean_list = re.split(r'[,::\+]', sen_mean) # 逻辑语义按,:+分割成列表元素
    #print(sen_mean_list)
    for exp_element in exp_element__list:
        exp_element_equal = re.search('.*?=(.*)', exp_element)
        #如果匹配元素存在+，则要分隔后再匹配
        if(re.search(r'\+', exp_element_equal.group(1))):
            exp_element_equal_list = re.split(r'\+', exp_element_equal.group(1))
            #print(exp_element_equal_list)
            i=0
            for exp_element_equal_elem in exp_element_equal_list:
                for sen_mean_elem in sen_mean_list:
                    sen_mean_elem_equal = re.search('.*?=(.*)', sen_mean_elem)
                    if (sen_mean_elem_equal):
                        if (sen_mean_elem_equal.group(1) == exp_element_equal_elem):
                            i += 1
                    else:
                        sen_mean_elem_equal = sen_mean_elem
                        if (sen_mean_elem_equal):
                            if (sen_mean_elem_equal == exp_element_equal_elem):
                                i += 1
            if(i == len(exp_element_equal_list)):
                return True
        else:
            for sen_mean_elem in sen_mean_list:
                sen_mean_elem_equal = re.search('.*?=(.*)', sen_mean_elem)
                if(sen_mean_elem_equal):
                    if(exp_element_equal.group(1) == sen_mean_elem_equal.group(1)):
                        return True
    return False

# 根据匹配到的通用经验寻找父标签
def parent_node(str):
    if platform.system() == 'Windows':
        dir = path.dirname(__file__)
        parent_path = path.dirname(dir)
    else:
        parent_path = ('/home/ubuntu/Daimeng')
    selector = etree.parse(parent_path + r'/home/ubuntu/DaiMeng/data/xmlData/库.预备概念.xml')
    parent_node = selector.xpath("//*[jy = '%s']" % str)
    return parent_node[0].tag

if __name__ == '__main__':
    str1 = '位置=背+上'
    str2 = 'V=游,主语=它,状语=飞快::后附加=地,动补=到::介宾=小+公鸡+身边,标点=，,CV=让,C宾语=公鸡::定语=小,宾语=坐::动补=在+自己+的+背+上,标点=。'
    normal_match(str1, str2)
