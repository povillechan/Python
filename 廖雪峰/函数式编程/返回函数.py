# -*- coding:utf-8 -*-
'''
@author: chenzf
'''

def lazy_sum(*args):
    def sum():
        ax = 0
        for n in args:
            ax = ax + n
        return ax
    return sum

f= lazy_sum(1,3,5,7,9)
print(f)
print(f())

def count():
    fs = []
    for i in range(1, 4):
        def f():
            return i*i
        fs.append(f)
    return fs

f1, f2, f3 = count()
print(f1(),f2(),f3())

def count2():
    def f(j):
        def g():
            return j*j
        return g
    fs=[]
    for i in range(1,4):
        fs.append(f(i))
    return fs
        
f1, f2, f3 = count2()
print(f1(),f2(),f3())

#利用闭包返回一个计数器函数，每次调用它返回递增整数：
def createCounter():
    n = 0
    def counter():
        nonlocal n
        n = n+1
        return n
    return counter

# 测试:
counterA = createCounter()
print(counterA(), counterA(), counterA(), counterA(), counterA()) # 1 2 3 4 5
counterB = createCounter()
if [counterB(), counterB(), counterB(), counterB()] == [1, 2, 3, 4]:
    print('测试通过!')
else:
    print('测试失败!')
