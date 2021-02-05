#!/usr/bin/python3 
#coding=utf-8
import sys
import pymssql
import accessData.accessConfig as aC;

'''
作者：张永涛    
编写时间：2018年10月17日
访问SQL Server 数据库类
此类无属性，只有返回一行数据和多行数据的两个方法
类初始化，从配置文件中获取数据库连接的配置信息
建立连接
返回一行数据方法：GetOne(self,sql,params)  输入参数：sql语句、语句条件参数
params是可选参数
应用实例：      
            import accessData.accessDB as aDB
            helper = aDB.msSqlHelper()
            sql = "SELECT BianMa,XuHao,LeiBie,CiZu  FROM dbo.CiLin WHERE BianMa=%s AND XuHao=%s"

            params = ('Be04A','06')
            row =helper.GetOne(sql,params)
            for cols in row:
                print(cols)
            print (row)

            
返回多行数据方法：GetAll(self,sql,params)  输入参数：sql语句、语句条件参数
应用实例：
    sql = "SELECT BianMa,XuHao,LeiBie,CiZu  FROM dbo.CiLin WHERE BianMa=%s AND XuHao=%s"
    params = ('Be04A','06')
    rows =helper.GetAll(sql,params)
    for row in rows:
        print(row[0], row[1], row[2], row[3])

#插入多条记录
    data=[(15,'zhangsan' ),(16,'lisi' )]
    helper = aDB.msSqlHelper()
    sql = "INSERT INTO BaiDuZhiDao_Answer   (QuestID,Answer) VALUES (%d,%s ) "
    helper.InsertMany(sql,data)
'''
class msSqlHelper(object):
    #
    def __init__(self):
        #获取数据库连接配置信息
        self.cC=aC.getConnConf()

    #获取数据库的连接。返回游标对象
    def __GetConnect(self):
        if self.cC.database=="":
            print("没有设置数据库信息")
            s
        # 参数依次是：IP地址,数据库登录名，数据库密码，数据库实体名称,指定字符集 （未指定可能出现中文乱码）
        try:
            self.conn = pymssql.connect(self.cC.server, self.cC.user, self.cC.password, self.cC.database, charset='utf8')
            # 使用cursor() 方法创建一个游标对象 cursor
            cur = self.conn.cursor()
            #返回游标对象
            return cur
        except BaseException as err :
            print( "发生异常:连接数据库失败。报错信息：" + str(err))
            sys.exit(1) #退出系统

    '''
        查询数据库：返回一行数据
        fetchone(): 获取一行数据
    '''
    def GetOne(self,sql,params):
        #获取数据库游标对象
        cursor = self.__GetConnect()
        try:
            # 使用execute()方法执行sql 
            cursor.execute(sql,params)
            result = cursor.fetchone()
            cursor.close()
            #最终关闭数据库连接
            self.conn.close()
            return result
        except BaseException as err  :
            print("发生异常:查询数据库失败(GetOne)。报错信息："+str(err))
            sys.exit(1) #退出系统

    '''
        查询数据库：返回多行数据
        fetchall(): 获取多行数据
    '''
    def GetAll(self,sql,params):
        #获取数据库游标对象
        cursor = self.__GetConnect()
        try:
            cursor.execute(sql,params)
            result = cursor.fetchall()
            cursor.close()
            #最终关闭数据库连接
            self.conn.close()
            return result
        except BaseException as err  :
            print("发生异常:查询数据库失败(GetAll)。报错信息："+str(err))
            sys.exit(1) #退出系统
        

    '''
    一次插入多条记录的方法
    '''
    def InsertMany(self,sql,data):
        #获取数据库游标对象
        cursor= self.__GetConnect()
        try:
            # 使用execute()方法执行sql
            cursor.executemany(sql,data)
            self.conn.commit()
            cursor.close()
            #最终关闭数据库连接
            self.conn.close()
        except BaseException as err  :
            print("发生异常:一次插入多条记录失败(InsertMany)。报错信息："+str(err))
            sys.exit(1) #退出系统
    '''
    修改记录操作
    '''
    def Update(self,sql,params):
        #获取数据库游标对象
        cursor= self.__GetConnect()
        try:
            # 使用execute()方法执行sql
            cursor.execute(sql,params)
            self.conn.commit()
            cursor.close()
            #最终关闭数据库连接
            self.conn.close()
        except BaseException as err  :
            print("发生异常:修改数据库失败(Update)。报错信息："+str(err))
            sys.exit(1) #退出系统



