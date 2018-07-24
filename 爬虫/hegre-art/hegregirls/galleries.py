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

# def get_page_detail(url):
#     if url == None:
#         pass
#     else:
#         try:
#             response = requests.get(url,headers=headers)
#             if response.status_code == 200:
#                 return response.text
#             return None
#         except RequestException as e:
#             print(e)
#             return None    
    
# def parse_page_index(html):
#     data = json.loads(html)
#     if data and 'data' in data.keys():
#         for item in data.get('data'):
#             yield item.get('article_url')
#              
#  
def parse_page(html):
    soup = BeautifulSoup(html, 'lxml')
    main_div = soup.find('div', id="block-system-main")
    contents = main_div.find_all('div', class_='field-name-coverl field-type-image')
    images = []
    
    for content in contents:    
        image_pattern = re.compile('<a href=.*?rel="(.*?)".*?<img.*?src="(.*?)".*?title="(.*?)"', re.S)
        results = re.findall(image_pattern, str(content))
    
        for result in results:
            images.append({'name': result[2],
                           'url':result[0],
                           'sub_url':result[1]       
                })
            
    return images
                       
#             
def download_image(images, year, month):
    for image in images:
        try:
            file_path = get_file_path(image,year,month)
            if os.path.exists(file_path):
                continue
            
            response = requests.get(image['url'],headers=headers,timeout=10)
            if response.status_code == 200:
                save_image(response.content, image, year, month)
                
        except RequestException as e:
            try:
                response = requests.get(image['sub_url'],headers=headers,timeout=10)
                if response.status_code == 200:
                    save_image(response.content, image, year, month)
            except RequestException as e:
                continue
               
         
def get_file_path(image, year, month):
    reJpg = re.compile(".*?\.jpg.*?", re.S)
    rePng = re.compile(".*?\.png.*?", re.S)
    file_name = image['name'].replace('?', '_')

    file_path = "E:\Picture\hegre-art\hegregirls\galleries\{year}\{month:0>2}\{name}.{suffix}"
    
    if re.search(reJpg, image['url']):
        file_path = file_path.format(year=year,month=month,name=file_name, suffix='jpg')
    elif re.search(rePng, image['url']):
        file_path = file_path.format(year=year,month=month,name=file_name, suffix='png')
    else:
        file_path = file_path.format(year=year,month=month,name=file_name, suffix='jpg')
        
    print(file_path)
    return file_path

def save_image(content, image, year, month):
    file_path = get_file_path(image,year,month)
    
    dir_name = os.path.dirname(file_path)
#     print(dir_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        
    with open(file_path, 'wb') as f:
        f.write(content)
    
def main(dateInfo):
    url = 'http://hegregirls.com/galleries/{year}/{month:0>2}'
#     for year in range(2002,2019):
#         for month in range(1,13):        
    html = get_page(url.format(year=dateInfo['year'],month=dateInfo['month']))
    if html:
        images = parse_page(html)
        if images:
            download_image(images, dateInfo['year'], dateInfo['month'])

#     for url in parse_page_index(html):
#         print(url)
#         html = get_page_detail(url)
#         if html:
#             result = parse_page_detail(html, url)
#             if result == None:
#                 pass
#             else:
#                 for item in result['images']:
#                     download_image(item)
    
if __name__ == '__main__':
    dateInfos=[]

    for year in range(2002,2019):
        for month in range(1,13):
            dateInfos.append({'year':year,
                              'month':month
                }
                )
    
    pool = Pool(3)      
    for item in dateInfos:
       pool.apply_async(main,(item,))

 
#  pool.map(main,dateInfos)
    pool.close()
    pool.join()
