# -*- coding:gbk -*-
import pymysql
 
conn = pymysql.connect(host=u'127.0.0.1', port=3306, user=u'root', passwd=u'fnst-3d3k', db=u'classinfo', charset=u'utf8')
cursor = conn.cursor(cursor=pymysql.cursors.DictCursor) 
cursor.execute("select * from class")

row_all = cursor.fetchall()
for row in row_all:
    print(row['caption'])
print(row_all)

# row_2 = cursor.fetchmany(3)

# row_3 = cursor.fetchall()
cursor.callproc('p1')
row_all2 = cursor.fetchall()
print(row_all2)

conn.commit()
cursor.close()
conn.close()

if True:
    print("haha1")
elif False:
    print("haha2")
else:
    print("haha3")


for item in row_all:
    print(item)