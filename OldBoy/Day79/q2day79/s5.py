#__author:  Administrator
#date:  2017/2/9
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests


# ############## 方式一 ##############

# ## 1、首先登陆任何页面，获取cookie
i1 = requests.get(url="http://dig.chouti.com/help/service")
i1_cookies = i1.cookies.get_dict()

# ## 2、用户登陆，携带上一次的cookie，后台对cookie中的 gpsd 进行授权
i2 = requests.post(
    url="http://dig.chouti.com/login",
    data={
        'phone': "8615131255089",
        'password': "xxoo",
        'oneMonth': ""
    },
    cookies=i1_cookies
)

# ## 3、点赞（只需要携带已经被授权的gpsd即可）
gpsd = i1_cookies['gpsd']
i3 = requests.post(
    url="http://dig.chouti.com/link/vote?linksId=10256240",
    cookies={'gpsd': gpsd}
)

print(i3.text)

