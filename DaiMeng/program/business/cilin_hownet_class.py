# coding=utf-8
"""
须要的文件：
d:\YYY\cilin_bianma_group.txt   # 按编码的前5位，提取的分类
读取后转为字典：cilin_bianma_group

d:\YYY\cilin_hownet_class.txt   # 词林与知网分类的对比，取出现次数最多的几个分类
读取之后提供一个列表ch_list

"""

import re
import ast


class CilinHownet(object):  # 定义
    def __init__(self):
        self.bianma_full = ''
        self.bianma5 = ''
        self.bianma4 = ''
        self.bianma2 = ''
        self.cilin_sync = ''
        self.cilin_group = ''
        self.hn_groups = {}
        self.hn_group_clear = {}
        self.hn_group_secondary = {}
        self.hn_group_attributes = {}
        self.hn_group_attribute_value = {}
        self.hn_group_most = []

    def __str__(self):
        return f"CH({self.bianma_full})({' '.join(re.split(' ', self.cilin_sync)[:3])}))"

    __repr__ = __str__


# 初始化cilin_hownet_class
def CH_init():
    with open('d:\YYY\cilin_hownet_class.txt') as fn:
        cilin_hownet_lines = fn.readlines()
    cc_list = []
    for line in cilin_hownet_lines:
        key, value = re.split(' ', line, 1)
        if key == 'bianma_full':
            ch = CilinHownet()
        if value[0] == '[' or value[0] == '{':
            ch.__dict__[key] = ast.literal_eval(value)
        else:
            ch.__dict__[key] = value.replace('\n', '')
        if key == 'hn_group_most':
            cc_list.append(ch)
    return cc_list


# 初始化cilin_bianma_group，这是一个字典
with open('d:\YYY\cilin_bianma_group.txt') as fn:
    group_lines = fn.readlines()
cilin_bianma_group = {re.split(' ', line, 1)[0]: re.split(' ', line, 1)[1].replace('\n', '') for line in group_lines}
# 初始化ch_list,这是一个list，里面的元素是CilinHownet()
ch_list = CH_init()

if __name__ == '__main__':
    for i in ch_list[:5]:
        print('*' * 50)
        print(i)
        # for key, value in i.__dict__.items():
        #     print(key, value)
        print(i.bianma5, cilin_bianma_group[i.bianma5])  # 按编码的前5位，提取的分类
