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

        modelurl  = urljoin('https://au.fleshlight.com/',item('a.permacover').attr('href'))
        name      = item('a.permacover .v-bottom h3').text()
        board_str = re.search('url\(\'(.*?)\'', item('.grid-image').attr('style'))
        board     = urljoin('https://', board_str.group(1))

        data_brief = {
                'board': board,
                'url'  : modelurl,
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

            stills = []            
            
            meta_imgs = b('meta[property="og:image"]')
            for meta in meta_imgs.items():
                stills.append(meta.attr('content')) 
                    
            board_str = re.search('url\(\'(.*?)\'', b('.main-product-container--pornstar').attr('style'))
            if board_str and len(board_str.group(1)) > 0:
                board     = urljoin('https://', board_str.group(1)) 
                stills.append(board) 
             
#             previews = b('div.owl-stage .owl-item .image')
#             for preview in previews.items():
#                 board_str = re.search('url\(\'(.*?)\'', item('.main-product-container--pornstar').attr('style'))
#                 board     = urljoin('https://', board_str.group(1)) 
#                 stills.append(board) 
#             
            if b('#combos'):
                board_str = re.search('url\(\'(.*?)\'', b('#combos').attr('style'))
                if board_str and len(board_str.group(1)) > 0:
                    board     = urljoin('https://', board_str.group(1)) 
                    stills.append(board) 
            
            if b('.girl-stats .girl-stats-image span'):
                board_str = re.search('url\(\'(.*?)\'', b('.girl-stats .girl-stats-image span').attr('style'))
                if board_str and len(board_str.group(1)) > 0:
                    board     = urljoin('https://', board_str.group(1)) 
                    stills.append(board) 
            
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

                
    def get_sub_dir_name(self,data):
        sub_dir_name = ""        
        return sub_dir_name
            
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly, threadNum):
        super().__init__(url,savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('FleshlightGirls')
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
                    items = a('.products .contain .grid .col-sm-12')
                    parse_succeed = True
                    for item in items.items():
                        try:
                            data_p = self.common.parse_item(item)    
                            data_t = {
                                'name' :  data_p.get('brief').get('name'),
                                'url'  :  data_p.get('brief').get('url'),
                                'board':  data_p.get('brief').get('board'),
                                'refurl': url
                                }
        
                            data = dict( data_t, **data_p )                                          
                            yield data
                        except:
                            parse_succeed = False
                            continue      
                    if parse_succeed:
                        self.dbUtils.put_db_url(url) 
                else:
                    self.log( 'html none in parse url %s' % url)         
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log( 'error in parse url %s' % url)         
                continue    
        
        yield None  
                        
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default=  'FleshlightGirls\\{filePath}')
    parser.add_argument('-p', type=int, default=  '0')
    parser.add_argument('-t', type=int, default=  cpu_count() - 1) 
    args = parser.parse_args()
    print(args)
    job_list = [
        ('S', 'https://au.fleshlight.com/collections/fleshlight-girls/'),
        ('S', 'https://au.fleshlight.com/collections/legends'),
        ('S', 'https://au.fleshlight.com/collections/dorcel-girls'),
        ('S', 'https://au.fleshlight.com/collections/camstars')
        ]
          
    for job_item in job_list:
         job = CWebParserSite(job_item[1], args.f, args.p, args.t)
         job.call_process()   
    
if __name__ == '__main__':   
    Job_Start() 
