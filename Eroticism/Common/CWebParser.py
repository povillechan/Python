# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os
import time
import json
import threading
from multiprocessing import cpu_count
import socket
from enum import Enum
from copy import deepcopy
import sys
import argparse


class CParseType(Enum):
    Parse_Entire = 0
    Parse_Brief = 1
    Parse_Detail = 2
    Parse_RealData = 3
    Parse_Detail2Brief = 4


class CWebParser(object):
    def __init__(self, savePath):
        self.parseOnly = 0
        self.savePath = 'H:\\Pictures\\' + savePath
        self.thread_num = None
        self.threadRunningCount = 1
        self.job_list = []

    '''
    parse_page
    
    @author: chenzf
    '''

    def parse_page(self):
        return None

    def parse_brief(self):
        return self.parse_page()

    def parse_detail(self):
        while True:
            try:
                items = self.dbUtils.get_db_item()
                if items.count() <= 0:
                    break

                for item in items:
                    yield item

                time.sleep(10)
            except:
                continue

        yield None

    def parse_detail_data(self):
        while True:
            try:
                items = self.dbUtils.get_db_detail_item()
                if items.count() <= 0:
                    break

                for item in items:
                    yield item

                time.sleep(10)
            except:
                continue

        yield None

    def parse_detail_to_brief(self):
        self.dbUtils.switch_db_detail_to_breif()

    '''
    process_image
    
    @author: chenzf
    '''

    def process_data(self, data):
        if self.parseOnly == CParseType.Parse_Entire or self.parseOnly == CParseType.Parse_RealData:
            if self.common.process_data(data):
                self.dbUtils.switch_db_detail_item(data)
            else:
                self.dbUtils.switch_db_one_detail_to_breif(data)
        elif self.parseOnly == CParseType.Parse_Brief:
            self.dbUtils.insert_db_item(data)
        elif self.parseOnly == CParseType.Parse_Detail:
            try:
                dataDetail = self.common.parse_detail_fr_brief(data)
                if dataDetail:
                    if self.args and self.args.l and self.args.l <= self.dbUtils.get_db_detail_item_count():
                        # self.log('process_data job limit reached, data dropped')
                        pass
                    else:
                        self.dbUtils.switch_db_item(data)
                        self.dbUtils.insert_db_detail_item(dataDetail)
            except:
                self.log('error in parse detail_fr_brief item')
            finally:
                self.pop_data_job(data)

        self.pop_data_job(data)

    def log(self, logText):
        fileName = self.savePath.format(filePath='Runlog.log')
        dirName = os.path.dirname(fileName)
        if not os.path.exists(dirName):
            os.makedirs(dirName)

        with open(fileName, 'a+') as f:
            f.write('%s %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), logText))

        print(logText)

    '''
    process
    
    @author: chenzf
    '''

    #     def sigint_handler(self, signum, frame):
    #         self.is_sigint_up = True
    #         print('catched interrupt signal!')

    def process(self):
        #         signal.signal(signal.SIGINT, self.sigint_handler)
        #         signal.signal(signal.SIGBREAK, self.sigint_handler)
        #         signal.signal(signal.SIGTERM, self.sigint_handler)
        #
        #         self.is_sigint_up = False
        socket.setdefaulttimeout(30)
        try:
            datas = None
            if self.parseOnly == CParseType.Parse_Entire:
                datas = self.parse_page()
            elif self.parseOnly == CParseType.Parse_Brief:
                datas = self.parse_brief()
            elif self.parseOnly == CParseType.Parse_Detail:
                datas = self.parse_detail()
            elif self.parseOnly == CParseType.Parse_Detail2Brief:
                self.parse_detail_to_brief()
                return
            else:
                datas = self.parse_detail_data()

            self.dataLocker = threading.Lock()
            #             while True:
            #                 data = next(datas)
            #                 if data:
            #                     self.process_data(data)
            #                 else:
            #                     break

            thread_list = []
            t = threading.Thread(target=self.job_thread, args=(datas,))
            t.start()
            thread_list.append(t)
            if self.thread_num:
                thread_num = self.thread_num
            else:
                thread_num = cpu_count() - 1
            #             thread_num = 1
            #             if self.parseOnly == 1 or self.parseOnly == 2:
            #                 thread_num = 0

            for i in range(thread_num):  # 创建10个线程
                t = threading.Thread(target=self.process_thread)
                t.start()
                thread_list.append(t)

            for t in thread_list:
                t.join()
        except:
            print('error occured in parse image')

    # vthread
    #     def process(self):
    #         try:
    #             datas = self.parse_page()
    #             while True:
    #                 data = next(datas)
    #                 if data:
    #                     self.process_data(data)
    #                 else:
    #                     break
    #         except:
    #             print('error occured in parse image')

    def job_thread(self, datas):
        #         times = 0
        while True:
            data = next(datas)
            while True:
                rel = self.push_data_job(data)
                if not rel:
                    time.sleep(1)
                else:
                    break

            if not data:
                # print("job parse ended!")
                return

    def process_thread(self):
        while True:
            try:
                data, endFlag = self.get_data_job()
                if not data and not endFlag:
                    time.sleep(1)
                    continue
                elif not data and endFlag:
                    print('thread end!')
                    return

                self.process_data(data)
                time.sleep(1)

            except Exception as e:
                print(e)
                continue

    def push_data_job(self, data):
        rel = True
        self.dataLocker.acquire()
        if self.thread_num:
            thread_num = self.thread_num
        else:
            thread_num = cpu_count() - 1

        if len(self.job_list) >= thread_num:
            # print('Job full, need waitting')
            rel = False
        elif self.args and self.args.l and self.parseOnly == CParseType.Parse_Detail and self.args.l <= self.dbUtils.get_db_detail_item_count():
            # print('Job limit reached, need pending')
            rel = False
        else:
            self.job_list.append({"status": 0,
                                  "data": data})
            # print('New job is pushed, size %s' % len(self.job_list))
            rel = True
        # print('thread %s leave push data' % threading.currentThread())
        self.dataLocker.release()
        return rel

    def pop_data_job(self, data):
        self.dataLocker.acquire()
        for i in range(0, len(self.job_list)):
            if self.job_list[i].get("data") == data:
                # print('a job is popped, size %s, index %s' % (len(self.job_list), i))
                del self.job_list[i]
                break

        self.dataLocker.release()

    def get_data_job(self):
        data = None
        self.dataLocker.acquire()
        endflag = False
        self.threadRunningCount += 1
        if self.threadRunningCount > 50:
            print("thread [%s]" % os.getpid(), 'job thread [%s]' % len(self.job_list), os.path.abspath(sys.argv[0]),
                  str(sys.argv[1:]))
            self.threadRunningCount = 1

        if len(self.job_list) >= 1:
            if not self.job_list[0].get("data"):
                data = None
                endflag = True
            else:
                for i in range(0, len(self.job_list)):
                    if self.job_list[i].get("status") == 0:
                        data = self.job_list[i].get('data')
                        self.job_list[i]["status"] = 1
                        # print('A job is getted, size %s, index %s' % (len(self.job_list),i))
                        break
        else:
            data = None

        self.dataLocker.release()
        return data, endflag

    def save_info(self, data):
        dir_name = self.savePath.format(filePath=data.get('name'))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(dir_name + '\\info.json', 'w') as f:
            json.dump(data, f)

    def urls_genarator(self):
        return None

    def call_process(self):
        self.process()

    def param_parse(self):
        parser = argparse.ArgumentParser(description='manual to this script')
        parser.add_argument('-s', type=int, default=None)
        parser.add_argument('-e', type=int, default=None)
        parser.add_argument('-f', type=str, default=None)
        parser.add_argument('-p', type=int, default='0')
        parser.add_argument('-t', type=int, default=cpu_count() - 1)
        parser.add_argument('-u', type=str, default=None)
        parser.add_argument('-l', type=int, default=None)
        self.args = parser.parse_args()


class CWebParserMultiUrl(CWebParser):
    # def __init__(self, url, start, end, savePath):
    def __init__(self, **kwArgs):
        super().param_parse()
        try:
            # save path
            if self.args.f:
                super().__init__(self.args.f)
                self.savePath = self.args.f + "\\{filePath}"
            elif kwArgs.get('savePath'):
                super().__init__(kwArgs.get('savePath'))
            else:
                raise Exception('no save path!')

            # url
            if self.args.u:
                self.url = self.args.u
            elif kwArgs.get('url'):
                self.url = kwArgs.get('url')
            else:
                raise Exception('no url!')

            # start
            if self.args.s:
                self.start = self.args.s
            elif kwArgs.get('start') is not None:
                self.start = kwArgs.get('start')
            else:
                raise Exception('no start positon!')

            # end
            if self.args.e:
                self.end = self.args.e
            elif kwArgs.get('end') is not None:
                self.end = kwArgs.get('end')
            else:
                raise Exception('no end positon!')

            # thread num
            self.thread_num = self.args.t

            # parse only
            self.parseOnly = CParseType(self.args.p)

        except Exception as e:
            print(e)
            exit()

    def urls_genarator(self):
        for i in range(self.start, self.end + 1):
            yield self.url.format(page=i)
        yield None


class CWebParserSingleUrl(CWebParser):
    def __init__(self, **kwArgs):
        super().param_parse()
        try:
            self.start = None
            self.end = None
            # save path
            if self.args.f:
                super().__init__(self.args.f)
                self.savePath = self.args.f + "\\{filePath}"
            elif kwArgs.get('savePath'):
                super().__init__(kwArgs.get('savePath'))
            else:
                raise Exception('no save path!')

            # url
            if self.args.u:
                self.url = self.args.u
            elif kwArgs.get('url'):
                self.url = kwArgs.get('url')
            else:
                raise Exception('no url!')

            # thread num
            self.thread_num = self.args.t

            # parse only
            self.parseOnly = CParseType(self.args.p)
        except Exception as e:
            print(e)
            exit()

    def urls_genarator(self):
        yield self.url
        yield None
