#__author:  Administrator
#date:  2017/2/15
import requests

response = requests.get('http://www.baidu.com')

url_list = [
    'http://www.baidu.com',
    'http://www.google.com',
    'http://dig.chouti.com',
    'http://www.bing.com',
]
for url in url_list:
    print('开始请求',url)
    response = requests.get(url=url)
    print('得到结果',response.url,response.content)