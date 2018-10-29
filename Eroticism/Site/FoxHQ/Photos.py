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
        url = item.attr('href')
        name = item('img').attr('alt')
                                           
        data_brief = {
            'url'  : url,
            'name' : self.webParser.utils.format_name(name) 
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
            video_src = b('center video')
            if video_src:
                video = urljoin(url,video_src.attr('src'))
                data_detail = {
                    'videos': {
                        'name'  : item.get('brief').get('name'),
                        'url'   : item.get('brief').get('url'),
                        'video' : video
                        }
                    }
                                
            else:                   
                stills = []
                for i in range(1,13):
                    stills.append(url + "%s.jpg"%i)
    
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
    def __init__(self, url, start, end, savePath, parseOnly, threadNum):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('FoxHQ')
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
                if url is None:
                    yield None
                    
                if self.dbUtils.get_db_url(url):
                    continue
                
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)     
                    #items
                    items = a('body > table:nth-child(2) center table:nth-child(1) > table:nth-child(1) td > a[target="_blank"]')
                    parse_succeed = True
                    for item in items.items():
                        try:
                            data_p = self.common.parse_item(item)    
                            data_t = {
                                'name'  : "FoxHQ",
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
    parser.add_argument('-e', type=int, default = 343)
    parser.add_argument('-f', type=str, default = 'FoxHQ\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    parser.add_argument('-t', type=int, default=  cpu_count() - 1) 
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('http://www.foxhq.com/showgals.php?page={page}', args.s, args.e, args.f, args.p, args.t)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
