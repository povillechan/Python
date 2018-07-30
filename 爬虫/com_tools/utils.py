# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re
from requests.exceptions import RequestException
import os

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
dir_path = "d:\\Pictures\\hegre-art\\hegre\\{catalog}\\{file_path}"
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

def get_video_file_path(url, file_name):
    reMp4 = re.compile(".*?\.mp4.*?", re.S)
    rem4v = re.compile(".*?\.m4v", re.S)
    file_name = file_name.replace('?', '_')    
    file_path = "{name}.{suffix}"
    # print(url)
    if re.search(reMp4, url):
        file_path = file_path.format(name=file_name, suffix='mp4')
    elif re.search(rem4v, url):
        file_path = file_path.format(name=file_name, suffix='m4v')
    else:
        file_path = file_path.format(name=file_name, suffix='avi')
    
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

'''
get_page

@author: chenzf
'''
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
def get_page_by_chrome(url, css_ele):         
    try:
        browser = webdriver.Chrome()
        wait = WebDriverWait(browser, 10)
        browser.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_ele)))
        return browser.page_source
    except TimeoutException as e:
        return None
    finally:
        browser.close()
        browser.quit()
