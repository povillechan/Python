# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re
from urllib import parse
from requests.exceptions import RequestException
from multiprocessing import Pool
from django.template.defaultfilters import urlencode
import json
from bs4 import BeautifulSoup
from string import hexdigits
from hashlib import md5
import os

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}

def get_page_index(offset, keyword):
    data = {
        'offset':offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':20,
        'cur_tab':1,
        'from':'search_tab',
        }
    print(parse.urlencode(data))
    url = 'https://www.toutiao.com/search_content/?' + parse.urlencode(data)
    print(url)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException as e:
        print(e)
        return None

def get_page_detail(url):
    if url == None:
        pass
    else:
        try:
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException as e:
            print(e)
            return None    
    
def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')
             
 
def parse_page_detail(html,url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    image_pattern = re.compile('gallery: JSON.parse\("(.*?)"\),', re.S)
    result = re.search(image_pattern, html.strip())
    if result:
#         print(str(result.group(1)).replace('\\\"','\"'))
        data = json.loads(str(result.group(1)).replace('\\\"','\"').replace('\\\\/','/'))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            return {
                'title':title,
                'url': url,
                'images':images}
            
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException as e:
         print(e)
         return None   

def save_image(content):
    file_path = "%s/%s.%s" % ('E:\Picture\头条', md5(content).hexdigest(),'jpg') 
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
             
def main(offset):
    html = get_page_index(offset,'街拍')
    for url in parse_page_index(html):
        print(url)
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result == None:
                pass
            else:
                for item in result['images']:
                    download_image(item)
    
if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 20 for i in range(10)])
