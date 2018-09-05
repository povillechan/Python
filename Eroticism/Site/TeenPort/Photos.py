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

        board        =  item('img').attr('src')
        product_url  =  item.attr('href')
        product_name =  item.text()
       
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            data = { 
            'board'   :  board,
            'url'     :  product_url,
            'name'    :  self.webParser.utils.format_name(product_name),
            }   
        else:            
            stills = []            
            for index in range(1, 13):
                stills.append(["%s/%02d.jpg"%(product_url, index) , "%s/%02dt.jpg"%(product_url, index)])
               
            site = ''    
            html = self.webParser.utils.get_page(product_url)   
            if html:
                b = pq(html)   
                site = b('div.title a:last-child').attr('title')
                
            data = {    
                'board'   :  board,
                'url'     :  product_url,
                'name'    :  self.webParser.utils.format_name(product_name),
                'stills'  :  stills,  
                'site'    :  site,
            }    
                
        return data 
    
    def parse_detail_fr_brief(self, item):
        data = deepcopy(item)
        
        product_url = item.get('product').get('url')
        
        html = self.webParser.utils.get_page(product_url)   
        if html:
            b = pq(html) 
            stills = []            
            for index in range(1, 13):
                stills.append(["%s/%02d.jpg"%(product_url, index) , "%s/%02dt.jpg"%(product_url, index)])
                 
            data.get('product')['stills']= stills 
            data.get('product')['site']  = b('div.title a:last-child').attr('title') 

        return data  
     

    def process_data(self, data):
        result = True
        sub_dir_name = "%s\\%s" %(data.get('product').get('site'),data.get('name'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)
            
        board = data.get('board')
        result &=  self.webParser.utils.download_file(board,
                                '%s\\%s' % (sub_dir_name, data.get('name')),    
                                 )                 
        
   
     
        stills = data.get('product').get('stills')
        for i, val in enumerate(stills, start=1): 
            for subVal in val:
                if subVal:
                    result &= self.webParser.utils.download_file(subVal,
                                     '%s\\galleries\\%s %s\\%s' % (sub_dir_name, data.get('name'), data.get('product').get('name'),str(i)),
                             )   
                    break
                
        board = data.get('product').get('board')
        result &=  self.webParser.utils.download_file(board,
                                     '%s\\galleries\\%s %s\\%s' % (sub_dir_name, data.get('name'), data.get('product').get('name'),data.get('product').get('name')),
                                 )    
        
        return result   
        
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('TeenPort')
        
    '''
    parse_page
    
    @author: chenzf
    ''' 
    def parse_page(self):
        urlsGen = self.urls_genarator()
        while True: 
            try:
                url = next(urlsGen)
                if not url:
                    yield None
                
                html = self.utils.get_page(url, headers={"Accept-Encoding":"",})     
                if html:
                    a = pq(html)   
                    #items
                    items = a('a.list_model')
                    
                    for item in items.items():
                        modelurl = item.attr('href')
                        name     = item('b').text()
                        board    = item('img').attr('src')

                        html = self.utils.get_page(modelurl)        
                        if html:
                            b = pq(html)                
                            products = b('a.list_model2')
                            for product in products.items():
                                product_data = self.common.parse_item(product)    
                                data = {
                                        'name': self.utils.format_name(name),
                                        'url' : modelurl,
                                        'board': board,
                                        'product': product_data}
                                                    
                                yield data
                    
                    self.log('parsed url %s' % url)      
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
    
                
                    
def Job_Start():
    print(__file__, "start!")
   
    job_list = [
#     ('S', 'http://www.teenport.com/galleries/wow-girls/'),
    ('S', 'http://www.teenport.com/galleries/teen-mega-world'),
    ('S', 'http://www.teenport.com/galleries/x-art'),
#     ('S', 'http://www.teenport.com/galleries/18-only-girls'),
    ('S', 'http://www.teenport.com/galleries/anal-angels'),
    ('S', 'http://www.teenport.com/galleries/tricky-masseur'),
    ('S', 'http://www.teenport.com/galleries/watch-me-fucked'),
    ('S', 'http://www.teenport.com/galleries/first-bgg'),
    ('S', 'http://www.teenport.com/galleries/cream-pie-angels'),
#     ('S', 'http://www.teenport.com/galleries/sexy-patty-cake'),
#     ('S', 'http://www.teenport.com/galleries/young-legal-porn'),
    ('S', 'http://www.teenport.com/galleries/18-stream'),
    ('S', 'http://www.teenport.com/galleries/nubiles/'),
    ('S', 'http://www.teenport.com/galleries/club-seventeen/'),
    
#     http://teenport.com/galleries/sandy-fair/
  
    ]
    
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default='TeenPort\\{filePath}')
    parser.add_argument('-p', type=int, default='0')
    args = parser.parse_args()
    print(args)
    for job_item in job_list:
        job = CWebParserSite(job_item[1], args.f, args.p)
        job.call_process()
        
if __name__ == '__main__':   
    Job_Start() 
