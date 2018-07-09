# __author:  Administrator
# date:  2017/2/9
# pip3 install requests

"""
import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.sogou.com/web?query=搞基建')
# print(response.text)

soup = BeautifulSoup(response.text, 'html.parser')
news_list = soup.find_all(name='div',class_='vrwrap')
print(news_list)
"""

"""
import requests

form_data = {
    'phone': 'asdf',
    'password': 'asdf',
    'oneMonth': 1
}
response = requests.post(
    url='http://dig.chouti.com/login',
    data=form_data
)
print(response.text)

# requests.put()
# requests.delete()
# requests.head()
# requests.options()
# requests.options()
"""
import requests
import json
requests.request(
    method='post',
    url='http://127.0.0.1:8000/test/',
    params={'query': '搞基建','q':'b'},  # "query=搞基建&q=b,"
    # data={'user':'alex','pwd':'sdfsdf'} # "user=alex;pwd=sdfsdf"    # content-type: application/x-www-form-urlencoded
    json=json.dumps({'user':'alex','pwd':'sdfsdf'}), # content-type: application/json
    headers={
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    },
    cookies={
        '.CNBlogsCookie': '128F6D14E7E5608652CF5A9338526A6C9B4B4CFE0BD85EC625DBAFADD93E0CBB8078415C72486FA8366113E622BDD18D873E6AF46238BE38ECB047FDF85DBB490C26E3983E72418FE9FFE2075D47F637347BEFA1'
    }
)

# def index(request):
#     request.method=> "post"
#     request.GET.get('query')
#     request.POST.get('user')