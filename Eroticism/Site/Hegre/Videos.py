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
        
        name  = item('a').attr('title')
        url   = urljoin('http://www.hegre.com/',item('a').attr('href'))
                                           
        data_brief = {
            'url'     : url,
            'name'    : self.webParser.utils.format_name(name),
        } 
        
        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data
        else:                    
            return self.parse_detail_fr_brief(data)     
    
    def parse_detail_fr_brief(self, item):    
        data = None     
        url  = item.get('brief').get('url')   
      
        html = self.webParser.utils.get_page(url)   
        if html:
            b = pq(html)                          
          
            board = b('meta[name="twitter:image"]').attr('content')
            
            stills = []                
            previews = b('.video-stills .board_image a')
            for preview in previews.items():
                stills.append(preview.attr('href'))
                
            video = b('.resolution.trailer.top-resolution a').attr('href')

            data_detail = {
                'videos': {
                    'name'  : item.get('brief').get('name'),
                    'url'   : url,
                    'board' : board,
                    'video' : video,
                    'stills': stills
                    }
                }
            data = deepcopy(item)
            data['detail'] = data_detail   
                   

        return data      
        
# class CWebParserSite(CWebParserMultiUrl):    
#     def __init__(self, url, start, end, savePath, parseOnly):
#         super().__init__(url, start, end, savePath)
#         self.utils = CWebSpiderUtils(self.savePath)  
#         self.parseOnly = CParseType(parseOnly)  
#         self.common = CWebParserSiteCommon(self)    
#         self.dbUtils = CWebDataDbUtis('Hegre22')
#         
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Hegre')
                
    '''
    parse_page
    
    @author: chenzf
    ''' 
    def parse_page(self):
        urlsGen = self.urls_genarator()
        while True: 
            try:
                url = next(urlsGen)
                if url is None:
                    yield None
                
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html, parser='html')   
                    #items
                    items = a('a.artwork')                   
                    for item in items.items():                        
                        modelurl = urljoin('http://www.hegre.com/',  item.attr('href').strip())
                        board = item('img').attr('src')
                        name = item.attr('title')                        
                                            
                        if self.dbUtils.get_db_url(modelurl):
                            continue
                        
                        bFarseSucceed = True
                        html2 = self.utils.get_page(modelurl)   
                        if html2:
                            b = pq(html2, parser='html')       
                            item_models = b('#films-wrapper div.item')
                            for item_model in item_models.items():    
                                try:                                                            
                                    data_p = self.common.parse_item(item_model)    
                                    data_t = {
                                        'name'  : self.utils.format_name(name),
                                        'url'   : modelurl,
                                        'board' : board,
                                        'refurl': modelurl
                                        }
            
                                    data = dict( data_t, **data_p )                                          
                                    yield data    
                                except:
                                    bFarseSucceed = False
                                    continue   
                            b = pq(html2, parser='html')       
                            item_models = b('#massages-wrapper div.item')
                            for item_model in item_models.items():    
                                try:                                                            
                                    data_p = self.common.parse_item(item_model)    
                                    data_t = {
                                        'name'  : self.utils.format_name(name),
                                        'url'   : modelurl,
                                        'board' : board,
                                        'refurl': modelurl
                                        }
            
                                    data = dict( data_t, **data_p )                                          
                                    yield data    
                                except:
                                    bFarseSucceed = False
                                    continue  
                                                 
                            self.log('parsed url %s' % modelurl) 
                            if bFarseSucceed:    
                                self.dbUtils.put_db_url(modelurl)       
                    
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
    parser.add_argument('-f', type=str, default = 'Hegre\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.hegre.com/models', args.f, args.p)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
