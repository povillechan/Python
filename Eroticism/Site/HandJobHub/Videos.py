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
        url  = item('a').attr('href')
        name = item('a').attr('title')
        board = item('a img').attr('src')
                                           
        data_brief = {
            'url'  : url,
            'name' : self.webParser.utils.format_name(name),
            'board': board
        } 
        
        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data
        else:                    
            return self.parse_detail_fr_brief(data)     
    
    def parse_detail_fr_brief(self, item):    
        data = None     
        url = item.get('brief').get('url')   
     
        html = self.webParser.utils.get_page(url)        
        if html:
            b = pq(html)
            
            video = None
            video_src = b('video source')
            if video_src:
                video = video_src.attr('src')
                
                stills = []
                prefix = re.search('(https://.*?)-\d.jpg', item.get('brief').get('board'))
                
                if prefix:
                    for i in range(1,10):
                        stills.append("%s-%s.jpg"%(prefix.group(1), i))
                    
                data_detail = {
                    'videos': {
                        'name'  : item.get('brief').get('name'),
                        'url'   : item.get('brief').get('url'),
                        'video' : video,
                        'stills': stills
                        }
                    }
                                
            else:       
                previews = b('#galleryImages div.gallery-item-col a')            
                stills = []
                for previews in previews.item():
                    stills.append(previews.attr('href'))
    
                data_detail = {
                    'galleries': {
                        'name'  : item.get('brief').get('name'),
                        'url'   : item.get('brief').get('url'),
                        'stills': stills
                        }
                    }
        data = deepcopy(item)
        data['detail'] = data_detail                 

        return data      
    
    def get_sub_dir_name(self,data):
        sub_dir_name = ""  
        return sub_dir_name
    
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('HandJobHub')
        
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
                    
                if self.dbUtils.get_db_url(url):
                    continue
                
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)     
                    #items
                    items = a('main.main-col div.row div.item-inner-col')
                    parse_succeed = True
                    for item in items.items():
                        try:
                            data_p = self.common.parse_item(item)    
                            data_t = {
                                'name'  : data_p.get('brief').get('name'),
                                'url'   : data_p.get('brief').get('url'),
                                'refurl': url
                                }
    
                            data = dict( data_t, **data_p )                                          
                            yield data
                        except:
                            parse_succeed = False
                            continue                 
                    if parse_succeed:
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
    parser.add_argument('-e', type=int, default = 409)
    parser.add_argument('-f', type=str, default = 'HandJobHub\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://handjobhub.com/top-rated/page{page}.html', args.s, args.e, args.f, args.p)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
