#__author:  Administrator
#date:  2017/2/15
import requests
from concurrent.futures import ProcessPoolExecutor

def async_url(url):
    response = None
    try:
        response = requests.get(url)
    except Exception as e:
        print('异常结果', response.url, response.content)
    print('获取结果',response.url,response.content)
    return response



url_list = [
    'http://www.baidu.com',
    'http://www.google.com',
    'http://dig.chouti.com',
    'http://www.bing.com',
]
# 创建线程池5
pool = ProcessPoolExecutor(5)
for url in url_list:
    print('开始请求',url)
    pool.submit(async_url, url)

pool.shutdown(wait=True)