# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re
from requests.exceptions import RequestException
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from pyquery import PyQuery as pq
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,parentdir)
from com_tools import utils

utils.dir_path = "d:\\Pictures\\Hunter\\Videos\\{file_path}"

'''
parse_page

@author: chenzf
''' 
def parse_page(urls):
    try:
        for url in urls:
            html = utils.get_page(url)
            if html:
                a = pq(html)   
                #items
                items = a('nav.pagination-a').prev_all('ul li.vid')

                for item in items.items():
                    url = item('a').attr('href')
                    discrib = item('a').attr('title')
                    result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))

                    b = pq(url)
                        
                    art_site_info = b('#breadcrumbs li')
                    info_string = []
                    for it in art_site_info.items(): 
                        info_string.append(it.text())
                        
                    if len(info_string) >=3:
                        site = info_string[0]
                        model = info_string[1]
                        name = info_string[2]
                        
                    video = None
                    video_item = b('video')
                    if video_item:
                        src = []

                        for src_item in video_item('source').items():
                            src.append(src_item.attr('src'))
                        video={
                            'src': src,
                            'poster':video_item.attr('poster')
                            }                                    

                           
                    image = {    
                        'site':  site,
                        'name':  utils.format_name(name),  
                        'model': utils.format_name(model),  
                        'discrib': utils.format_name(discrib),
                        'small': result[1] if result and len(result) >= 2 else None,
                        'mid':   item('a').attr('src'),
                        'large':  result[0] if result and len(result) >= 2 else None,  
                        'url':  url,
                        'image_set': result,       
                        'video': video 
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
def process_image(image):
    try:
        sub_dir_name = "%s\\%s\\%s" %(image.get('site'), image.get('model'), image.get('name'))
        dir_name = utils.dir_path.format(file_path=sub_dir_name)
        
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)        
        
        
        with open(dir_name+'\\info.json', 'w') as f:    
            json.dump(image, f)
        
        
        for subkeys in ['large','mid','small']:
            url = image.get(subkeys)
      #      print(url)
            if url:
                utils.download_file(url, 
                                    utils.get_file_path(url, 
                                                        "%s\\%s" %(sub_dir_name, 'board')
                                                        ),
                                    headers={'Referer':image.get('url')}                                                            
                                    )
                
                break
        
        video = image.get('video')
        if video:  
            for video_item in video.get('src'):
                utils.download_file(video_item, 
                                    utils.get_video_file_path(video_item,  
                                                              "%s\\%s" %(sub_dir_name, 'video')
                                                              ),
                                    headers={'Referer':image.get('url')}                                                            
                                    ) 
                break
            utils.download_file(video.get('poster'), 
                                utils.get_file_path(video_item,  
                                                         "%s\\%s" %(sub_dir_name, 'poster')
                                                         ),
                                headers={'Referer':image.get('url')}                                                            
                                )      

    
    except:
        print('process_image error occured!')
     
'''
main

@author: chenzf
'''     
def main(urls):
    try:
        images = parse_page(urls) 
        pool = ThreadPoolExecutor(max_workers=3)       
        for image in images:
            if image:
                pool.submit(process_image,image)
            else:
                break
    except:
        print('error occured in parse %s' %urls)

           
def call_process(url, start, end):
    main([url.format(page=i) for i in range(start, end)])


