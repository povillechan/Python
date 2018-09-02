# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
from pyquery import PyQuery as pq
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,parentdir)
from com_tools import utils

def page_count(url):
    print('page count ', url)
    html = utils.get_page(url)
    if html:
        a = pq(html)             
        
        next_page = a('li.next')
        print(next_page)
        if next_page and next_page('a'):
            return page_count(next_page('a').attr('href'))
        elif next_page:
            cur_page = next_page.prev('li span')
            if cur_page:
                page = cur_page.text().split(' ')[1]
                return int(page) 
    else:
        return None
            
if __name__ == '__main__':   
    print(page_count('https://www.hegrehunter.com/archive/'))
