# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json
import argparse
from copy import deepcopy
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParser import CParseType,CWebParser,CWebParserMultiUrl,CWebParserSingleUrl
from Common.CWebDataDbUtis import CWebDataDbUtis
from Common.CWebSpiderUtils import CWebSpiderUtils
from copy import deepcopy
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import vthread
import pymongo
from copy import deepcopy

class CWebParserSiteCommon(object):
    def __init__(self, webParser):
        self.webParser = webParser
#    
    def parse_item(self, item):   
        data = None   
        product_name  =  item.attr('title')
        product_url   =  item.attr('href')
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            data = { 
                    'url'     :  product_url,
                    'name'    :  self.webParser.utils.format_name(product_name),
            }   
        else:
            html = self.webParser.utils.get_page(product_url)   
            if html:
                b = pq(html)                                    
                stills = []            
                previews = b('div.masonry_thumbs div.item div.masonry_item > a')
                for preview in previews.items():
                    stills.append(preview('a').attr('href'))
                    
                data = {    
                    'url'     :  product_url,
                    'name'    :  self.webParser.utils.format_name(product_name),
                    'stills'  :  stills,  
                }    
                    
        return data 
    
    def parse_detail_fr_brief(self, item):
        data = deepcopy(item)
        
        product_url = item.get('product').get('url')
        
        html = self.webParser.utils.get_page(product_url)   
        if html:
            b = pq(html)                                    
            stills = []            
            previews = b('div.masonry_thumbs div.item div.masonry_item > a')
            for preview in previews.items():
                stills.append(preview('a').attr('href'))                    
                
            data.get('product')['stills']= stills 

        return data         

    def process_data(self, data):
        result = True
        sub_dir_name = "%s\\%s" %(data.get('name'),data.get('product').get('name'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)   
     
        stills = data.get('product').get('stills')
        for i, subVal in enumerate(stills, start=1): 
            if subVal:
                result &= self.webParser.utils.download_file(subVal,
                                 '%s\\%s' % (sub_dir_name, str(i)),
                         )         
        return result   
    
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Faponix')
        
    '''
    parse_page
    
    @author: chenzf
    ''' 
    def parse_page(self):
        urlsGen = self.urls_genarator()
        while True: 
            try:
                url, name = next(urlsGen)
                if not url:
                    yield None
                                
                if self.dbUtils.get_db_url(url):
                    continue
                
                data_total = 0
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)   
                    data_total = a('button.js-load-more').attr('data-total')
                    
                if int(data_total) > 0:
                    for page in range(1, int(data_total)+1):
                        try:
                            cate_url = '%s?mode=async&action=get_block&block_id=list_albums_common_albums_list&from=%s' %(url,page)
                                  
                            if self.dbUtils.get_db_url(cate_url):
                                continue
                            
                            html = self.utils.get_page(cate_url)     
                            if html:
                                b = pq(html)   
                    
                                items = b('div.masonry_item >a')
                    
                                for item in items.items(): 
                                    product_data = self.common.parse_item(item)    
                                    data = {
                                        'name':    self.utils.format_name(name),
                                        'product': product_data}
                                                    
                                    yield data
                                self.dbUtils.put_db_url(cate_url) 
                        except:
                            continue
                    self.log('parsed url %s' % url)      
                    self.dbUtils.put_db_url(url) 
                else:
                    self.log('request %s error' %url)         
            except:
                self.log( 'error in parse url %s' % url)         
                yield None    
        
        yield None  
        
    '''
    process_image
    
    @author: chenzf
    '''    
    def process_data(self, data):
        if self.parseOnly == CParseType.Parse_Entire or self.parseOnly == CParseType.Parse_RealData:
            if self.common.process_data(data):
                self.dbUtils.switch_db_detail_item(data)            
        elif self.parseOnly == CParseType.Parse_Brief:
            datatmp = deepcopy(data)
            self.dbUtils.insert_db_item(datatmp)
        elif self.parseOnly == CParseType.Parse_Detail:
            try:
                dataDetail = self.common.parse_detail_fr_brief(data)  
                if dataDetail:
                    self.dbUtils.switch_db_item(data)
                    self.dbUtils.insert_db_detail_item(dataDetail)
            except:
                self.log('error in parse detail_fr_brief item')       
    
    '''
    urls_genarator
    
    @author: chenzf
    '''                  
    def urls_genarator(self):
        html = self.utils.get_page(self.url)     
        if html:
            a = pq(html)
            categorys = a('div.masonry_item a')
            for category in categorys.items():
                yield category.attr('href'), category.attr('title')
        yield None       
        
                
def Job_Start():
    print(__file__, "start!")
   
    job_list = [
    ('S', 'https://www.faponix.com/categories/'), 
    ]
    
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default='Faponix\\{filePath}')
    parser.add_argument('-p', type=int, default='0')
    args = parser.parse_args()
    print(args)
    for job_item in job_list:
        job = CWebParserSite(job_item[1], args.f, args.p)
        job.call_process()
        
if __name__ == '__main__':   
    Job_Start() 
