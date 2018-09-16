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

        board =  item('img').attr('src')
        product_url  =  item('a').attr('href')
        product_name = item('a').attr('title')
        
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            data = { 
                'board': board,
                'url'  : product_url,
                'name' : self.webParser.utils.format_name(product_name)        
            }   
        else:
            html = self.webParser.utils.get_page(product_url, headers={"Accept-Encoding":"",})   
            if html:
                b = pq(html)                          
    
                video = None
                video_item = b('video')

                if video_item:
                    video = video_item.attr('src') 
                                   
                stills = []            
                previews = b('div.ngg-gallery-thumbnail')
                for preview in previews.items():
                    stills.append([ preview('a').attr('href'), preview('img').attr('src')])
                       
                data = {    
                    'board'   : poster,
                    'url'     : product_url,
                    'name'    : self.webParser.utils.format_name(product_name),
                    'stills'  :  stills,      
                    'video'   :  video      
                   }    
                
        return data 
    
    def parse_detail_fr_brief(self, item):
        data = None     
        url = item.get('product').get('url')        
        html = self.webParser.utils.get_page(url, headers={"Accept-Encoding":"",})        
        
        if html:
            b = pq(html)                          

            video = None
            video_item = b('video')
            if video_item:
                video = video_item.attr('src') 
                                   
            stills = []            
            previews = b('div.ngg-gallery-thumbnail')
            for preview in previews.items():
                stills.append([ preview('a').attr('href'), preview('img').attr('src')])
                   
            product_data = {    
                'board': item.get('product').get('board'),
                'url'  : item.get('product').get('url'),
                'name' : self.webParser.utils.format_name(item.get('product').get('name')),
                'stills'  :  stills,      
                'video'   :  video      
               }    
            
            data = {
                'name': item.get('name'),
                'url' : item.get('url'),
                'product': product_data
                }
        return data         

    def process_data(self, data):
#         print(data)
        result = True
        if data.get('video'):
            sub_dir_name = "%s\\films\\%s %s" %(data.get('name'), data.get('name'), data.get('product').get('name'))
        else:
            sub_dir_name = "%s\\galleries\\%s %s" %(data.get('name'), data.get('name'), data.get('product').get('name'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\..\\info.json', 'w') as f:    
            json.dump(data, f)
            
        board = data.get('product').get('board')
        result &=  self.webParser.utils.download_file(board,
                                '%s\\%s' % (sub_dir_name, data.get('product').get('name')),
                                headers={'Referer':data.get('product').get('url')}        
                                 )                 
        
        if data.get('product').get('video'):
            result &= self.webParser.utils.download_file(data.get('product').get('video'),
                            '%s\\%s' % (sub_dir_name, data.get('product').get('name')),
                            headers={'Referer':data.get('product').get('url')}        
                             )             
     
        stills = data.get('product').get('stills')
        for i, val in enumerate(stills, start=1): 
            for subVal in val:
                if subVal:
                    result &= self.webParser.utils.download_file(subVal,
                                     '%s\\%s' % (sub_dir_name, str(i)),
                                     headers={'Referer':data.get('product').get('url')}     
                             )   
                    break
        
        return result      
        
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

                        html = self.utils.get_page(modelurl, headers={"Accept-Encoding":"",})        
                        if html:
                            b = pq(html)                
                            products = b('li.box-shadow')
                            for product in products.items():
                                product_data = self.common.parse_item(product)    
                                data = {'name': self.utils.format_name(name),
                                        'url' : modelurl,
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
    parser.add_argument('-f', type=str, default=  '18OnlyGirls\\{filePath}')
    parser.add_argument('-p', type=int, default=  '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.18onlygirlsblog.com/models-list/', args.f, args.p)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
