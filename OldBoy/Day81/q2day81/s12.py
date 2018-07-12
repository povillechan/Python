#__author:  Administrator
#date:  2017/2/15
# pip3 install grequests
import grequests


request_list = [
    grequests.get('http://httpbin.org/delay/1', timeout=0.001),
    grequests.get('http://fakedomain/'),
    grequests.get('http://httpbin.org/status/500')
]


# ##### 执行并获取响应列表 #####
response_list = grequests.map(request_list)
print(response_list)