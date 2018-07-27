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
dir_path = "d:\Pictures\hegre-art\hegre\\photos\{file_path}"
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
download_file

@author: chenzf
'''             
def download_file(url, file_path):   
    if url is None:
        return 
      
    try:  
        if os.path.exists(file_path):
            print(file_path + " is omitted")
            return       
  
        response = requests.get(url,headers=headers,timeout=30)
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

    print(file_path + ' is done')
    
def process_image(image):
    dir_name = dir_path.format(file_path=image.get('name'))
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)        
    
    
    with open(dir_name+'\\info.json', 'w') as f:    
        json.dump(image, f)
    
    
    for subkeys in ['small','mid','large']:
        url = image.get(subkeys)
  #      print(url)
        if url:
             download_file(url, get_file_path(url, image.get('name')+
                                               '\\'+ subkeys))
    
    detail = image.get('detail')
    board = detail.get('board')
    if board:
        download_file(board, get_file_path(board, image.get('name')+
                                               '\\board'))  
            
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
    url = 'http://www.hegre.com/photos?galleries_page={page}'    
    html = get_page(url.format(page=page))
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
    
