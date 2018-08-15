# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import win32gui
import win32api
import win32con
import win32clipboard
from   ctypes import *
import time
from pyquery import PyQuery as pq

class CWebParser(object):
    def __init__(self, savePath, startUrl, nextUrlCss):
        self.savePath = savePath
        self.setUp()
        self.setRule(startUrl, nextUrlCss)
        self.searchedList = []

    def setUp(self):
        # 创建一个FirefoxProfile实例，用于存放自定义配置
        profile = webdriver.FirefoxProfile()
        # 指定下载路径，默认只会自动创建一级目录，如果指定了多级不存在的目录，将会下载到默认路径
        profile.set_preference('browser.download.dir', self.savePath)
        # 将browser.download.folderList设置为2，表示将文件下载到指定路径
        # 设置成2表示使用自定义下载路径；设置成0表示下载到桌面；设置成1表示下载到默认路径
        profile.set_preference('browser.download.folderList',2)
        # browser.helperApps.alwaysAsk.force对于未知的MIME类型文件会弹出窗口让用户处理，默认值为True，设定为False表示不会记录打开未知MIME类型文件的方式
#         profile.set_preference('browser.helperApps.alwaysAsk.force',False)
#         # 在开始下载时是否显示下载管理器
#         profile.set_preference('browser.download.manager.showWhenStarting',False)
#         # 设定为False会把下载框进行隐藏
#         profile.set_preference('browser.doenload.manager.useWindow',False)
#         # 默认值为True，设定为False表示不获取焦点
#         profile.set_preference('browser.download.manager.focusWhenStarting',False)
#         # 下载.exe文件弹出警告，默认值是True，设定为False则不会弹出警告框
#         profile.set_preference('browser.download.manager.alertOnEXEOpen',False)
#         # browser.helperApps.neverAsk.openFile表示直接打开下载文件，不显示确认框
#         # 默认值为空字符串，下行代码行设定了多种文件的MIME类型
#         # 例如application/exe，表示.exe类型的文件，application/excel表示Excel类型的文件
#         profile.set_preference('browser.helperApps.neverAsk.openFile','application/pdf')
#         # 对所给出文件类型不再弹出提示框进行询问，直接保存到本地磁盘
#         profile.set_preference('browser.helperApps.nerverAsk.saveToDisk','application/zip,application/octet-stream')
#         # browser.download.manager.showAlertOnComplete设定下载文件结束后是否显示下载完成提示框，默认为True，设定为False表示下载完成后不显示下载完成提示框
#         profile.set_preference('browser.download.manager.showAlertOnComplete',False);
#         # browser.download.manager.closeWhenDone设定下载结束后是否自动关闭下载框，默认为True，设定为False表示不关闭下载管理器
#         profile.set_preference('browser.download.manager.closeWhenDone',False)
        #启动浏览器时，通过firefox_profile参数
        #将自动配置添加到FirefoxProfile对象中
        self.driver = webdriver.Firefox(firefox_profile=profile)
        self.wait = WebDriverWait(self.driver, 10)
#            
#         options = webdriver.ChromeOptions()
#         prefs = {'download.default_directory': self.savePath}
# #         prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.savePath}
# 
#         options.add_experimental_option('prefs', prefs)
#         self.driver = webdriver.Chrome(chrome_options=options)
        
    def setRule(self, startUrl, nextUrlCss):
        self.startUrl = startUrl
        self.nextUrlCss = nextUrlCss
        
    def getSavePageName(self, title):
        return None
        
    def getUrltoSave(self, url, nextUrlCss):
        try:
            self.driver.get(url)
            print(url, self.driver.title)
            if url in self.searchedList and url == self.startUrl:
                pass
            else:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, nextUrlCss)))
                print(-1) 
                titleName = self.driver.title + ' - Mozilla Firefox'
#                 mainHwnd = win32gui.FindWindow(None, titleName)  
       
    #             print(0)      
                # 按下ctrl+s
                win32api.keybd_event(0x11, 0, 0, 0)
                win32api.keybd_event(0x53, 0, 0, 0)
                win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(1)             
     
    #             print(1)
                hwnd = win32gui.FindWindow(None, '另存为')  
                savePageName = self.getSavePageName(titleName)
                
                if savePageName:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    print(savePageName)
                    win32clipboard.SetClipboardText(savePageName)
                    print(savePageName)
                    win32clipboard.CloseClipboard()
    #                 print(2) 
                    # 按下ctrl+a
                    win32api.keybd_event(0x11, 0, 0, 0)
                    win32api.keybd_event(0x41, 0, 0, 0)
                    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(1)
    #                 print(3) 
                    # 按下ctrl+v
                    win32api.keybd_event(0x11, 0, 0, 0)
                    win32api.keybd_event(0x56, 0, 0, 0)
                    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(1)
    #                 print(4)             
                # 按下alt+s       
                win32api.keybd_event(0x12, 0, 0, 0)
                win32api.keybd_event(0x53, 0, 0, 0)
                win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(1)                 
    #             print(5) 
                hwnd = win32gui.FindWindow(None, '确认另存为')  
                if hwnd:
                    # 按下alt+y
                    win32gui.SetForegroundWindow(hwnd)
                    win32api.keybd_event(0x12, 0, 0, 0)
                    win32api.keybd_event(89, 0, 0, 0)
                    win32api.keybd_event(89, 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(1)
                    print(6) 
        
                self.searchedList.append(url)
#             print(7) 
#             win32gui.SetForegroundWindow(mainHwnd)
            html =  self.driver.page_source
            a = BeautifulSoup(html, 'lxml')
            ab = a.select(nextUrlCss)
            nextUrl= ab[-1].attrs['href']

            if nextUrl in self.searchedList:
                return None
            else:
                return nextUrl
        except Exception as e:
            print(e)
            return None
        
    def run(self):
        try:
#             self.driver.maximize_window()

            for nextCss in self.nextUrlCss:      
                nextUrl = self.startUrl            
                while nextUrl:
                    nextUrl = self.getUrltoSave(nextUrl, nextCss)
        except Exception as e:
            print(e)
        finally:    
            self.driver.close()

        
#     def test_dataPicker(self):
#         url1 = 'https://github.com/mozilla/geckodriver/releases'
#         self.driver.get(url1)
#         #选择下载zip类型文件，使用application/zip指代此类型文件
#         self.driver.find_element_by_xpath('//strong[.="geckodriver-v0.19.1-win64.zip"]').click()
#         time.sleep(10)
#         url = 'https://www.python.org/downloads/release/python-2712/'
#         self.driver.get(url)
#         self.driver.find_element_by_link_text('Windows x86-64 MSI installer').click()
#         time.sleep(10)
# 
#     def tearDown(self):
#         self.driver.quit()

'''
键盘键与虚拟键码对照表
 
　　　 　　字母和数字键 数字小键盘的键
功能键 其它键 
　　　　　　键　　 键码　  　键　　 键码　　　 键　　 键码 　　  键　　　　键码 
　　　　　　A　　　65　　   0 　　96 　　　　F1 　　112 　　Backspace 　　　8 
　　　　　　B　　　66　　   1　　 97 　　　　F2 　　113　　 Tab 　　　　　　9 
　　　　　　C　　　67 　　  2 　　98 　  　　F3 　　114　　  Clear 　　　　　12 
　　　　　　D　　　68　　　3　　 99 　　　　F4 　　115　　Enter 　　　　　13 
　　　　　　E　　　69 　　  4 　　100　　　　F5 　　116　　Shift　　　　　 16 
　　　　　　F　　　70 　　  5 　　101　　　　F6 　　117　　Control 　　　　17 
　　　　　　G　　　71 　　  6　　 102　　　　F7 　　118 　　Alt 　　　　　　18 
　　　　　　H　　　72 　　　7 　　103　 　　F8 　　119　　Caps Lock 　　　20 
　　　　　　I　　　73 　　　8 　　104　　　　F9 　　120　　Esc 　　　　　　27 
　　　　　　J　　　74 　　　9　　 105　　　　F10　　121　　Spacebar　　　　32 
　　　　　　K　　　75 　　　* 　　106　  　　F11　　122　　Page Up　　　　 33 
　　　　　　L　　　76 　　　+ 　　107　　  　F12　　123　　Page Down 　　　34 
　　　　　　M　　　77 　　　Enter 108　　　　-- 　　--　　　End 　　　　　　35 
　　　　　　N　　　78 　　　-　　 109　　　　-- 　　-- 　　　Home　　　　　　36 
　　　　　　O　　　79 　　　. 　　110　　　　--　　 -- 　　 　Left Arrow　　　37 
　　　　　　P　　　80 　　　/ 　　111　　　　--　　 -- 　　 　Up Arrow　　　　38 
　　　　　　Q　　　81 　　　-- 　　--　　　 　--　　 -- 　　 　Right Arrow 　　39 
　　　　　　R　　　82 　　　-- 　　--　　　　--　　 -- 　　 　　Down Arrow 　　 40 
　　　　　　S　　　83 　　　-- 　　--　　　　　-- 　　-- 　　 　Insert 　　　　 45 
　　　　　　T　　　84 　　　-- 　　--　　　　　--　　 -- 　　 　Delete 　　　　 46 
　　　　　　U　　　85 　　　-- 　　--　　　 　-- 　　-- 　　 　Help 　　　　　 47 
　　　　　　V　　　86 　　　--　　 --　　　　-- 　　-- 　　 　Num Lock 　　　 144 
　　　　　　W　　　87 　　　　　　　　　
　　　　　　X　　　88 　　　　　
　　　　　　Y　　　89 　　　　　
　　　　　　Z　　　90 　　　　　
　　　　　　0　　　48 　　　　　
　　　　　　1　　　49 　　　　　
　　　　　　2　　　50 　　　　　　
　　　　　　3　　　51 　　　　　　
　　　　　　4　　　52 　　　　　　
　　　　　　5　　　53 　　　　　　
　　　　　　6　　　54 　　　　　　
　　　　　　7　　　55 　　　　　　
　　　　　　8　　　56 　　　　　　
　　　　　　9　　　57 　
'''