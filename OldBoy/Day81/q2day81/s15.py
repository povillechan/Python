#__author:  Administrator
#date:  2017/2/15
# pip3 install tornado

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import ioloop


def handle_response(response):
    if response.error:
        print("Error:", response.error)
    else:
        print(response.body)
        # 方法同twisted
        ioloop.IOLoop.current().stop()


def func():
    url_list = [
        'http://www.cnblogs.com',
        'http://www.bing.com',
    ]
    for url in url_list:
        print(url)
        http_client = AsyncHTTPClient()
        http_client.fetch(HTTPRequest(url), handle_response)


ioloop.IOLoop.current().add_callback(func)
# print(type(ioloop.IOLoop.current()))

ioloop.IOLoop.current().start()
# from tornado.platform.select import SelectIOLoop