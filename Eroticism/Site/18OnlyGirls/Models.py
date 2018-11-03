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
 
    def process_data(self, data):
        result = True
        sub_dir_name = self.get_sub_dir_name(data)
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # board    
        board = data.get('board')
        if board:
            result &=  self.webParser.utils.download_file(board,
                                    '%s\\%s' % (sub_dir_name, data.get('name')),
                                    headers={'Referer':data.get('url')}        
                                     )                 
        
        # galleries
        galleries = data.get('detail').get('galleries')
        if galleries:            
            board = galleries.get('board')
            if board:
                result &=  self.webParser.utils.download_file(board,
                                    '%s\\galleries\\%s\\%s' % (sub_dir_name, galleries.get('name'), galleries.get('name')),
                                    headers={'Referer':galleries.get('url')}        
                                     )                 
        
            
            stills = galleries.get('stills') 
            if stills:
                for i, subVal in enumerate(stills, start=1):            
                    if subVal:
                        result &= self.webParser.utils.download_file(subVal,
                                    '%s\\galleries\\%s\\%s' % (sub_dir_name, galleries.get('name'), str(i)),
                                    headers={'Referer':galleries.get('url')}     
                             )   
         
        # videos
        videos = data.get('detail').get('videos')
        if videos:            
            board = videos.get('board')
            if board:
                result &=  self.webParser.utils.download_file(board,
                                    '%s\\videos\\%s\\%s' % (sub_dir_name, videos.get('name'), videos.get('name')),
                                    headers={'Referer':videos.get('url')}        
                                     )                 
        
            
            stills = videos.get('stills') 
            if stills:
                for i, subVal in enumerate(stills, start=1):            
                    if subVal:
                        result &= self.webParser.utils.download_file(subVal,
                                    '%s\\videos\\%s\\%s' % (sub_dir_name, videos.get('name'), str(i)),
                                    headers={'Referer':videos.get('url')}     
                             )                          
                
            video = videos.get('video')
            if video:
                self.webParser.utils.download_file(video,
                                    '%s\\videos\\%s\\%s' % (sub_dir_name, videos.get('name'), videos.get('name')),
                                    headers={'Referer':videos.get('url')}        
                                     )      
                
        return result  


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

                        if self.dbUtils.get_db_url(modelurl):
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
                                        'url' :   modelurl,
                                        'refurl': modelurl
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
                continue    
        
        yield None  
                
                    
def job_start():
    para_args = {
        'savePath': '18OnlyGirls\\{filePath}',
        'url': 'https://www.18onlygirlsblog.com/models-list/',
        'database': '18OnlyGirls'
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':   
    job_start() 
