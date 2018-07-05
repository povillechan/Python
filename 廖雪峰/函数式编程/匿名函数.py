# -*- coding:utf-8 -*-
'''
@author: chenzf
'''

print(list(map(lambda x: x * x, [1, 2, 3, 4, 5, 6, 7, 8, 9])))

f = lambda x: x * x
print(f)
print(f(5))

#请用匿名函数改造下面的代码：
def is_odd(n):
    return n % 2 == 1

L = list(filter(is_odd, range(1, 20)))
print(L)

L = list(filter(lambda n: n%2==1, range(1, 20)))
print(L)