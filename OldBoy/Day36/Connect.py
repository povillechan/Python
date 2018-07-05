'''
Created on  
@author: povil
'''
# -*- coding: utf-8 -*- 
import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='fnst-3d3k', db='class_info', charset='utf8')

cursor = conn.cursor()
  

# effect_row = cursor.execute("insert into tb3(nid,num) values(1,20)")
# effect_row = cursor.execute("insert into tb3(nid,num) values(2,20)")

#effect_row = cursor.execute("update hosts set host = '1.1.1.2' where nid > %s", (1,))
  

#effect_row = cursor.executemany("insert into hosts(host,color_id)values(%s,%s)", [("1.1.1.11",1),("1.1.1.11",2)])
  
  
# 
# conn.commit()
#   
cursor.execute("select * from class")

row_all = cursor.fetchall()

print(row_all)

for i in row_all:
#    print(row_all[i][0], row_all[i][1])   

    print(i[0],i[1])   
    if i[1] == '三年二班':
        print("hahaha")   

cursor.close()

conn.close()