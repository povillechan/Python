# -*- coding:utf-8 -*-
'''
@author: chenzf
'''

def f(x):
    return x**2

r = map(f, [1,2,3,4,5])
print(r)
print(list(r))
    
    
from functools import reduce   
def add(x,y):
    return x+y

print(reduce(add,[1,2,3,4,5])) 

def fn(x,y):
    return x*10+y

print(reduce(fn,[1,2,3,4,5])) 
    
#把用户输入的不规范的英文名字，变为首字母大写，其他小写的规范名字    
def normalize(name):
    return name[0].upper() + name[1:].lower()
    
L1 = ['adam', 'LISA', 'barT']
L2 = list(map(normalize, L1))
print(L2)

#可以接受一个list并利用reduce()求积
def prod(L):
    return reduce(lambda x,y: x*y, L)

print('3 * 5 * 7 * 9 =', prod([3, 5, 7, 9]))
if prod([3, 5, 7, 9]) == 945:
    print('测试成功!')
else:
    print('测试失败!')
    
#利用map和reduce编写一个str2float函数，把字符串'123.456'转换成浮点数123.456
DIGITS = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '.':-1}
isDigital = True;
def char2num(s):
    return DIGITS[s]

# def floatsum(x,y):
#     if y==-1:
#         isDigital = false
#     
#     if isDigital:
#         return x*10 + y
#     else:
#         return 
#     return DIGITS[s]

def str2float(s):
    return reduce(lambda x, y: x * 10 + y, map(char2num, s))   
    
print('str2float(\'123.456\') =', str2float('123.456'))
if abs(str2float('123.456') - 123.456) < 0.00001:
    print('测试成功!')
else:
    print('测试失败!')