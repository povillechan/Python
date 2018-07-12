#__author:  Administrator
#date:  2017/2/15
from twisted.web.client import getPage
from twisted.internet import reactor


class TwistedRequest(object):
    def __init__(self):
        self.__req_counter = 0
        self.__rev_counter = 0

    def __execute(self, content, url, callback):
        if callback:
            callback(url, content)
        self.__rev_counter += 1
        if self.__rev_counter == self.__req_counter:
            reactor.stop()

    def fetch_url(self, url_callback_list):

        self.__req_counter = len(url_callback_list)

        for item in url_callback_list:
            url = item['url']
            print(url)
            success_callback = item['success_callback']
            error_callback = item['error_callback']
            # 发送URL请求
            deferred = getPage(bytes(url, encoding='utf8'))
            # 当请求成功后，执行__execute，传入参数
            deferred.addCallback(self.__execute, url, success_callback)
            deferred.addErrback(self.__execute, url, error_callback)

        reactor.run()


def callback(url, content):
    print(url, content)


def error(url, content):
    print(url, content)


obj = TwistedRequest()
obj.fetch_url([
    {'url': 'http://www.baidu.com', 'success_callback': callback, 'error_callback': error},
    {'url': 'http://www.cnblogs.com', 'success_callback': callback, 'error_callback': error},
])