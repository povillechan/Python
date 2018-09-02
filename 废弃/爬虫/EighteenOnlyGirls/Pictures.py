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

save_dir = os.path.basename(sys.argv[0]).split(".")[0]
utils.dir_path = "d:\\Pictures\\18OnlyGirls\\"+save_dir+"\\{file_path}"

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
            
            b = pq(url)
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

                'mid':   mid,

                'url':  url,

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
    
#     video = image.get('video')
#     if video:  
#         utils.get_video_file_path(video, utils.get_video_file_path(video, image.get('name')+
#                                            '\\video'))            
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
    url = 'https://www.18onlygirlsblog.com/category/pictures/page/{page}/'    
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
    pool.map(main,[i  for i in range(1,46)])

    pool.close()
    pool.join()
