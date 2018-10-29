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
from multiprocessing import cpu_count

class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)
#    
    def parse_item(self, item):   
        data = None   

        board        =  item('img').attr('src')
        product_url  =  item.attr('href')
        product_name =  item.text()
        
        data_brief = { 
            'url'  : product_url,
            'board': board  ,  
            'name' : self.webParser.utils.format_name(product_name)
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
            stills = []            
            for index in range(1, 13):
                stills.append("%s/%02d.jpg"%(product_url, index))

            data_detail = {
                    'galleries': {
                        'name' : item.get('brief').get('name'),
                        'url'  : product_url,
                        'stills':stills,
                        'board': item.get('brief').get('board'),
                        'site' : b('div.title a:last-child').attr('title') 
                        }
                    }  
            
            data = deepcopy(item)
            data['detail'] = data_detail
             
        return data    

    def get_sub_dir_name(self,data):
        sub_dir_name = "%s\\%s" %(data.get('detail').get('galleries').get('site'), data.get('name'))
        return sub_dir_name      
        
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly, threadNum):
        super().__init__(url, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('TeenPort')
        self.thread_num = threadNum
                
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
                        
                        if self.dbUtils.get_db_url(modelurl):
                            continue
                        
                        html = self.utils.get_page(modelurl)        
                        if html:
                            b = pq(html)                
                            products = b('a.list_model2')
                            try:
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
                            except:
                                continue          
                                               
                            self.dbUtils.put_db_url(modelurl)    
                    self.log('parsed url %s' % url)      
                else:
                    self.log('request %s error' %url)  
            except (GeneratorExit, StopIteration):
                break       
            except:
                self.log( 'error in parse url %s' % url)         
                yield None    
        
        yield None  
              
                    
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
    parser.add_argument('-t', type=int, default=  cpu_count() - 1) 
    args = parser.parse_args()
    print(args)
    for job_item in job_list:
        job = CWebParserSite(job_item[1], args.f, args.p, args.t)
        job.call_process()
        
if __name__ == '__main__':   
    Job_Start() 
