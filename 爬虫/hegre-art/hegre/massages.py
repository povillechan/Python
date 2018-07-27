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

utils.dir_path = "d:\\Pictures\\hegre-art\\hegre\\massages\\{file_path}"

'''
parse_page

@author: chenzf
''' 
def parse_page(html):
    image = []  

    soup = BeautifulSoup(html, 'lxml')   
    #items
    items  = soup.find_all('div', class_="item")
    
    for item in items:       
        #poster_image
        poster_image  = item.find('div', class_="board_image")
        if poster_image:
            name  = poster_image.find('img').attrs['alt'].strip()
            poster_image = poster_image.find('img').attrs['src']

        mid = item.find('a', attrs={'data-lightbox':"lightbox--poster_image"})
        if not mid:
            mid_url = None;
        else:
            mid_url = mid.attrs['href']
             
        large = item.find('a', attrs={'data-lightbox':"lightbox--board_image"})
        if not large:
            large_url = None;
        else:
            large_url = large.attrs['href']   

        image.append({           
            'name': name.strip().replace('\"','_').replace(':','_'),            
            'small': poster_image,
            'mid': mid_url,
            'large': large_url,   
            'url':  urljoin('http://www.hegre.com/', item.find('a').attrs['href']),
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
    item  = soup.find('div', class_="video-player-wrapper")
    
    if item:       
        #poster_image
        style_text  = item.attrs['style']
        image['board']  = re.search("url\(\'(.*?)\'\)", style_text, re.S).group(1)
    
    Full = []
    items = soup.find_all('div', class_="resolution content ")
    for item in items:
        Full.append(item.find('a').attrs['href'])
    image['full'] = Full
    
    Trailer = []
    items = soup.find_all('div', class_="resolution trailer top-resolution")
    for item in items:
        Trailer.append(item.find('a').attrs['href'])
    image['trailer'] = Trailer
    
    item =soup.find('div',class_='video-stills')
    Stills = []
    if item:
        stills = item.find_all('div', class_="img-holder")
        for still in stills:  
            small = still.find('img')
            if not small:
                small_url = None;
            else:
                small_url = small.attrs['src']   
                  
            large = item.find('a')
            if not large:
                large_url = None;
            else:
                large_url = large.attrs['href']   
 
        Stills.append({           
            'small': small_url,            
            'large': large_url,   
            })
    image['stills'] = Stills
    
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
    trailer = detail.get('trailer') 
    if trailer:
        video = trailer[0]   
        utils.download_file(video, utils.get_video_file_path(video, image.get('name')+
                                               '\\' + image.get('name'))) 
        
    stills = image.get('stills')  
    if stills :
        for i, val in enumerate(stills):   
            utils.download_file(val, utils.get_file_path(val, image.get('name')+
                                               '\\'+ i)) 
'''
process_image_detail

@author: chenzf
'''         
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
    url = 'https://www.hegre.com/massage?id=bondage-femdom-massage&massages_page={page}'    
    html = utils.get_page(url.format(page=page))
    if html:
        images = parse_page(html)
        if images:
            for image in images:
                image['detail'] = process_image_detail(image.get('url'))
                process_image(image)

if __name__ == '__main__':   
    pool = Pool(3)      
    pool.map(main,[i  for i in range(1,5)])

    pool.close()
    pool.join()