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
        product_name = item('img').attr('alt')
        product_url  = item.attr('href')
        
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            data = { 
                'name' : self.webParser.utils.format_name(product_name),
                'url'  : product_url,
            }   
        else:
            html = self.webParser.utils.get_page(product_url)   
            if html:
                b = pq(html) 
                
                previews = b('dt.gallery-icon a')
                stills = []
                for preview in previews.items():
                    stills.append(preview.attr('href'))  

                data = {   
                    'name' : self.webParser.utils.format_name(product_name), 
                    'url'  : product_url,
                    'stills'  :  stills,  
                }    
                    
        return data 
    
    def parse_detail_fr_brief(self, item):
        data = deepcopy(item)
        
        product_url = item.get('product').get('url')        
        html = self.webParser.utils.get_page(product_url)   
        if html:
            b = pq(html) 

            previews = b('dt.gallery-icon a')
            stills = []
            for preview in previews.items():
                stills.append(preview.attr('href'))                                 

            data.get('product')['stills']= stills 
             
        return data         

    def process_data(self, data):
        result = True
        sub_dir_name = "%s\\%s" %(data.get('model'), data.get('productName'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)
            
        stills = data.get('stills')
        for i, subVal in enumerate(stills, start=1):
            if subVal:
                result &= self.webParser.utils.download_file(subVal,
                                 '%s\\%s' % (sub_dir_name, str(i)),
                                headers={'Referer':data.get('productUrl')}
                         )   
        return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Erocurves')
        
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
                
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)   
                    #items
                    items = a('div.ts-responsive-wrap div.tshowcase-inner-box div.tshowcase-box-photo > a')
                    
                    for item in items.items():
                        modelurl = item.attr('href')
                        name     = item('img').attr('title')
                        board    = item('img').attr('src')                        

                        html = self.utils.get_page(modelurl)        
                        if html:
                            b = pq(html)                
                            products = b('div.home_tall_box > a')
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
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-s', type=int, default = 1)
    parser.add_argument('-e', type=int, default = 62)
    parser.add_argument('-f', type=str, default = 'Erocurves\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.erocurves.com/model-archives/?tpage={page}', args.s, args.e, args.f, args.p)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
