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

utils.dir_path = "d:\\Pictures\\hegre-art\\hegregirls\\models\\{file_path}"

'''
parse_page

@author: chenzf
''' 
def parse_page(html):
    soup = BeautifulSoup(html, 'lxml')
    
    images = []
        
    main_div = soup.find('div', id="block-system-main")
    contents = main_div.find_all('div', class_='node-grid')


    for content in contents:  
        try:
            nick = None
            if content.select_one('.grid-meta .nick'):
                nick =  content.select_one('.grid-meta .nick').string
            images.append({
                    'name': utils.format_name(content.find('div', class_='grid-meta').find('a').string),
                    'url':  urljoin('http://hegregirls.com/', content.find('div', class_='grid-meta').find('a').attrs['href']),
                    'board': content.find('img').attrs['src'],  
                    'nick': nick,
                    'stats': content.select_one('.grid-meta .stats').string,      
            })
        except Exception as e:
            print(content.find('div', class_='grid-meta').find('a').string)
            print("error")
    return images

'''
parse_page

@author: chenzf
''' 
def parse_page_detail(html):
    image = {}
    soup = BeautifulSoup(html, 'lxml')   
    #board_image
    board_image  = soup.find('div', class_="field-name-model-board")
    if board_image:
        board_image = board_image.find('img').attrs['src']     
  
    image['board_image'] = board_image
       
    #poster_image
    poster_image  = soup.find('div', class_="box border")
    if poster_image:
        poster_image = poster_image.find('img').attrs['src']

    image['poster_image'] = poster_image
    
   
    #profile    

    labels = soup.find('div', class_="box border")
    rows = labels.find_all('li')
    profile = []
    for row in rows:
        profile.append(row.get_text().strip().replace('\n', '')) 
    image['profile'] = profile    
    
    #wrapper
    galleries_dict = []
    films_dict=[]
    
    items = soup.select('#main-content .content .content .grid-4')
    for item in items:
        if re.search('galleries', item.attrs['about']):
            date_release = ""
            for s in item.find(class_="release-date").strings:
                date_release += s

            
            try:           
                detail_url = item.select_one('.preview-link a')
                if detail_url:
                    detail_url = detail_url.attrs['href']
                
                if detail_url:
                    detail_url = urljoin('http://hegregirls.com/', detail_url)
                    
                galleries_dict.append({
                    'name': utils.format_name(item.select_one('.grid-meta a').string),
                    'date': date_release,
                    'url': urljoin('http://hegregirls.com/', item.select_one('.field-name-coverl a').attrs['href']),
                    'img':item.find('img').attrs['src'],
                    'board': item.select_one('.field-name-coverl a').get('rel')[0],
                    'detail': parse_galleries_detail(detail_url)
                    })  
            except:
                print('galleries_dict dict error')                      
                                    
                                    
        else:   
            try:   
                films_dict.append({
                    'name': utils.format_name(item.select_one('.grid-meta a').string),
                    'img':  item.select_one('.field-name-movie-cover a img').attrs['src'],
                    'board': item.select_one('a.hegre-poster-zoom').get('href')[0],
                    'url': urljoin('http://hegregirls.com/',item.select_one('.field-name-movie-cover a').attrs['href']),
                    })       
                 
            except:
                print('films_dict dict error')    
#                 print(item.select_one('.grid-meta a').string)
#                 print(item.select_one('.field-name-movie-cover a').attrs['href'])   
#                 print(item.select_one('.field-name-movie-cover a img').attrs['src']) 
#                 print(item.select_one('a.hegre-poster-zoom').attrs['href'])  
#                 print(item.select_one('a.hegre-poster-zoom').attrs['rel'])
                                   
    image['galleries'] = galleries_dict  
    image['films'] = films_dict  

    return image               

def parse_galleries_detail(url):
    if not url:
        return None

    detail = {}
    html = utils.get_page(url)
    if not html:
        return None;
    
    soup = BeautifulSoup(html, 'lxml')
    #board_image
    board_image  = soup.find('div', class_="preview-board")
    if board_image:
        board_image = board_image.find('img').attrs['src']    

  
    detail['board_image'] = board_image
    
    images = []
    items = soup.select('.bottom-border-solid .thumbnail')
    if items:
        for item in items:
            images.append({
                'small': item.find('img').attrs['src'],
                'large': item.find('a').attrs['href']})
        
    detail['images'] = images
    return detail
    

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
    
    board = image.get('board')
    if board:
        utils.download_file(board, utils.get_file_path(board, image.get('name')+
                                               '\\board'))  
    
#     for subkeys in ['small','mid','large']:
#         url = image.get(subkeys)
#   #      print(url)
#         if url:
#              utils.download_file(url, utils.get_file_path(url, image.get('name')+
#                                                '\\'+ subkeys))
#     
#     detail = image.get('detail')
#     board = detail.get('board')
#     if board:
#         utils.download_file(board, utils.get_file_path(board, image.get('name')+
#                                                '\\board'))  
#             
    detail = image.get('detail')
    if detail:
        board_image = detail.get('board_image')
        if board_image:
            utils.download_file(board_image, utils.get_file_path(board_image, image.get('name')+
                                               '\\board_image'))  
        poster_image = detail.get('poster_image')
        if board_image:
            utils.download_file(poster_image, utils.get_file_path(poster_image, image.get('name')+
                                               '\\poster_image'))  
            
        galleries =  detail.get('galleries')
        if galleries:
            for gallery in galleries:
                utils.download_file(gallery.get('img'), utils.get_file_path(gallery.get('img'),  image.get('name')+'\\galleries\\'+gallery.get('name')+
                                               '\\img'))  
            
                utils.download_file(gallery.get('board'), utils.get_file_path(gallery.get('board'), image.get('name')+'\\galleries\\'+gallery.get('name')+
                                               '\\board'))  
                
                detail_s = gallery.get('detail')
                if detail_s:
                    if detail_s.get('board_image'):
                        utils.download_file(detail_s.get('board_image'), utils.get_file_path(detail_s.get('board_image'), image.get('name')+'\\galleries\\'+gallery.get('name')+
                                               '\\board_image'))  
                         
                    if detail_s.get('images'):
                        for i, val in enumerate(detail_s.get('images')):   
                            if val.get('small'):
                                utils.download_file(val.get('small'), utils.get_file_path(val.get('small'), image.get('name')+'\\galleries\\'+gallery.get('name')+'\\'+ str(i) +
                                               '_small'))  
                            if val.get('large'):
                                utils.download_file(val.get('large'), utils.get_file_path(val.get('large'), image.get('name')+'\\galleries\\'+gallery.get('name')+'\\'+ str(i) +
                                               '_large'))  
        films =  detail.get('films')
        if films:
            for film in films:
                utils.download_file(film.get('img'), utils.get_file_path(film.get('img'),  image.get('name')+'\\films\\'+film.get('name')+
                                               '\\img'))  
            
                utils.download_file(film.get('board'), utils.get_file_path(film.get('board'), image.get('name')+'\\films\\'+film.get('name')+
                                               '\\board'))  
                

def process_image_detail(url):
    detail = None
    html = utils.get_page(url)
    try:
        if html:
            detail = parse_page_detail(html)
    except:
        print('error-')
        print(url) 
    return detail


'''
main

@author: chenzf
'''     
def main(page):
    url = 'http://hegregirls.com/models?page={page}'    
    html = utils.get_page(url.format(page=page))
    if html:
        images = parse_page(html)
        if images:
            for image in images:
                image['detail'] = process_image_detail(image.get('url'))
#                 print(image)
                process_image(image)

if __name__ == '__main__':   
    pool = Pool(3)      
    pool.map(main,[i  for i in range(0,6)])

    pool.close()
    pool.join()
