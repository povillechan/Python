# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os
import time
import threading


class CWebLog(object):
    job_list = []
    dataLocker = threading.Lock()

    @staticmethod
    def log(logText, fileName=None):
        if fileName:
            dirName = os.path.dirname(fileName)
            if not os.path.exists(dirName):
                os.makedirs(dirName)

            with open(fileName, 'a+') as f:
                f.write('%s %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), logText))

        # CWebLog.dataLocker.acquire()
        # indent = threading.currentThread().ident
        # if indent in CWebLog.job_list:
        #     job_index = CWebLog.job_list.index(indent)
        # else:
        #     CWebLog.job_list.append(indent)
        #     job_index = len(CWebLog.job_list) - 1
        # CWebLog.dataLocker.release()
        #
        # cnt = 0
        # while cnt <= job_index:
        #     cnt = cnt + 1
        #     print("\r", end='', flush=True)
        #
        # print(indent, " ", logText, end=' ', flush=True)

        print(logText)
