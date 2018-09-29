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
from Common.CWebParserProcess import CWebParserProcess
from copy import deepcopy
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import vthread
import pymongo
from copy import deepcopy

class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)
#    
    def parse_item(self, item):   
        data = None   
#         product_name = item('img').attr('alt')
        product_url  = item.attr('href')        
                            
        data_brief = { 
            'url'  : product_url,    
            }   
        
        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data 
        else:                    
            return self.parse_detail_fr_brief(data) 
    
    def parse_detail_fr_brief(self, item):
        data = None 
        
        product_url = item.get('brief').get('url')        
        html = self.webParser.utils.get_page(product_url)   
        if html:
            b = pq(html) 
                
            previews = b('dt.gallery-icon a')
            stills = []
            for preview in previews.items():
                stills.append(preview.attr('href'))  
                               
            product_name = b('div.single_inside_content h1').text()
            data_detail = {
                    'galleries': {
                        'name' : self.webParser.utils.format_name(product_name),
                        'url'  : product_url,
                        'stills':stills,
                        }
                    }  
            
            data = deepcopy(item)
            data['detail'] = data_detail
             
        return data         

  
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Gyrls')
        
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
                        modelsearch = modelurl 
                        name     = item('img').attr('title')
                        board    = item('img').attr('src')
                        
                        try:
                            while modelsearch is not None:
                                html = self.utils.get_page(modelsearch)    
                                    
                                if html:
                                    b = pq(html)                       
                                    if self.dbUtils.get_db_url(modelsearch):
                                        pass
                                    else:                
                                        products = b('div.home_box > a')
                                        for product in products.items():
                 
                                            data_p = self.common.parse_item(product)    
                                            data_t = {
                                                    'name': self.utils.format_name(name),
                                                    'url'  :   modelurl,
                                                    'board':   board,
                                                    'refurl':  modelurl
                                                    }
                    
                                            data = dict( data_t, **data_p )                                          
                                            yield data
                                            
                                        self.dbUtils.put_db_url(modelsearch)      
                                    nexturl = b ('link[rel=next]')
                                    if nexturl:
                                        modelsearch = nexturl.attr('href')
                                    else:
                                        modelsearch = None                                
                                else:
                                    modelsearch = None
                        except:
                            continue
                    
                    self.log('parsed url %s' % url)      
                else:
                    self.log('request %s error' %url)         
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log( 'error in parse url %s' % url)         
                continue    
        
        yield None      
                
                    
def Job_Start():
    print(__file__, "start!")
   
    job_list = [
    ('S', 'http://www.gyrls.com/models/?search=&tshowcase-categories='), 
    ]
    
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default='Gyrls\\{filePath}')
    parser.add_argument('-p', type=int, default='0')
    args = parser.parse_args()
    print(args)
    for job_item in job_list:
        job = CWebParserSite(job_item[1], args.f, args.p)
        job.call_process()
        
if __name__ == '__main__':   
    Job_Start() 
