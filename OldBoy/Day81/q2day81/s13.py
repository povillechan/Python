#__author:  Administrator
#date:  2017/2/15
# pip3 install twisted
# pip3 install wheel
#       b. 下载twisted http://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted
#       c. 进入下载目录，执行 pip3 install Twisted‑17.1.0‑cp35‑cp35m‑win_amd64.whl


from twisted.web.client import getPage
from twisted.internet import reactor

REV_COUNTER = 0
REQ_COUNTER = 0

def callback(contents):
    print(contents,)

    global REV_COUNTER
    REV_COUNTER += 1
    if REV_COUNTER == REQ_COUNTER:
        reactor.stop()


url_list = ['http://www.bing.com', 'http://www.baidu.com', ]
REQ_COUNTER = len(url_list)
for url in url_list:
    print(url)
    deferred = getPage(bytes(url, encoding='utf8'))
    deferred.addCallback(callback)
reactor.run()