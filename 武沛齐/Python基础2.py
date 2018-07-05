# -*- coding:utf-8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

# 定义函数（lambda表达式）
my_lambda = lambda arg : arg + 1
  
# 执行函数
result = my_lambda(123)

print(result)

def func(*args):
    print(args)


# 执行方式一
func(11,33,4,4454,5)

# 执行方式二
li = [11,2,2,3,3,4,54]
func(*li)

def func2(**kwargs):
    print(kwargs)


# 执行方式一
func2(name='wupeiqi',age=18)

# 执行方式二
li = {'name':'wupeiqi', 'age':18, 'gender':'male'}
func2(**li)

#map
li = [11, 22, 33]
sl = [1, 2, 3]
new_list = map(lambda a, b: a + b, li, sl)
print(new_list.__str__())
for item in new_list:
    print(type(item),item)
    
