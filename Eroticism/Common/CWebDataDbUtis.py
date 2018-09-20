# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import vthread
import os
import pymongo

        
class CWebDataDbUtis(object):
    def __init__(self, clientName):
        self.dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.dbname             = self.dbclient[clientName]
        self.dbUrl              = self.dbname["datas_url"]
        self.dbBriefJob         = self.dbname["datas_brief"]
        self.dbBriefJobParsed   = self.dbname["datas_brief_parsed"]      
        self.dbBriefJobError    = self.dbname["datas_brief_error"]      
        self.dbDetailJob        = self.dbname["datas_detail"]
        self.dbDetailJobParsed  = self.dbname["datas_detail_parsed"]     
        self.dbDetailJobError   = self.dbname["datas_detail_error"]    
     
                     
    def put_db_url(self, url):
        data = {'url': url}
        if self.dbUrl.find_one(data):
            pass
        else:
            self.dbUrl.insert_one(data)
    
    def get_db_url(self,url):
        data = {'url': url} 
        if self.dbUrl.find_one(data):
            return data
        return None
                
    def get_db_item(self):
        return self.dbBriefJob.find() 
    
    def insert_db_item(self,data):
        if self.dbBriefJob.find_one(data) or self.dbBriefJobParsed.find_one(data):
            print('data already in database <brief>!')
        else:
            self.dbBriefJob.insert_one(data)
            print('data insert in database <brief>!')
          
    def switch_db_item(self,data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbBriefJob.find_one(data):
            self.dbBriefJob.delete_one(data)
        if not self.dbBriefJobParsed.find_one(data):
            self.dbBriefJobParsed.insert_one(data)
            
    def switch_db_item_error(self,data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbBriefJob.find_one(data):
            self.dbBriefJob.delete_one(data)
        if not self.dbBriefJobError.find_one(data):
            self.dbBriefJobError.insert_one(data)
            
    def get_db_detail_item(self):
        return self.dbDetailJob.find()  
    
    def insert_db_detail_item(self,data):
        if self.dbDetailJob.find_one(data) or self.dbDetailJobParsed.find_one(data):
            print('data already in database <detail>!')
        else:
            self.dbDetailJob.insert_one(data)
            print('data insert in database <detail>!')
      
    def switch_db_detail_item(self,data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbDetailJob.find_one(data):
            self.dbDetailJob.delete_one(data)
        if not self.dbDetailJobParsed.find_one(data):
            self.dbDetailJobParsed.insert_one(data)
            
    def switch_db_detail_item_error(self,data):
        if data.get('_id'):
            data.pop('_id')
        if self.dbDetailJob.find_one(data):
            self.dbDetailJob.delete_one(data)
        if not self.dbDetailJobError.find_one(data):
            self.dbDetailJobError.insert_one(data)
        