import requests
from contextlib import closing

Headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.12 Safari/537.36",
#    'Referer':'http://cdn-movies.pizzapiez.com/0/43/43350/NOWATERMARK_240.mp4?validfrom=1534408780&validto=1534415980&ip=121.237.157.221&rate=50k&burst=2mb&hash=kUkEs7lIyDuVNS%2BK7tLzckT48Sc%3D',
#     'Host': 'cdn-movies.pizzapiez.com',
#     'Upgrade-Insecure-Requests': '1',
#     'Range': 'bytes=0-',
#     'If-Range': '"1d910687c-4cd7024-521effae89480"',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
#     'Accept-Encoding': 'identity;q=1, *;q=0',
#     'chrome-proxy': 'frfr',
}
cookies = {
    'csrfst':'ZjokoUNp-1534409214-0777863d7a850e30'
}
url = 'http://cdn-movies.pizzapiez.com/0/43/43350/NOWATERMARK_240.mp4?validfrom=1534408780&validto=1534415980&ip=121.237.157.221&rate=50k&burst=2mb&hash=kUkEs7lIyDuVNS%2BK7tLzckT48Sc%3D'
# url = 'http://cdn-movies.pizzapiez.com/0/43/43350/NOWATERMARK_240.mp4'

# response = requests.get(url,headers=Headers,timeout=30, )
# print(response.content)
# 
# with closing(requests.get(url, headers=Headers,timeout=30, stream=True)) as response:
    
response = (requests.get(url, headers=Headers,timeout=30, stream=True))
print(response.status_code)
chunk_size = 512 
for data in response.iter_content(chunk_size=chunk_size):
      print(data)
# response = requests.get(url,headers=Headers,timeout=30, )
# print(response.content)