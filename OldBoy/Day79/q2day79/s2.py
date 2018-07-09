#__author:  Administrator
#date:  2017/2/9
import requests


response = requests.get(
    url='https://www.zhihu.com/',
    headers={
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
)
print(response.text)