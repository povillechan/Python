# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re
from requests.exceptions import RequestException
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import socket 
from requests.adapters import HTTPAdapter
class CWebSpiderUtils(object):
    m_defHeaders = {
                    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding":"gzip, deflate, br",
                    "Accept-Language":"zh-CN,zh;q=0.9",
                    "Cache-Control":"max-age=0",
                    "Connection":"keep-alive",
                    }
    m_defTimeout = (10,30)
    m_defSuccessCode = 200
    m_dirPath = ''
    
    def __init__(self, dirPath):
        self.dirPath = dirPath
    '''
    get_page
    
    @author: chenzf
    '''
    def get_page(self, url, headers=None):         
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))
 
            if headers:
                new_headers = self.m_defHeaders.copy()
                new_headers.update(headers)
                response = s.get(url,headers=new_headers,timeout=self.m_defTimeout)
            else:
                response = s.get(url,headers=self.m_defHeaders,timeout=self.m_defTimeout)
                
            if response.status_code == self.m_defSuccessCode:
                return response.text
            return None
        except RequestException as e:
            print(e)
            return None
                                         
    '''
    download_file
    
    @author: chenzf
    '''          
    def download_file(self, url, filePath, headers=None):   
        if url is None:
            return False
          
        try:  
            filePath = self.get_file_path(url,filePath)
            if not filePath:
                return False
                                     
#             if os.path.exists(filePath):
#                 if  os.path.getsize(filePath) > 0:
#                     print(filePath + " is omitted")
#                     return
#                 else:
#                     os.remove(filePath)     
#                   s = requests.Session()
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))
            if headers:
                new_headers = self.m_defHeaders.copy()
                new_headers.update(headers)
                response = s.get(url,headers=new_headers,timeout=self.m_defTimeout, stream=True)
            else:
                response = s.get(url,headers=self.m_defHeaders,timeout=self.m_defTimeout, stream=True)
                
            if response.status_code == self.m_defSuccessCode:
                content_size = int(response.headers['content-length'])
#                 print('recevice size = %s'%content_size)
                if os.path.exists(filePath):
                    if  os.path.getsize(filePath) == content_size:
                        print(filePath + " is omitted")
                        return True
                    else:
                        os.remove(filePath)         
      
                return self.save_file(response, filePath)            
        except Exception as e:   
            print(e)         
            return False
    
    '''
    get_file_path
    
    @author: chenzf
    '''         
    def get_file_path(self, url, fileName):
        rePng = re.compile(".*?\.png.*?", re.S)
        reJpg = re.compile(".*?\.jpg.*?", re.S)
        reMp4 = re.compile(".*?\.mp4.*?", re.S)
        rem4v = re.compile(".*?\.m4v", re.S)
        reFlv = re.compile(".*?\.flv", re.S)
        reWebm = re.compile(".*?\.webm", re.S)
        reAvi = re.compile(".*?\.avi", re.S)
        fileName = fileName.replace('?', '_')    
        filePath = "{name}.{suffix}"


        if re.search(rePng, url):
            filePath = filePath.format(name=fileName, suffix='png')
        elif re.search(reJpg, url):
            filePath = filePath.format(name=fileName, suffix='jpg')
        elif re.search(reMp4, url):
            filePath = filePath.format(name=fileName, suffix='mp4')
        elif re.search(rem4v, url):
            filePath = filePath.format(name=fileName, suffix='m4v')
        elif re.search(reFlv, url):
            filePath = filePath.format(name=fileName, suffix='flv')
        elif re.search(reWebm, url):
            filePath = filePath.format(name=fileName, suffix='webm')
        elif re.search(reAvi, url):
            filePath = filePath.format(name=fileName, suffix='avi')
        else:
            return None
        
        filePath =  self.dirPath.format(filePath = filePath)            
        return filePath   
    
    '''
    save_info
    
    @author: chenzf
    '''    
    def save_file(self, response, filePath, type='wb'):    
        dirName = os.path.dirname(filePath)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
    
        if os.path.exists(filePath):
            os.remove(filePath)
            
        chunk_size = 512 
        try:
            with open(filePath, type) as f:
    #             f.write(content)
                for content in response.iter_content(chunk_size=chunk_size):
                    f.write(content)
                    f.flush()
        except:
            if os.path.exists(filePath):
                os.remove(filePath)
            print(filePath + ' is abort')
            return False
    
        print(filePath + ' is done')   
        return True
 
    '''
    format_name
    
    @author: chenzf
    ''' 
    def format_name(self, name):
        return name.strip().replace('\"','_').replace(':','_').replace(',','_')
    
    '''
    init_chrome
    
    @author: chenzf
    '''
    def init_chrome(self): 
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, 10)
            
    '''
    get_chrome
    
    @author: chenzf
    '''
    def get_chrome(self, url, cssElement):         
        try:
            self.browser.get(url)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, cssElement)))
            return self.browser.page_source
        except Exception as e:
            print(e)
            return None
    '''
    close_chrome
    
    @author: chenzf
    '''
    def close_chrome(self):         
        self.browser.close()           
                
            
    '''
    get_page
    
    @author: chenzf
    '''
    def get_page_by_chrome(self, url, cssElement):         
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
#             chrome_options.add_argument('--disable-gpu')
            browser = webdriver.Chrome(chrome_options=chrome_options)
            wait = WebDriverWait(browser, 10)
#             browser.set_window_size(0,0)
            browser.get(url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, cssElement)))
            return browser.page_source
        except TimeoutException as e:
            return None
        finally:
            browser.close()
            
            
    