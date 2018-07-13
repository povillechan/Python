# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import requests
import re
from requests.exceptions import RequestException
from multiprocessing import Pool

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}

def get_one_page(url):
#    print(url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException as e:
        print(e)
        
def parse_one_page(html):
#    print(html.strip())
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?<a.*?title="(.*?)".*?<p class="star">(.*?)</p>.*?<i class="integer">(.*?)</i>.*?<i class="fraction">(.*?)</i>', re.S)
    result = re.findall(pattern, html.strip())
    for item in result:
        a = tuple(map(lambda x: x.strip(), item))
#       print(item[0].strip()+"-<<"+ item[1].strip()+">> "+ item[2].strip()+"  Score:" + item[3].strip()+item[4].strip())
        print("%s-<<%s>> %s  Score:%s%s" % a)

def main(offset):        
#    print(requests.get('http://maoyan.com/board/4', headers=headers).text)
#     for index in range(0,10):    
    content = get_one_page('http://maoyan.com/board/4?offset=%s' % (offset))
    parse_one_page(content)      

if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])