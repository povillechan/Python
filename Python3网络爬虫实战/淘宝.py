# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

# import requests
# import re
# from urllib import parse
# from requests.exceptions import RequestException
# from multiprocessing import Pool
# from django.template.defaultfilters import urlencode
# import json
# from bs4 import BeautifulSoup
# from string import hexdigits
# from hashlib import md5
# import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
from pyquery import PyQuery as pq
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}

#     
# if __name__ == '__main__':

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def search():
    browser.get('http://www.taobao.com/')
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))                                            
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button")))
        
        input.send_keys('美食')
        submit.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.total")))
        
        return total.text
    except TimeoutException as e:
        print(e)
        return search()
        

def next_page(page_number):
    print("current page %s" % page_number)
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))                                            
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
        
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"), str(page_number)
        ))
        

    except TimeoutException as e:
        print(e)
        return next_page(page_number)
       
    get_products()
    
def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item"))) 
    html = browser.page_source

    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    products=[]
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal':  item.find('.deal-cnt').text()[:-3],
            'title' : item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
            }
        print(product)
        products.append(product)
    return products
    
def main():
    total = search()
    total = int(re.compile('(\d+)').search(total).group(1))
    print(total)
    for i in range(2,total):
        next_page(i)
    
if __name__ == '__main__':
    main()



