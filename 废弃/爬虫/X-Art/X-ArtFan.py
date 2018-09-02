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
import vthread 

save_dir = os.path.basename(sys.argv[0]).split(".")[0]
utils.dir_path = "d:\\Pictures\\X-Art\\"+save_dir+"\\{file_path}"

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

            a = pq(html)   
            #items
            items = a('li.g1-collection-item')
        
            for item in items.items():
                url = item('a[rel=bookmark]').attr('href')
                name = item('a[rel=bookmark]').text()
                result = re.findall('[a-zA-z]+://[^\s]*', str(item('img.attachment-bimber-grid-standard').attr('srcset')))
    
                b = pq(url)
    
                video = None
                player = b('div.flowplayer')
                if player:
                    src = json.loads(player.attr('data-item')).get('sources')[0].get('src')     
                    board = re.search('background-image: url\((.*?)\)', player.attr('style')).group(1)
                    video = {
                        'src':src,
                        'board':board
                        }
    
                previews = b('div.tiled-gallery-item a')
                details = []
                for preview in previews.items():
                    details.append({
                        'large': preview('img').attr('data-large-file'),
                        'mid': preview('img').attr('data-medium-file'),
                        'small': preview('img').attr('src'),                    
                        }
                        )
                       
     
                image = {           
                    'name': utils.format_name(name),
    #                 'small': result[1] if result and len(result) >= 2 else None,
    #                 'mid':   mid,
    #                 'large':  result[2] if result and len(result) >= 3 else None,  
                    'url':  url,
                    'video': video,
                    'detail':details,
                    'image_set': result
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
        utils.download_file(video.get('src'), utils.get_video_file_path(video.get('src'), image.get('name')+
                                           '\\video'))     
        utils.download_file(video.get('board'), utils.get_file_path(video.get('board'), image.get('name')+
                                               '\\video_board'))       
    stills = image.get('detail')  
    if stills :
        for i, val in enumerate(stills):   
            for subkeys_val in ['large','mid','small']:                 
                image_url = val.get(subkeys_val)
                if image_url:
                    utils.download_file(image_url, utils.get_file_path(image_url, image.get('name')+
                                               '\\'+ str(i+1))) 
                    break
     
# '''
# main
# 
# @author: chenzf
# '''     
# def main(page):
#     url = 'https://xartfan.com/page/{page}/'    
#     try:
#         html = utils.get_page(url.format(page=page))
#     
#         if html:
#             images = parse_page(html)
#             if images:
#                 for image in images:
#                     process_image(image)
#     except:
#         print('error occured in parse %s' %url.format(page=page))

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
    
if __name__ == '__main__':   
#     pool = Pool(3)      
#     pool.map(main,[i  for i in range(1,53)])
# 
#     pool.close()
#     pool.join()
    call_process('https://xartfan.com/page/{page}', 1, 53)
    
