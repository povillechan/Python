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
dir_path = "d:\Pictures\hegre-art\hegre\models\{file_path}"
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
def parse_page(url, html):
    image = {'url':url}   

    soup = BeautifulSoup(html, 'lxml')   
    #board_image
    board_image  = soup.find('div', class_="board_image")
    if board_image:
        name  = board_image.find('img').attrs['alt'].strip()
        board_image = board_image.find('img').attrs['src']     
  
    image['board_image'] = board_image
    image['name'] = name
       
    #poster_image
    poster_image  = soup.find('div', class_="poster_image")
    if poster_image:
        poster_image = poster_image.find('img').attrs['src']

    image['poster_image'] = poster_image
    
    #products  
    details = soup.find('div', class_="details")
    counts = details.find('div', class_="counts")
    items = counts.find_all('a')
    products = []
    for item in items:
        products.append(item.get_text().strip())
                
    image['products'] = products
    
    #profile    
    labels = soup.find('div', class_="labels")
    rows = labels.find_all('div', class_="row")
    profile = []
    for row in rows:
        profile.append(row.get_text().strip().replace('\n', '')) 
    image['profile'] = profile
    
    
    #galleries-wrapper
    galleries_dict = []
    galleries = soup.find(id = 'galleries-wrapper')

    if galleries:
        items = galleries.find_all('div', class_='item')
        for item in items:
            date_item = item.find('small').string.replace(' ','-').replace(',','-').replace('--','-').split('-')
            date = date_item[2] +'-'+ date_item[0]+'-'+ date_item[1]
            
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
            
            galleries_dict.append({
                'name': item.find('img').attrs['alt'].strip(),
                'url': urljoin('http://www.hegre.com/', item.find('a').attrs['href']),
                'small': item.find('img').attrs['src'],
                'mid': mid_url,
                'large': large_url,
                'date':date            
                })
                                   
    image['galleries'] = galleries_dict                      
                                   
    
    #films-wrapper
    films_dict=[]
    films = soup.find(id = 'films-wrapper')
    if films:
        items = films.find_all('div', class_='item')
        for item in items:
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
            
            films_dict.append({
                'name': item.find('img').attrs['alt'].strip(),
                'url': urljoin('http://www.hegre.com/', item.find('a').attrs['href']),
                'small': item.find('img').attrs['src'],
                'mid': mid_url,
                'large': large_url,      
                })
    image['films'] = films_dict  
    
    #massages-wrapper
    massages_dict=[]
    massages = soup.find(id = 'massages-wrapper')
    if massages:
        items = massages.find_all('div', class_='item')
        for item in items:
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
            
            massages_dict.append({
                'name': item.find('img').attrs['alt'].strip(),
                'url': urljoin('http://www.hegre.com/', item.find('a').attrs['href']),
                'small': item.find('img').attrs['src'],
                'mid': mid_url,
                'large': large_url,      
                })
    image['massages'] = massages_dict      

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

'''
parse_main_page

@author: chenzf
'''    
def parse_main_page(html):
    pages = []
    
    soup = BeautifulSoup(html, 'lxml')
    item_div = soup.find_all('div', class_="item")   
    
    for item in item_div:
        url  = urljoin('http://www.hegre.com/',  item.find('a', class_='artwork').attrs['href'].strip())
        pages.append(url)
    return pages
'''
process_page

@author: chenzf
'''  
def process_page(page):
    html = get_page(page)
    if html:
        image = parse_page(page, html)   
        if image:
            process_image(image)
            
'''
process_image

@author: chenzf
'''  
def process_image(image):
    dir_name = dir_path.format(file_path=image.get('name'))
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    
    with open(dir_name+'\\info.json', 'w') as f:    
        json.dump(image, f)
        
    url = image.get('poster_image')
    download_image(url, get_file_path(url, image.get('name') + '\\poster_image'))
       
    url = image.get('board_image')
    download_image(url, get_file_path(url, image.get('name') + '\\board_image'))
    
    
    for keys in ['galleries', 'films','massages']:
        for keys_item in image.get(keys):
            dir_name = dir_path.format(file_path=image.get('name')+'\\'+ keys+'\\'+ keys_item.get('name'))            
#             print(dir_name)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
           
            for subkeys in ['small','mid','large']:
                url = keys_item.get(subkeys)
                print(url)
                if url:
                     download_image(url, get_file_path(url, image.get('name')+'\\'+ keys+'\\'+ keys_item.get('name')+'\\'+subkeys))
    
'''
main

@author: chenzf
'''     
def main():
    url = 'https://www.hegre.com/models'    
    html = get_page(url)
    pages = []

    if html:
        pages = parse_main_page(html)

    pool = Pool(3)  
    for page in pages:
        pool.apply_async(process_page,(page,))

    pool.close()
    pool.join()

if __name__ == '__main__':   
    main()
