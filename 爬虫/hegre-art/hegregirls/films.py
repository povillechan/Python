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

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,parentdir)
from com_tools import utils

utils.dir_path = "d:\\Pictures\\hegre-art\\hegregirls\\films\\{file_path}"

'''
parse_page

@author: chenzf
''' 
def parse_page(html):
    image = []  

    soup = BeautifulSoup(html, 'lxml')   
    #items
    items  = soup.find_all('div', class_="node-grid")
    
    for item in items: 
        image.append({           
            'name': utils.format_name(item.select_one('.grid-meta h4 a').string),            
            'board': item.select_one('.content .field-type-image a img').get('src'),
            'url':  urljoin('http://www.hegregirls.com/', item.select_one('.content .field-type-image a').get('href')),
            })

    return image

'''
parse_page

@author: chenzf
''' 
def parse_page_detail(html):
    image = {}
    soup = BeautifulSoup(html, 'lxml')   
    #items
    try:
        date_release = ""
        for s in soup.find(class_="title-subtitle").strings:
            date_release += s

        video = soup.select_one('.mejs-mediaelement video source')
        if video:
            video = video.get('src')
        else:
            video = None

        mid = soup.select_one('.mejs-mediaelement video')
        if mid:
            mid = soup.select_one('.mejs-mediaelement video').get('poster')
        else:
            mid = soup.select_one('.featured img')
            if mid:
                mid = mid.get('src')
            else:
                mid = None

        image = {
            'small':soup.select_one('.field-name-movie-cover a img').get('src'),
            'mid':mid,
            'large':soup.select_one('.field-name-movie-cover a').get('href'),
            'video':video,
            'date':date_release
        }
    except:
        print('error-' + soup.select_one('#page-title').string)
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
    
    
    for subkeys in ['board']:
        url = image.get(subkeys)
        if url:
             utils.download_file(url, utils.get_file_path(url, image.get('name')+
                                               '\\'+ subkeys))
    
    detail = image.get('detail')
    if detail:
        for subkeys in ['small', 'mid', 'large']:
            url = detail.get(subkeys)
            if url:
                utils.download_file(url, utils.get_file_path(url, image.get('name')+
                                               '\\'+ subkeys))

        video = detail.get('video')
        if video:
            utils.download_file(video, utils.get_video_file_path(video, image.get('name')+
                                               '\\video'))                           

'''
process_image_detail

@author: chenzf
'''         
def process_image_detail(url):
    detail = None
    html = utils.get_page_by_chrome(url, '.mejs-poster')
    if html:
        detail = parse_page_detail(html)
      
    return detail
     
'''
main

@author: chenzf
'''     
def main(page):
    url = 'http://hegregirls.com/films?page={page}'    
    html = utils.get_page(url.format(page=page))
    if html:
        images = parse_page(html)
        if images:
            for image in images:
                image['detail'] = process_image_detail(image.get('url'))
                process_image(image)

if __name__ == '__main__':   
    pool = Pool(3)      
    pool.map(main,[i  for i in range(0,9)])

    pool.close()
    pool.join()