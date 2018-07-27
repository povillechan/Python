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

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}

def get_page(url):         
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException as e:
        print(e)
        return None
 
def parse_page(html):
    images = []
    
    soup = BeautifulSoup(html, 'lxml')
    item_div = soup.find_all('div', class_="item")
   
    
    for item in item_div:

        small_url = item.find('div', class_='img-holder').find('img').attrs['src']
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

        date_item = item.find('small').string.replace(' ','-').replace(',','-').replace('--','-').split('-')
        date = date_item[2] +'-'+ date_item[0]+'-'+ date_item[1]
        name = item.find('a', class_='open-in-content-overlay').attrs['title'].strip()
        info = urljoin('http://www.hegre.com/', item.find('a', class_='open-in-content-overlay').attrs['href'])
     
#     for content in contents:    
#         image_pattern = re.compile('<a href=.*?rel="(.*?)".*?<img.*?src="(.*?)".*?title="(.*?)"', re.S)
#         results = re.findall(image_pattern, str(content))
#      
#         for result in results:
        images.append({'name': name,
                       'small':small_url,
                       'mid':mid_url,
                       'large':large_url,
                       'info':info,
                       'date':date
            })
    return images
                       
#             
def download_image(images):
    for image in images:
        for key in ['small','mid','large']:            
            try:
                if not image[key]:
                    continue
                
                file_path = get_file_path(image, key)
                if os.path.exists(file_path):
                    continue
            
                response = requests.get(image[key],headers=headers,timeout=10)
                if response.status_code == 200:
                    save_image(response.content, image, file_path)
                
            except RequestException as e:            
                continue
            
        save_info(image, file_path)    
         
def get_file_path(image, key):
    reJpg = re.compile(".*?\.jpg.*?", re.S)
    rePng = re.compile(".*?\.png.*?", re.S)
    file_name = image['name'].replace('?', '_')
    date_split = image['date'].split('-')
    
    date = date_split[0] + '\\' + date_split[1] + '\\' +  date_split[2]

    file_path = "d:\Pictures\hegre-art\hegre\photos\{date}_{name}\{name}_{type}.{suffix}"
    
    if re.search(reJpg, image[key]):
        file_path = file_path.format(date=date,name=file_name, type=key, suffix='jpg')
    elif re.search(rePng, image[key]):
        file_path = file_path.format(date=date,name=file_name, type=key, suffix='png')
    else:
        file_path = file_path.format(date=date,name=file_name, type=key, suffix='jpg')
        
    print(file_path)
    return file_path

def save_image(content, image, file_path):        
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        
    with open(file_path, 'wb') as f:
        f.write(content)

def save_info(image, file_path):    
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    file_path  =  dir_name+'\info.txt'
    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, 'w') as f:
        f.write(image['info'])
        
def main(page):
    url = 'http://www.hegre.com/photos?galleries_page={page}'    
    html = get_page(url.format(page=page))
    if html:
        images = parse_page(html)
        if images:
            download_image(images)

if __name__ == '__main__':   
    pool = Pool(3)      
    pool.map(main,[i  for i in range(1,50)])

    pool.close()
    pool.join()
    
