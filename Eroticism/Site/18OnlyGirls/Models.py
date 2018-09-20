# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json, collections
import argparse
from copy import deepcopy
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParser import CParseType,CWebParser,CWebParserMultiUrl,CWebParserSingleUrl
from Common.CWebDataDbUtis import CWebDataDbUtis
from Common.CWebSpiderUtils import CWebSpiderUtils
from Common.CWebParserSite import CWebParserSite
from copy import deepcopy
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import vthread
import pymongo
from copy import deepcopy

class CWebParserSiteCommon(CWebParserSite):
    def __init__(self, webParser):
        super().__init__(webParser)
#    
    def parse_item(self, item):   
        data = None   

        board =  item('img').attr('src')
        product_url  =  item('a').attr('href')
        product_name = item('a').attr('title')
        data_brief = {
                'board': board,
                'url'  : product_url,
                'name' : self.webParser.utils.format_name(product_name)        
            } 
        
        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data
        else:                    
            return self.parse_detail_fr_brief(data) 
    
    def parse_detail_fr_brief(self, item):
        data = None     
        url = item.get('brief').get('url')        
        html = self.webParser.utils.get_page(url, headers={"Accept-Encoding":"",})        
        
        if html:
            b = pq(html)                          

            video = None
            video_item = b('video source')
            if video_item:
                video = video_item.attr('src') 
                                   
            stills = []            
            previews = b('div.ngg-gallery-thumbnail')
            for preview in previews.items():
                stills.append(preview('a').attr('href'))
                   
#             product_data = {    
#                 'board': item.get('product').get('board'),
#                 'url'  : item.get('product').get('url'),
#                 'name' : self.webParser.utils.format_name(item.get('product').get('name')),
#                 'stills'  :  stills,      
#                 'video'   :  video      
#                }    
#             
#             data = {
#                 'name': item.get('name'),
#                 'url' : item.get('url'),
#                 'product': product_data
#                 }
            data_detail = None
            if video:
                data_detail = {
                    'videos': {
                        'name' : self.webParser.utils.format_name(item.get('brief').get('name')),
                        'url'  : item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'video': video,
                        'stills':stills,
                        }
                    }
            else:
                data_detail = {
                    'galleries': {
                        'name' : self.webParser.utils.format_name(item.get('brief').get('name')),
                        'url'  : item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'stills':stills,
                        }
                    }  
                                                
            data = deepcopy(item)
            data['detail'] = data_detail
        return data        
 
#     def get_sub_dir_name(self,data):
#         sub_dir_name = "%s" %(data.get('name'))        
#         return sub_dir_name
        
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url,savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('18OnlyGirls')
        
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
                    items = a('ul.links li')
                    
                    for item in items.items():
                        modelurl = item('a').attr('href')
                        name = item('a').attr('title')

                        if self.dbUtils.get_db_url(url):
                            continue
                        
                        html = self.utils.get_page(modelurl, headers={"Accept-Encoding":"",})        
                        if html:
                            b = pq(html)                
                            products = b('li.box-shadow')
                            try:
                                for product in products.items():
                                    data_p = self.common.parse_item(product)    
                                    data_t = {
                                        'name': self.utils.format_name(name),
                                        'url' : modelurl
                                        }
        
                                    data = dict( data_t, **data_p )                                          
                                    yield data
                            except:
                                continue
                        
                            self.dbUtils.put_db_url(modelurl) 
                    
                    self.log('parsed url %s' % url)      
                else:
                    self.log('request %s error' %url)         
            except:
                self.log( 'error in parse url %s' % url)         
                yield None    
        
        yield None  
                
                    
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default=  '18OnlyGirls\\{filePath}')
    parser.add_argument('-p', type=int, default=  '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.18onlygirlsblog.com/models-list/', args.f, args.p)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
