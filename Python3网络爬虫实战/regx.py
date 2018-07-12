# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re

content = requests.get('http://book.douban.com/')
result = re.findall('<a.*?class="name".*?>(.*?)</a>.*?class="author">(.*?)</div>', content.text.strip(), re.S)
 
if result:
    for item in result:
        print(item)        
