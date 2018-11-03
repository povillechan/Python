# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json, collections

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParser import CParseType, CWebParser, CWebParserMultiUrl, CWebParserSingleUrl
from Common.CWebDataDbUtis import CWebDataDbUtis
from Common.CWebSpiderUtils import CWebSpiderUtils
from Common.CWebParserProcess import CWebParserProcess
from copy import deepcopy
from pyquery import PyQuery as pq
from urllib.parse import urljoin


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)
#    
    def parse_item(self, item):   
        data = None   
        product_name  =  item.attr('title')
        product_url   =  item.attr('href')
                           
        data_brief = { 
            'url'     :  product_url,
            'name'    :  self.webParser.utils.format_name(product_name),
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
            previews = b('div.masonry_thumbs div.item div.masonry_item > a')
            for preview in previews.items():
                stills.append(preview('a').attr('href'))                    
            
            data_detail = {
                'galleries': {
                    'name'  : item.get('brief').get('name'),
                    'url'   : product_url,
                    'stills':stills,
                    }
                } 
                
            data = deepcopy(item)
            data['detail'] = data_detail

        return data         


class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, **kwArgs):
        super().__init__(**kwArgs)
        self.utils = CWebSpiderUtils(self.savePath)
        self.common = CWebParserSiteCommon(self)
        self.dbUtils = CWebDataDbUtis(kwArgs.get('database'))
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
                    break
                                
                if self.dbUtils.get_db_url(url):
                    continue
                
                data_total = 1
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)   
                    data_total = a('button.js-load-more').attr('data-total')
                    if not data_total:
                        data_total = 1
                    
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
#                                     product_data = self.common.parse_item(item)    
#                                     data = {
#                                         'name':    self.utils.format_name(name),
#                                         'product': product_data}
#                                     
                                    data_p = self.common.parse_item(item)    
                                    data_t = {
                                            'name':    name,
                                            'url'  :   data_p.get('brief').get('url'),
                                            'refurl':  cate_url
                                            }
        
                                    data = dict( data_t, **data_p )                                          
                                    yield data
                                self.dbUtils.put_db_url(cate_url) 
                        except:
                            continue
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
        
                
def job_start():
    para_args = {
        'savePath': 'Faponix\\{filePath}',
        'url': 'https://www.faponix.com/categories/',
        'database': 'Faponix'
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':   
    job_start() 
