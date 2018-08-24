# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json
import argparse
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParser import CWebParserMultiUrl,CWebParserCommon
from Common.CWebSpiderUtils import CWebSpiderUtils
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import vthread
import pymongo
from copy import deepcopy

from Models import CWebParserSite

class CWebParserSiteDb(CWebParserSite):    
    def __init__(self, savePath, parseOnly):
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.parseOnly = parseOnly  
        self.common = CWebParserHunterCommon(self)    
        self.dbUtils = CWebDataDbUtis('PornVidHub')
                 
    '''
    parse_page
    
    @author: chenzf
    ''' 
    def parse_page(self):
      
        while True: 
            try:
                if self.parseOnly == 1:
                    for item in self.dbUtils.get_db_item():
                        data = deepcopy(item)
                        data.pop('_id')               
                        try:
                            step = 1
                            url = data.get('videos')[0].get('url')                                       
                            step = 2
                            if url:
                                video, still= self.parse_video_detail(url)
                                step = 3
    
                                if not video or still ==[]:
                                    continue
                                
                                data.get('videos')[0]['video'] = video
                                data.get('videos')[0]['stills'] = still
                                
                                self.common.switch_db_item(item)
                                datatmp = deepcopy(data)
                                self.common.insert_db_detail_item(datatmp)
                                
                                yield data
                            else:
                                data['videos'] = []                            
                                yield data 
                            step = 7
                    except:
                        self.log('error in parse item %s , step %s' % (modelurl, step))   
                        continue  
                else:
                    for item in self.dbUtils.get_db_detail_item():
                        data = deepcopy(item)
                        data.pop("_id")
                        yield data    
            except:
                self.log('error in parse %s' % url)
#                 browser.close_chrome()
                yield None    
#         browser.close_chrome()
        yield None
        
    '''
    process_image
     
    @author: chenzf
    '''    
    def process_data(self, data):
        if self.parseOnly == 1:
            return 
        
        if self.common.process_data(data):
            self.dbUtils.switch_db_detail_item(data)
             
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default = 'd:\\Pictures\\WebSpider\\PornVidHub\\Models\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSiteDb(args.f,args.p)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
