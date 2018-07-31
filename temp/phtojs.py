# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
from selenium import webdriver
from bs4 import BeautifulSoup
browser = webdriver.Chrome()
browser.get('http://www.hegregirls.com/massage/countless-orgasms-massage')

soup = BeautifulSoup(browser.page_source, 'lxml')   
print(soup.select_one('.mejs-poster img').get('src'))

browser.close()