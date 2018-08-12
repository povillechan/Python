# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re
from requests.exceptions import RequestException
import os

class CWebSpiderUtils(object):
    m_defHeaders = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    m_defTimeout = 30
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
            if headers:
                new_headers = self.m_defHeaders.copy()
                new_headers.update(headers)
                response = requests.get(url,headers=new_headers,timeout=self.m_defTimeout)
            else:
                response = requests.get(url,headers=self.m_defHeaders,timeout=self.m_defTimeout)
                
            if response.status_code == self.m_defSuccessCode:
                return response.text
            return None
        except RequestException as e:
            return None
                                         
    '''
    download_file
    
    @author: chenzf
    '''          
    def download_file(self, url, filePath, headers=None):   
        if url is None:
            return 
          
        try:  
            filePath = self.get_file_path(url,filePath)
            if not filePath:
                return
                                     
            if os.path.exists(filePath):
                if  os.path.getsize(filePath) > 0:
                    print(filePath + " is omitted")
                    return
                else:
                    os.remove(filePath)     
      
            if headers:
                new_headers = self.m_defHeaders.copy()
                new_headers.update(headers)
                response = requests.get(url,headers=new_headers,timeout=self.m_defTimeout)
            else:
                response = requests.get(url,headers=self.m_defHeaders,timeout=self.m_defTimeout)
                
            if response.status_code == self.m_defSuccessCode:
                self.save_file(response.content, filePath)
            
        except RequestException as e:            
            return
    
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
    def save_file(self, content, filePath, type='wb'):    
        dirName = os.path.dirname(filePath)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
    
        if os.path.exists(filePath):
            os.remove(filePath)
            
        with open(filePath, type) as f:
            f.write(content)
    
        print(filePath + ' is done')   
 
    '''
    format_name
    
    @author: chenzf
    ''' 
    def format_name(self, name):
        return name.strip().replace('\"','_').replace(':','_').replace(',','_')
    
    '''
    get_page
    
    @author: chenzf
    '''
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    @classmethod
    def get_page_by_chrome(self, url, cssElement):         
        try:
            browser = webdriver.Chrome()
            wait = WebDriverWait(browser, 10)
            browser.set_window_size(0,0)
            browser.get(url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, cssElement)))
            return browser.page_source
        except TimeoutException as e:
            return None
        finally:
            browser.close()
            browser.quit()
