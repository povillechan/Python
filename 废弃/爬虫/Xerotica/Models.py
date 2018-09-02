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
            referer = url
            if html:
                a = pq(html)   
                #items
                items = a('div.modelItem')
            
                for item in items.items():
                  
                    url = item('a.thumb').attr('href')
                    board = item('img').attr('src')
                    name = item('a.title').text()
                  
                    b = pq(url,headers=utils.default_headers, timeout=30)
                    poster = b('div.left div.photo img').attr('src')
                    profile=[]
                    profile_info = b('div.right li')
                    for profile_item in profile_info.items():
                        profile.append(profile_item.text())             
                    
                    details = None
                    videos_info = b('div.content div.item')
                    if videos_info:
                        for video_item in videos_info.items():
                            video_url = video_item('a.thumb').attr('href')
                            video_name = video_item('a.thumb').attr('title')
                            video_img  = re.search('(.*?)-\d.jpg$', video_item('img').attr('src'), re.S)                              
                            
                            c = pq(video_url,headers=utils.default_headers, timeout=30)
                            video_poster = c('video').attr('poster')
                            src = []                         
                            for src_item in c('video source').items():
                                src.append(src_item.attr('src'))
                            
                            details ={
                                'url':video_url,
                                'name':utils.format_name(video_name),  
                                'image_set': [ '%s-%s.jpg' %(video_img.group(1),i) for i in range(1,10)],
                                'poster': video_poster,
                                'src': src
                                }
                                                       
                            image = {    
                                'brief':{
                                        'name': utils.format_name(name),  
                                        'board': board,
                                        'url':  url,
                                        'profile':profile,
                                        'referer':referer
                                    },
                                'video':details,
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
      
    dir_name = utils.dir_path.format(file_path=image.get('brief').get('name'))
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    
    with open(dir_name+'\\info.json', 'w') as f:    
        json.dump(image['brief'], f)       
           

    board = image.get('brief').get('board')
    if board:
        utils.download_file(board,
                            utils.get_file_path(board, 
                                               "%s\\%s" %(image.get('brief').get('name'), 'board')
                                                ),
                            headers={'Referer':image.get('brief').get('referer')}                                             
                        )           

    
    video = image.get('video')
    if video:  
        for i, val in enumerate(video.get('image_set')):    
            utils.download_file(val, utils.get_file_path(val,    
                                                              "%s\\%s\\%s" %(image.get('brief').get('name'), video.get('name'), str(i+1) )
                                                    )  ,
                               headers={'Referer':video.get('url')}
                        )           

        utils.download_file(video.get('poster'), utils.get_file_path(video.get('poster'),    
                                                           "%s\\%s\\%s" %(image.get('brief').get('name'), video.get('name'), 'poster' )
                                                    ),
                            headers={'Referer':video.get('url')}
                        )          
        
        for video_item in video.get('src'):
            utils.download_file(video_item, 
                                utils.get_video_file_path(video_item,  
                                                         "%s\\%s\\%s" %(image.get('brief').get('name'), video.get('name'), 'video')
                                                         ),   
                                headers={'Referer':video.get('url')}                                                  
                                ) 
            break
    
        with open("%s\\%s\\info.json" %(dir_name, video.get('name')), 'w') as f:    
            json.dump(video, f)     

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
        print('error occured in parse images')

           
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

    
