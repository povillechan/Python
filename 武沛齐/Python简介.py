# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import getpass
# import os
# 
# name1 = "wupeiqi"
# name2 = name1
# 
# 
# # 将用户输入的内容赋值给 name 变量
# name = input("请输入用户名：")
#  
# # 打印输入的内容
# print(name)
# 
# 
# # 用户输入不可见
# pwd = getpass.getpass("请输入密码")
# 
# print(pwd)
# 
# 
# # 字符串拼接
# print("i am %s, and passwd is %s" % (name, pwd))
# 
# 
# #列表
# name_list=['alex', 'seven', 'eric']
# name_list_2=list(['alex', 'seven', 'eric'])
# print(name_list)
# print(name_list_2)
# 
# #元组
# age=(11,22,33,"44","55")
# age_2=tuple((11,22,33,"44","55"))
# print(age)
# print(age_2)
# 
# #字典
# person={"name":"alex", "age":18}
# person_2=dict({"name":"alex", "age":18})
# print(person)
# print(person_2)

#文件
fileobj = open("index.html", "rb")
data = fileobj.read().decode("utf-8")
print(data)

print("lines read")
fileobj.seek(0, 0)
for line in fileobj.readlines():
    print(line)
    
fileobj.close()





