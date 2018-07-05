# -*- coding:utf-8 -*-
'''
@author: chenzf
'''

print(sorted([36, 5, -12, 9, -21]))
print(sorted([36, 5, -12, 9, -21], key=abs))
print(sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower, reverse=True))

L = [('Bob', 75), ('Adam', 92), ('Bart', 66), ('Lisa', 88)]
def by_name(t):
    return t[0].lower()

L2 = sorted(L, key=by_name)
print(L2)

def by_score(t):
    return t[1]

L3 = sorted(L, key=by_score)
print(L3)