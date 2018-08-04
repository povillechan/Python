# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re
from requests.exceptions import RequestException
from multiprocessing import Pool
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import vthread 
import os,sys
from pyquery import PyQuery as pq
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from com_tools import utils

save_dir = os.path.basename(sys.argv[0]).split(".")[0]
utils.dir_path = "d:\\Pictures\\Xerotica\\"+save_dir+"\\{file_path}"

'''
parse_page

@author: chenzf
''' 
def parse_page(urls_gen):
    try:
        while True:
            url = next(urls_gen)
            if not url:
                return None
            html = utils.get_page(url)

            if html:
                a = pq(html)   
                #items
                items = a('div.modelItem')
            
                for item in items.items():

                    url = item('a.thumb').attr('href')
                    board = item('img').attr('src')
                    name = item('a.title').text()
                  
                    b = pq(url)
                    poster = b('div.left div.photo img').attr('src')
                    profile=[]
                    profile_info = b('div.right li')
                    for profile_item in profile_info.items():
                        print(profile_item.text())
                    
                    details = []

                           
                    image = {    
                        'name': utils.format_name(name),  
                        'board': board,
                        'url':  url,
                        'detail':details,
                    }            
                    yield image
    except:
        print('error in parse %s' % url)
        yield None    
    
    yield None   
            
'''
process_image

@author: chenzf
'''  
@vthread.pool(3)  
def process_image(image):
    print(image)
       
    dir_name = utils.dir_path.format(file_path=image.get('name'))
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    
    with open(dir_name+'\\info.json', 'w') as f:    
        json.dump(image, f)

'''
main

@author: chenzf
'''     
def main(urls_gen):
    try:
        images = parse_page(urls_gen)  
        while True:
            image = next(images)
            if image:
                process_image(image)
            else:
                break
    except:
        print('error occured in parse %s' %urls)

           
def urls_genarator(url, start, end):
    for i in range(start,end):
        yield url.format(page=i)
    yield None
    
def call_process(url, start, end):
    main(urls_genarator(url, start, end))
    
work_url = 'https://www.xerotica.com/models/page{page}.html'    
def Job_Start(url = None):
    print(__file__, "start!")
    if url is None:
        url = work_url
#    total_page = PageCount.page_count(url)
    call_process(url, 1, 136)
    
if __name__ == '__main__':   
    Job_Start()

    
