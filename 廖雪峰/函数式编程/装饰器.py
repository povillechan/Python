# -*- coding:utf-8 -*-
'''
@author: chenzf
'''
import datetime
from wupeiqi.Python基础2 import func


def now():
    print(datetime.time())

    
now()
f = now
print(f)
f()
print(f())
print(f.__name__)

print("一层装饰器")


def log(func):

    def wrapper(*args, **kw):
        print('call %s()' % func.__name__)
        return func(*args, **kw)

    return wrapper


@log
def now2():
    print(datetime.time())

    
now2()
print(now2.__name__)      
  
print("二层装饰器")


def log2(text):

    def decorator(func):

        def wrapper(*args, **kw):
            print('%s call %s()' % (text, func.__name__))
            return func(*args, **kw)

        return wrapper

    return decorator


@log2('excute')
def now3():
    print(datetime.time())

    
now3()
print(now3.__name__)

import functools

print("二层装饰器")


def log3(text):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kw):
            print('%s call %s()' % (text, func.__name__))
            return func(*args, **kw)

        return wrapper

    return decorator


@log3('excute')
def now4():
    print(datetime.time())

    
now4()
print(now4.__name__)

# 请设计一个decorator，它可作用于任何函数上，并打印该函数的执行时间：
import time


def metric(fn):
    def calcutime(*args, **kw):
        start = time.time()
        rel = fn(*args, **kw)
        end = time.time()
        print('start time %s,end %s, splash %s' % (start, end, end-start))
        return rel
    return calcutime


# 测试
@metric
def fast(x, y):
    time.sleep(0.0012)
    return x + y;


@metric
def slow(x, y, z):
    time.sleep(0.1234)
    return x * y * z;


f = fast(11, 22)
s = slow(11, 22, 33)
print(f,s)
if f != 33:
    print('测试失败!')
elif s != 7986:
    print('测试失败!')
        
