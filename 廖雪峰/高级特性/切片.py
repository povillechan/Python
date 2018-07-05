# -*- coding:utf-8 -*-
'''
@author: chenzf
'''
def trim(s):
    rls=s[:]
    if len(rls) == 0:
        return rls
    
    while rls[0:1] == " ":
        rls=rls[1:]
        if len(rls) == 0:
            return rls
    
    while rls[-1] == ' ':
        rls=rls[:-1]
        if len(rls) == 0:
            return rls
    
    return rls

if trim('hello  ') != 'hello':
    print('测试失败!')
elif trim('  hello') != 'hello':
    print('测试失败!')
elif trim('  hello  ') != 'hello':
    print('测试失败!')
elif trim('  hello  world  ') != 'hello  world':
    print('测试失败!')
elif trim('') != '':
    print('测试失败!')
elif trim('    ') != '':
    print('测试失败!')
else:
    print('测试成功!')