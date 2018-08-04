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

utils.dir_path = "d:\\Pictures\\Hunter\\Photos\\{file_path}"

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
                items = a('nav.pagination-a').prev_all('ul li')
            
                for item in items.items():
                    if item.hasClass('vid'):
                        continue
                    
                    url = item('a').attr('href')
                    discrib = item('a').attr('title')
                    result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))
        
                    b = pq(url)
        #            
                    art_site_info = b('#breadcrumbs li')
                    info_string = []
                    for it in art_site_info.items(): 
                        info_string.append(it.text())
                        
                    if len(info_string) >=3:
                        site = info_string[0]
                        model = info_string[1]
                        name = info_string[2]
                    
                    previews = b('ul.gallery-b  li')
                    details = []
                    for preview in previews.items():
                        details.append({
                            'large': preview('a').attr('href'),
                            'small': preview('img').attr('src'),                    
                            }
                            )
                           
                    image = {    
                        'site':  site,
                        'name':  utils.format_name(name),  
                        'model': utils.format_name(model),  
                        'discrib': utils.format_name(discrib),
                        'small': result[1] if result and len(result) >= 2 else None,
                        'mid':   item('a').attr('src'),
                        'large':  result[0] if result and len(result) >= 2 else None,  
                        'url':  url,
                        'detail':details,
                        'image_set': result,
        
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
        
    #     video = image.get('video')
    #     if video:  
    #         utils.download_file(video.get('src'), utils.get_video_file_path(video.get('src'), image.get('name')+
    #                                            '\\video'))     
    #         utils.download_file(video.get('board'), utils.get_file_path(video.get('board'), image.get('name')+
    #                                                '\\video_board'))       
        stills = image.get('detail')  
        if stills :
            for i, val in enumerate(stills):   
                for subkeys_val in ['large','mid','small']:                 
                    image_url = val.get(subkeys_val)
                    if image_url:
                        utils.download_file(image_url, 
                                            utils.get_file_path(image_url, 
                                                                "%s\\%s" %(sub_dir_name,str(i+1))
                                                                ),                                                                     
                                            headers={'Referer':image.get('url')}
                                            )
                        break
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

