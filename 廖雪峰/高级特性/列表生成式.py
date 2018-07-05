# -*- coding:utf-8 -*-
'''
@author: chenzf
'''

print(list(range(1,10)))
print(list(range(10)))
L=[]
for x in range(1,10):
    L.append(x ** 2)
print(L)

print([x * x for x in range(1,10)])
print([x * x for x in range(1,10) if x%2==0])

print([m + n for m in 'ABC' for n in 'XYZ'])


import os
print([d for d in os.listdir(".")])


d = {'x': 'A', 'y': 'B', 'z': 'C' }
for keys in d.keys():
    print(keys)
    
for values in d.values():
    print(values)
    
for keys,values in d.items():
    print(keys," ",values)

print([k + "=" + v for k,v in d.items()])

L = ['Hello', 'World', 'IBM', 'Apple']
print([s.lower() for s in L]) 

L1 = ['Hello', 'World', 18, 'Apple', None]
L2 = [ s.lower() for s in L1 if isinstance(s,str)]

print(L2)
if L2 == ['hello', 'world', 'apple']:
    print('测试通过!')
else:
    print('测试失败!')
