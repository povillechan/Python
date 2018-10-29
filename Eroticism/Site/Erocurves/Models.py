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
# #         product_name = item('img').attr('alt')
        product_url  = item.attr('href')        
#                   
#         data = { 
#             'url'  : product_url,
#         }   
#         
#         if self.webParser.parseOnly == CParseType.Parse_Brief:                             
#             return data 
#         else:                    
#             return self.parse_detail_fr_brief(data) 
        
        
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
               
            product_name = b('h1.single_title').text()   
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

#     def process_data(self, data):
#         result = True
#         sub_dir_name = "%s\\%s" %(data.get('name'), data.get('product').get('name'))
#        
#         dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
#         if not os.path.exists(dir_name):
#             os.makedirs(dir_name)
#         
#         with open(dir_name + '\\info.json', 'w') as f:    
#             json.dump(data, f)
#             
#         board = data.get('board')
#         if board:
#             result &=  self.webParser.utils.download_file(board,
#                                      '%s\\..\\%s' % (sub_dir_name, data.get('name'))
#                                      )   
#         
#         stills = data.get('product').get('stills')
#         for i, subVal in enumerate(stills, start=1):
#             if subVal:
#                 result &= self.webParser.utils.download_file(subVal,
#                                  '%s\\%s' % (sub_dir_name, str(i))                                
#                          )   
#         return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly, threadNum):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Erocurves')
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
                
                if self.dbUtils.get_db_url(url):
                    continue
                
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
#                                 product_data = self.common.parse_item(product)    
#                                 data = {
#                                         'name': self.utils.format_name(name),
#                                         'url' : modelurl,
#                                         'board': board,
#                                         'product': product_data}
#                                 
                                
                                data_p = self.common.parse_item(product)    
                                data_t = {
                                        'name': self.utils.format_name(name),
                                        'url'  :   modelurl,
                                        'board':   board,
                                        'refurl':  modelurl
                                        }
        
                                data = dict( data_t, **data_p )                                          
                                yield data

                    self.log('parsed url %s' % url)      
                    self.dbUtils.put_db_url(url) 
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
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-s', type=int, default = 1)
    parser.add_argument('-e', type=int, default = 62)
    parser.add_argument('-f', type=str, default = 'Erocurves\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    parser.add_argument('-t', type=int, default=  cpu_count() - 1) 
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.erocurves.com/model-archives/?tpage={page}', args.s, args.e, args.f, args.t)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
