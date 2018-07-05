# -*- coding:utf-8 -*-
'''
@author: chenzf
'''

print([x * x for x in range(10)])

print((x * x for x in range(10)))
for n in (x * x for x in range(10)):
    print(n)
    
def fib(max_num):
    n, a, b = 0, 0, 1
    while n < max_num:
        print(b)
        a,b=b, a+b
        n += 1
    return "OK"

fib(10)


def fib_yield(max_num):
    n, a, b = 0, 0, 1
    while n < max_num:
        yield(b)
        a,b=b, a+b
        n += 1
    return "OK"

fib_rel = fib_yield(10)
for n in fib_rel:
    print(n)
    
    
#for循环调用generator时，发现拿不到generator的return语句的返回值。如果想要拿到返回值，必须捕获StopIteration错误，返回值包含在StopIteration的value中：
g = fib_yield(6)
while True:
    try:
        x = next(g)
        print('g:', x)
    except StopIteration as e:
        print('Generator return value:', e.value)
        break

#杨辉三角
# def triangles():
#     L=[]
#     n = 1;
#     while True:
#         if (n == 1):
#             L2=[]  
#             L2.append(1)
#             n+=1
#             L = L2
#             yield L
#         elif (n == 2):
#             L2=[] 
#             L2.append(1)
#             L2.append(1) 
#             n+=1
#             L = L2
#             yield L
#         else:
#             L2=[]  
#             L2.append(L[0])
#             for i in range(len(L)-1):
#                 L2.append(L[i]+L[i+1])              
# 
#             L2.append(L[-1])
#             L=L2
#             yield L
#     return "OK"
    
import copy
def triangles():
    L = [1]
    while True:
        yield copy.copy(L)
        L.append(0)
        L = [L[i - 1] + L[i] for i in range(len(L))]
        
n = 0
results = []
for t in triangles():  
    results.append(t)
    n = n + 1
    if n == 10:
        break
print(results)
if results == [
    [1],
    [1, 1],
    [1, 2, 1],
    [1, 3, 3, 1],
    [1, 4, 6, 4, 1],
    [1, 5, 10, 10, 5, 1],
    [1, 6, 15, 20, 15, 6, 1],
    [1, 7, 21, 35, 35, 21, 7, 1],
    [1, 8, 28, 56, 70, 56, 28, 8, 1],
    [1, 9, 36, 84, 126, 126, 84, 36, 9, 1]
]:
    print('测试通过!')
else:
    print('测试失败!')
    
    
    
    
    