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
from pyquery import PyQuery as pq
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from com_tools import utils

utils.dir_path = "d:\\Pictures\\18OnlyGirls\\movies\\{file_path}"

'''
parse_page

@author: chenzf
''' 
def parse_page(html):
    image = []  

    try:
        a = pq(html)   
        #items
        items = a('#content li.box-shadow')
    
        for item in items.items():
     #       img = item('img').attr('src')
    #         srcset = item('img').attr('srcset')
            url = item('a').attr('href')
            name = item('a').attr('title')
            mid = item('img').attr('src')
            result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))

            b = pq(url)
    #        video = b('video source').attr('src')
            video = b('video a').attr('href')
    
            previews = b('.ngg-gallery-thumbnail a')
            details = []
            for preview in previews.items():
                details.append({
                    'large': preview('a').attr('data-src'),
                    'small': preview('a').attr('data-thumbnail')
                    }
                    )
                   
            image.append({           
                'name': utils.format_name(name),
                'small': result[1] if result and len(result) >= 2 else None,
                'mid':   mid,
                'large':  result[2] if result and len(result) >= 3 else None,  
                'url':  url,
                'video': video,
                'detail':details
                })
    except:
        print('error in parse')
#         print(url)
#         print(result)
        return None

    return image

'''
process_image

@author: chenzf
'''      
def process_image(image):
    dir_name = utils.dir_path.format(file_path=image.get('name'))
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)        
    
    
    with open(dir_name+'\\info.json', 'w') as f:    
        json.dump(image, f)
    
    
    for subkeys in ['large','mid','small']:
        url = image.get(subkeys)
  #      print(url)
        if url:
            utils.download_file(url, utils.get_file_path(url, image.get('name')+
                                               '\\'+ image.get('name')))
            break
    
    video = image.get('video')
    if video:  
        utils.download_file(video, utils.get_video_file_path(video, image.get('name')+
                                           '\\video'))            
    stills = image.get('detail')  
    if stills :
        for i, val in enumerate(stills):   
            for subkeys_val in ['large','small']:                 
                image_url = val.get(subkeys_val)
                if image_url:
                    utils.download_file(image_url, utils.get_file_path(image_url, image.get('name')+
                                               '\\'+ str(i+1))) 
                    break
     
'''
main

@author: chenzf
'''     
def main(page):
    url = 'https://www.18onlygirlsblog.com/category/movies/page/{page}/'    
    try:
        html = utils.get_page(url.format(page=page))
    
        if html:
            images = parse_page(html)
            if images:
                for image in images:
                    process_image(image)
    except:
        print('error occured in parse %s' %url.format(page=page))

if __name__ == '__main__':   
    pool = Pool(3)      
    pool.map(main,[i  for i in range(1,44)])

    pool.close()
    pool.join()
