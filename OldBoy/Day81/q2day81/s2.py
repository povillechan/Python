#__author:  Administrator
#date:  2017/2/15
import requests
from concurrent.futures import ThreadPoolExecutor

def async_url(url):
    response = None
    try:
        response = requests.get(url)
    except Exception as e:
        print(e)

    return response
def callback(future,*args,**kwargs):
    from concurrent.futures._base import Future
    # print(future.result(),future._exception,args,kwargs)

url_list = [
    'http://www.baidu.com',
    'http://www.google.com',
    'http://www.bing.com',
]
# 创建线程池5
pool = ThreadPoolExecutor(5)
for url in url_list:
    v = pool.submit(async_url, url)
    # v.add_done_callback(callback)
pool.shutdown(wait=True)