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
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException as e:
        print(e)
        return None


def parse_page(url, html):
    soup = BeautifulSoup(html, 'lxml')
    
    images = []
        
    main_div = soup.find('div', id="block-system-main")
    contents = main_div.find_all('div', class_='node-grid')
    
    for content in contents:  
        image_content = content.find('img').attrs['src']                
 #       print(image_content.attrs['src'])
        
        name_content = content.find('div', class_='grid-meta').find('a').string
 #       print(name_content)

        info_content = urljoin(url, content.find('div', class_='grid-meta').find('a').attrs['href'])
        images.append({'url':  image_content,
                       'name':  name_content,
                       'info': info_content
            })
            
    return images

                       
#             
def download_image(images):
    for image in images:
        print(image)
        try:
            file_path = get_file_path(image)
            if os.path.exists(file_path):
                continue
            
            response = requests.get(image['url'], headers=headers, timeout=10)
            if response.status_code == 200:
                save_image(response.content, image)
                pass
                
        except RequestException as e:
            continue
               
         
def get_file_path(image):
    reJpg = re.compile(".*?\.jpg.*?", re.S)
    rePng = re.compile(".*?\.png.*?", re.S)
    file_name = image['name'].replace('?', '_')

    file_path = "d:\Pictures\hegre-art\hegregirls\models\{name}\{name}.{suffix}"
    
    if re.search(reJpg, image['url']):
        file_path = file_path.format(name=file_name, suffix='jpg')
    elif re.search(rePng, image['url']):
        file_path = file_path.format(name=file_name, suffix='png')
    else:
        file_path = file_path.format(name=file_name, suffix='jpg')
        
    print(file_path)
    return file_path


def save_image(content, image):
    file_path = get_file_path(image)
    
    dir_name = os.path.dirname(file_path)
#     print(dir_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        
    with open(file_path, 'wb') as f:
        f.write(content)
        
    with open(dir_name+'\info.txt', 'w') as f:
        f.write(image['info'])


def get_next_url(url, html):
    soup = BeautifulSoup(html, 'lxml')
    nextPage = soup.find('a', title="Go to next page")
    
    if nextPage:        
        return urljoin(url, nextPage.attrs['href'])
    else:
        return None


def main():
    url = 'http://hegregirls.com/models'

    while url:
        html = get_page(url)
        if html:
            images = parse_page(url, html)
            if images:
                download_image(images)
        url = get_next_url(url, html)
        
            
if __name__ == '__main__':
    main()
