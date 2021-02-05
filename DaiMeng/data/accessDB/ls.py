import pyodbc
import re
import os

# 连接数据库
if os.name is 'nt':
    _MDB = r'C:\Users\X1 Carbon\Desktop\Database1.mdb'  # 绝对路径
    _DRV = '{microsoft access driver (*.mdb, *.accdb)}'  # odbc数据源
else:
    _MDB = r'/home/ubuntu/DaiMeng/data/accessDB/Database1.mdb'  # 绝对路径
    _DRV = 'MDBTools'  # odbc数据源

_con = pyodbc.connect('DRIVER={};DBQ={};'.format(_DRV, _MDB))
_con.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
_cursor = _con.cursor()

# 清空xh_word1
_cursor.execute("DELETE FROM xh_word1")
_con.commit()

_row = _cursor.execute("select * from xh_word").fetchall()
_row_new = [[re.sub("'", r"''", j) if j is not None else "无" for j in i] for i in _row]

for i in _row_new:
    # print(type(i))
    a = [j for j in re.split("[|]", i[6]) if j != ""]
    b = ""
    for k in a:
        # print(k)
        try:
            i.encode('latin1').decode('utf-8')
        except:
            continue
        else:
            pass
        if len(b + k) < 4000:
            b += "||" + k
        else:
            print(len(b))
            break
    else:
        # print(len(b))
        pass

    sql = "INSERT INTO xh_word1 VALUES('{}','{}','{}','{}','{}','{}','{}')".format(*i[:6], b)
    _cursor.execute(sql)

_con.commit()
_con.close()
