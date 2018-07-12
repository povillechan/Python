# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
from bs4 import BeautifulSoup

content = requests.get('http://book.douban.com/')


soup = BeautifulSoup(content.text, 'lxml')
# print(soup.find_all('li'))
for item in soup.find_all("li", attrs={'class':'item'}):
#     print('---------------')
#     print(item)
    for subitem in item.find('a', attrs={'class':'name'}):
        print(subitem.string)