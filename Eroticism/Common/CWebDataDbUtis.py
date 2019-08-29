# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import pymongo
from Common.CWebLog import CWebLog

class CWebDataDbUtis(object):
    def __init__(self, clientName):
        self.dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.dbname = self.dbclient[clientName]
        self.dbUrl = self.dbname["datas_url"]
        self.dbBriefJob = self.dbname["datas_brief"]
        self.dbBriefJobParsed = self.dbname["datas_brief_parsed"]
        self.dbBriefJobNoParsed = self.dbname["datas_brief_no_parsed"]
        self.dbBriefJobError = self.dbname["datas_brief_error"]
        self.dbDetailJob = self.dbname["datas_detail"]
        self.dbDetailJobParsed = self.dbname["datas_detail_parsed"]
        self.dbDetailJobError = self.dbname["datas_detail_error"]

    def put_db_url(self, url):
        data = {'url': url}
        if self.dbUrl.find_one(data):
            pass
        else:
            self.dbUrl.insert_one(data)

    def get_db_url(self, url):
        data = {'url': url}
        if self.dbUrl.find_one(data):
            return data
        return None

    def get_db_item(self):
        return self.dbBriefJob.find()

    def get_db_item_count(self):
        return self.dbBriefJob.count()

    def insert_db_item(self, data):
        if self.dbBriefJob.find_one(data) or self.dbBriefJobParsed.find_one(data):
            CWebLog.log('data already in database <brief>!')
        else:
            self.dbBriefJob.insert_one(data)
            CWebLog.log('data insert in database <brief>!')

    def switch_db_item(self, data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbBriefJob.find_one(data):
            self.dbBriefJob.delete_one(data)
        if not self.dbBriefJobParsed.find_one(data):
            self.dbBriefJobParsed.insert_one(data)

    def switch_db_item_no_parsed(self, data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbBriefJob.find_one(data):
            self.dbBriefJob.delete_one(data)
        if not self.dbBriefJobNoParsed.find_one(data):
            self.dbBriefJobNoParsed.insert_one(data)

    def switch_db_item_error(self, data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbBriefJob.find_one(data):
            self.dbBriefJob.delete_one(data)
        if not self.dbBriefJobError.find_one(data):
            self.dbBriefJobError.insert_one(data)

    def get_db_detail_item(self):
        return self.dbDetailJob.find()

    def get_db_detail_item_count(self):
        return self.dbDetailJob.count()

    def insert_db_detail_item(self, data):
        if self.dbDetailJob.find_one(data) or self.dbDetailJobParsed.find_one(data):
            CWebLog.log('data already in database <detail>!')
        else:
            self.dbDetailJob.insert_one(data)
            CWebLog.log('data insert in database <detail>!')

    def switch_db_detail_item(self, data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbDetailJob.find_one(data):
            self.dbDetailJob.delete_one(data)
        if not self.dbDetailJobParsed.find_one(data):
            self.dbDetailJobParsed.insert_one(data)

    def switch_db_detail_item_error(self, data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbDetailJob.find_one(data):
            self.dbDetailJob.delete_one(data)
        if not self.dbDetailJobError.find_one(data):
            self.dbDetailJobError.insert_one(data)

    def switch_db_detail_to_breif(self):
        for item in self.get_db_detail_item():
            self.switch_db_one_detail_to_breif(item)

    def switch_db_one_detail_to_breif(self, data):
        self.dbDetailJob.delete_one(data)

        data.pop('_id')
        data.pop('detail')

        if self.dbBriefJobParsed.find_one(data):
            self.dbBriefJobParsed.delete_one(data)

        self.dbBriefJob.insert_one(data)

    def switch_db_brief_noparse_to_brief(self):
        for data in self.dbBriefJobNoParsed.find():
            if data.get('_id'):
                data.pop('_id')
            if not self.dbBriefJob.find_one(data):
                self.dbBriefJob.insert_one(data)
            self.dbBriefJobNoParsed.delete_one(data)

    def parse_clear_url(self):
        self.dbUrl.remove()
