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

utils.dir_path = "d:\\Pictures\\hegre-art\\hegre\\photos\\{file_path}"

'''
parse_page

@author: chenzf
''' 
def parse_page(html):
    images = []  

    soup = BeautifulSoup(html, 'lxml')   
    #items
    items  = soup.find_all('div', class_="item")
    
    for item in items:
        poster_image = item.find('div', class_='img-holder').find('img').attrs['src']
       

        mid = item.find('div', class_='cover-links').find('a', attrs={'data-lightbox':"lightbox--poster_image"})
        if not mid:
            mid_url = None;
        else:
            mid_url = mid.attrs['href']

        large = item.find('div', class_='cover-links').find('a', attrs={'data-lightbox':"lightbox--board_image"})
        if not large:
            large_url = None;
        else:
            large_url = large.attrs['href']   

        name = item.find('a', class_='open-in-content-overlay').attrs['title'].strip()
        images.append({
			'name': name.strip().replace('\"','_').replace(':','_').replace('?','_'),
            'small': poster_image,
            'mid': mid_url,
            'large': large_url,   
            'url':  urljoin('http://www.hegre.com/', item.find('a', class_='open-in-content-overlay').attrs['href']),
            })

    return images

'''
parse_page

@author: chenzf
''' 
def parse_page_detail(html):

    image = {}

    soup = BeautifulSoup(html, 'lxml')   
    #items
    board = None

    item  = soup.find('div', class_="content-overlay-wrapper") 
    if item:
        style_text  = item.select_one('div[class="non-members"]').attrs['style']
        board  = re.search("url\((.*?)\)", style_text, re.S).group(1)
    
    image['board'] = board
            
    DownLoad = []
    items = soup.find_all('div', class_="gallery-zips")
    for item in items:
        DownLoad.append(item.find('a').attrs['href'])
    image['download'] = DownLoad   
    
    image['date'] = soup.find('span', class_="date").string
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
    
    
    for subkeys in ['small','mid','large']:
        url = image.get(subkeys)
  #      print(url)
        if url:
             utils.download_file(url, utils.get_file_path(url, image.get('name')+
                                               '\\'+ subkeys))
    
    detail = image.get('detail')
    board = detail.get('board')
    if board:
        utils.download_file(board, utils.get_file_path(board, image.get('name')+
                                               '\\board'))  
            
def process_image_detail(url):
    detail = None
    html = utils.get_page(url)
    if html:
        detail = parse_page_detail(html)
      
    return detail
     
'''
main

@author: chenzf
'''     
def main(page):
    url = 'http://www.hegre.com/photos?galleries_page={page}'    
    html = utils.get_page(url.format(page=page))
    if html:
        images = parse_page(html)
        if images:
            for image in images:
                image['detail'] = process_image_detail(image.get('url'))
                process_image(image)

if __name__ == '__main__':   
    pool = Pool(3)      
    pool.map(main,[i  for i in range(1,50)])

    pool.close()
    pool.join()
    
