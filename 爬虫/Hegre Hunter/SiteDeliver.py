# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
from pyquery import PyQuery as pq
site_list = ['https://www.hegrehunter.com/']
site_searched = []

def site_search_by_url(url):
    print('parse %s' % url)
    a = pq(url)    

    site_navi = a('h2').filter(lambda i: pq(this).text() == 'Free Erotic Sites').nextAll('ul li a')

    for site in site_navi.items():
        site_url = site.attr('href')
        print('get url %s' % site_url)
        if site_url not in site_list  and site_url not in site_searched:
            print('put in %s' % site_url)
            site_list.append(site_url)

            
while len(site_list) > 0:
    site_search_by_url(site_list[0])
    site_searched.append(site_list[0])
    site_list.pop(0)
    
    
print(site_searched)