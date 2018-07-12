# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import urllib.request

#response = urllib.request.urlopen('http://www.baidu.com')
#print(response.read().decode("utf8))


data = bytes(urllib.parse.urlencode({'world':'hello'}), encoding='utf8')
response = urllib.request.urlopen('http://httpbin.org/post', data=data)
print(type(response))
print(response.status)
print(response.getheaders())
print(response.read().decode("utf8"))