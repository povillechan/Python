# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import time
import requests
import re
from requests.exceptions import RequestException
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from requests.adapters import HTTPAdapter


class CWebSpiderUtils(object):
    m_defHeaders = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        'Connection': 'close',
        #                     "Connection":"keep-alive",

    }
    m_defTimeout = (30, 30)
    m_defSuccessCode = [200, 204, 206]
    m_savePath = ''
    m_retry_times = 3

    def __init__(self, savePath):
        self.savePath = savePath
        self.chrome_service = Service("C:\\Windows\\System32\\chromedriver.exe")
        self.chrome_service.start()

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
                response = s.get(url, headers=new_headers, timeout=self.m_defTimeout)
            else:
                response = s.get(url, headers=self.m_defHeaders, timeout=self.m_defTimeout)

            if response.status_code in self.m_defSuccessCode:
                return response.text
            return None
        except RequestException as e:
            print(e)
            return None

    '''
    download_file
    
    @author: chenzf
    '''

    def download_file(self, url, filePath, fileType=None, headers=None):
        if url is None:
            return False

        filePath = self.get_file_path(url, filePath, fileType)
        if not filePath:
            return False

        down_retrys = 0
        while True:
            try:

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
                    response = s.get(url, headers=new_headers, timeout=self.m_defTimeout, stream=True)
                else:
                    response = s.get(url, headers=self.m_defHeaders, timeout=self.m_defTimeout, stream=True)

                if response.status_code in self.m_defSuccessCode:
                    if 'content-length' in response.headers:
                        content_size = int(response.headers['content-length'])
                        #                 print('recevice size = %s'%content_size)
                        if os.path.exists(filePath):
                            if os.path.getsize(filePath) == content_size:
                                print(filePath + " is omitted")
                                return True
                            else:
                                os.remove(filePath)
                    else:
                        if os.path.exists(filePath):
                            print(filePath + " is omitted")
                            return True

                    return self.save_file(response, filePath)
                else:
                    print(url + " is error[%s]" % response.status_code)
                    down_retrys += 1
                    if down_retrys >= self.m_retry_times:
                        return False
                    else:
                        time.sleep(10)
                        continue
            except Exception as e:
                print(e)
                down_retrys += 1
                if down_retrys >= self.m_retry_times:
                    return False
                else:
                    time.sleep(10)
                    continue

    '''
    get_file_path
    
    @author: chenzf
    '''

    def get_file_path(self, url, fileName, fileType):
        rePng = re.compile(".*?\.png.*?", re.S)
        reJpg = re.compile(".*?\.jpg.*?", re.S)
        reMp4 = re.compile(".*?\.mp4.*?", re.S)
        rem4v = re.compile(".*?\.m4v", re.S)
        reFlv = re.compile(".*?\.flv", re.S)
        reWebm = re.compile(".*?\.webm", re.S)
        reAvi = re.compile(".*?\.avi", re.S)
        fileName = fileName.replace('?', '_')
        filePath = "{name}.{suffix}"

        if fileType:
            filePath = filePath.format(name=fileName, suffix=fileType)
        elif re.search(rePng, url):
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

        filePath = self.savePath.format(filePath=filePath)
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

        total_size = 0
        chunk_size = 512
        content_size = 0
        report_space = 100
        report_count = 0
        if 'content-length' in response.headers:
            content_size = int(response.headers['content-length'])
        try:
            with open(filePath, type) as f:
                #             f.write(content)
                for content in response.iter_content(chunk_size=chunk_size):
                    f.write(content)
                    f.flush()
                    total_size += len(content)
                    report_count += 1
                    if report_count >= report_space:
                        report_count = 0
                        if content_size > 0:
                            print("File %s [%.2f%%]" % (filePath, int(total_size * 100) / int(content_size)))
                        else:
                            print("File %s [%.0f Kb]" % (filePath, int(total_size) / 1024))
        except Exception as e:
            print("Download file error [%s]" % e)
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
        return name.strip().replace('\"', '_').replace(':', '_').replace(',', '_').replace('!', '_').replace('?',
                                                                                                             '_').replace(
            '/', ' ')

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

    def get_page_by_chrome(self, url, cssElement, headless=True):
        html = None
        browser = None
        try:
            #             self.log('get_page_by_chrome_start[%s]' %threading.currentThread())
            #             c_service = Service('C:\\Windows\\System32\\chromedriver.exe')
            #             c_service.command_line_args()
            #             if self.chrome_service_running:
            #                 pass
            #             else:

            #                 self.chrome_service_running = True

            use_option = False
            chrome_options = webdriver.ChromeOptions()
            if headless:
                chrome_options.add_argument('--headless')
                use_option = True
            #             chrome_options.add_argument('--headless')
            #             chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('disable-infobars')
            if use_option:
                #                 browser = webdriver.Chrome(chrome_options=chrome_options)
                browser = webdriver.Remote(self.chrome_service.service_url, chrome_options=chrome_options)
            else:
                #                 browser = webdriver.Chrome()
                browser = webdriver.Remote(self.chrome_service.service_url)
                browser.set_window_size(0, 0)
            wait = WebDriverWait(browser, 60)
            #             browser.set_window_size(0,0)
            #             print(browser.__dict__)
            #             print(browser.window_handles)
            #
            #             for item in browser.window_handles:
            #                 print(type(item))
            #                 print(item)

            browser.get(url)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, cssElement)))
            html = browser.page_source
            browser.quit()
            #             self.log('browser.close()[%s]' %threading.currentThread())
            return html
        except:
            browser.quit()

            #             c_service.stop()
            return None
        finally:
            browser.quit()

            #             c_service.stop()
            return html

    '''
    process
    
    @author: chenzf
    '''

    def log(self, logText):
        fileName = self.savePath.format(filePath='Utils.log')
        dirName = os.path.dirname(fileName)
        if not os.path.exists(dirName):
            os.makedirs(dirName)

        with open(fileName, 'a+') as f:
            f.write('%s %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), logText))

        print(logText)
