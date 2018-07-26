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
import os
from urllib.parse import urljoin
import json

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
dir_path = "d:\Pictures\hegre-art\hegre\massages\{file_path}"
'''
get_page

@author: chenzf
'''
def get_page(url):         
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException as e:
        print(e)
        return None
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
    return image
                                          
'''
download_image

@author: chenzf
'''             
def download_image(url, file_path):   
    if url is None:
        return 
      
    try:  
        if os.path.exists(file_path):
            return       
  
        response = requests.get(url,headers=headers,timeout=10)
        if response.status_code == 200:
            save_file(response.content, file_path)
        
    except RequestException as e:            
        return
  
'''
get_file_path

@author: chenzf
'''         
def get_file_path(url, file_name):
    rePng = re.compile(".*?\.png.*?", re.S)
    file_name = file_name.replace('?', '_')    
    file_path = "{name}.{suffix}"
    
    if re.search(rePng, url):
        file_path = file_path.format(name=file_name, suffix='png')
    else:
        file_path = file_path.format(name=file_name, suffix='jpg')
    
    file_path = dir_path.format(file_path = file_path)
        
    print(file_path)
    return file_path
def get_video_file_path(url, file_name):
    print(url)
    reMp4 = re.compile(".*?\.mp4.*?", re.S)
    file_name = file_name.replace('?', '_')    
    file_path = "{name}.{suffix}"
    
    if re.search(reMp4, url):
        file_path = file_path.format(name=file_name, suffix='mp4')
    else:
        file_path = file_path.format(name=file_name, suffix='avi')
    
    file_path = dir_path.format(file_path = file_path)
        
    print(file_path)
    return file_path   
'''
save_info

@author: chenzf
'''    
def save_file(content, file_path, type='wb'):    
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        
    with open(file_path, type) as f:
        f.write(content)

def process_image(image):
    dir_name = dir_path.format(file_path=image.get('name'))
    print(dir_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)        
    
    
    with open(dir_name+'\\info.json', 'w') as f:    
        json.dump(image, f)
    
    
    for subkeys in ['small','mid','large']:
        url = image.get(subkeys)
  #      print(url)
        if url:
             download_image(url, get_file_path(url, image.get('name')+
                                               '\\'+ subkeys))
    
    detail = image.get('detail')
    board = detail.get('board')
    download_image(board, get_file_path(board, image.get('name')+
                                               '\\board'))  
    trailer = detail.get('trailer') 
    if trailer:
        video = trailer[0]   
        print(video)
        download_image(video, get_video_file_path(video, image.get('name')+
                                               '\\' + image.get('name'))) 
        
    stills = image.get('stills')  
     
    if stills :
        for i, val in enumerate(stills):   
            download_image(val, get_file_path(val, image.get('name')+
                                               '\\'+ i)) 
    
def process_image_detail(url):
    detail = None
    html = get_page(url)
    if html:
        detail = parse_page_detail(html)
      
    return detail

'''
main

@author: chenzf
'''     
def main(page):
    url = 'https://www.hegre.com/massage?id=bondage-femdom-massage&massages_page={page}'        html = get_page(url.format(page=page))
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