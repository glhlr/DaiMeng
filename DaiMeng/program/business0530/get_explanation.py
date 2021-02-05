# coding=utf-8

"""
get_explans用于获取词语在字词典中的解释
获取的顺序：新华字典的词典、成语词典、字典，然后到字词典（习之提供）中的词典、成语词典、字典
第一个词典找到就不往下找了。
输入参数可以是一个词，也可以是一个list
返回一个list，每个元素对应一个词的解释。
没有解释的情况下，返回''。

本模块文件，默认目录是：DaiMeng.code.business.get_explanation
access数据库文件，默认是：DaiMeng/data/accessDB/DaiMeng.mdb
access数据要在自己的电脑配置odbc才能正常连接。
"""

import pyodbc
import os

my_dir = os.path.dirname('zicidian.mdb')
MDB = r'/home/ubuntu/DaiMeng/data/accessDB/DaiMeng.mdb'
#MDB = my_dir + r"/../../../DaiMeng/data/accessDB/DaiMeng.mdb"  # access 的数据库所在目录
# MDB = my_dir + r"zicidian.mdb"
print( MDB)

DRV = 'MDBTools'  # odbc数据源



def get_explan(word):  # 遍历所有的字词典数据库，返回结果
    con = pyodbc.connect('DRIVER={};DBQ={};'.format(DRV, MDB))  # 连接access数据库
    # sql_cilin = r"select * from CiLin where cizu ='%s' " % word
    sql_xh_ci = r"select explanation from xh_ci where ci ='%s' " % word
    sql_xh_idiom = r"select explanation from xh_idiom where word ='%s' " % word
    sql_xh_word = r"select explanation from xh_word where word ='%s' " % word
    # sql_xh_xiehouyu = r"select explanation from xh_ci where ci ='%s' " % word
    sql_zcd_ci = r"select meaning from zcd_ci where name ='%s' " % word
    sql_zcd_idiom = r"select meaning from zcd_idiom where name ='%s' " % word
    sql_zcd_word = r"select meaning from zcd_word where name ='%s' " % word

    # con.execute(sql)
    row, res = con.execute(sql_xh_ci).fetchall(), "xh_ci"
    if row == []:
        row, res = con.execute(sql_xh_idiom).fetchall(), 'xh_idiom'
        if row == []:
            row, res = con.execute(sql_xh_word).fetchall(), 'xh_word'
            if row == []:
                row, res = con.execute(sql_zcd_ci).fetchall(), 'zcd_ci'
                if row == []:
                    row, res = con.execute(sql_zcd_idiom).fetchall(), 'zcd_idiom'
                    if row == []:
                        row, res = con.execute(sql_zcd_word).fetchall(), 'zcd_word'
                        if row == []:
                            row = [('',)]
    # print(res, len(row), ":", row)
    con.close()
     
    return row


def get_explans(words):  # 整理返回结果的格式，得到一个list
    if type(words) == str:
        words = [words]
    x = [get_explan(word)[0][0] for word in words]
    return x


def test_random():
    import random
    for i in range(1, 2):
        con = pyodbc.connect('DRIVER={};DBQ={};'.format(DRV, MDB))  # 连接access数据库
        #sql_cilin = r"select top 2000 cizu from CiLin"
        sql_cilin = r"select top 264434 ci from xh_ci"
        row1 = con.execute(sql_cilin).fetchall()
        con.close()
        # print(len(row1))
        a = [y[0] for y in row1][random.randint(0, len(row1))]
    
        x = get_explans(a)
        print(a)
        print(x)
        return [a,x[0]]
    


def test_list():
    con = pyodbc.connect('DRIVER={};DBQ={};'.format(DRV, MDB))  # 连接access数据库
    
    #sql_cilin = r"select top 20 cizu from CiLin"
    sql_cilin = r"select top 264434 ci from xh_ci"
    row1 = con.execute(sql_cilin).fetchall()
    con.close()
    # print(len(row1))
    a = [y[0] for y in row1]
    x = get_explans(a)
    for i in x:
        print(i)


if __name__ == '__main__':
    test_list()
    test_random()
