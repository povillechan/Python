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
from multiprocessing import cpu_count

class CWebParserSiteCommon(object):
    def __init__(self, webParser):
        self.webParser = webParser
#    
    def parse_item(self, item):   
        data = None   
        url   = item.attr('href')
        name  = item.attr('title')

        data_brief = {
            'name' : self.webParser.utils.format_name(name), 
            'url'  : url    
            } 
        
        data = {'brief': data_brief}
        
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data
        else:                    
            return self.parse_detail_fr_brief(data) 
    
    def parse_detail_fr_brief(self, item):
        data = None     
        url = item.get('brief').get('url')        
        html = self.webParser.utils.get_page_by_chrome(url, 'video', headless=False)       
        
        if html:
            b = BeautifulSoup(html, 'lxml')                         
             
            video  = b.select_one('video.fp-engine').get('src')  

            board = None
            board_url = re.search('preview_url: \'(https.*?)\'', html, re.S)
            if board_url:
                board = board_url.group(1)

            data_detail = {
                'videos': {
                    'name' : item.get('brief').get('name'),
                    'url'  : url,
                    'board': board,
                    'video': video,
                    'stills':[],
                    }
                }
                                                
            data = deepcopy(item)
            data['detail'] = data_detail
        return data       

    def process_data(self, data):
        result = True
        sub_dir_name = "" 
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
#         with open(dir_name + '\\info.json', 'w') as f:    
#             json.dump(data, f)
           
        board = data.get('detail').get('videos').get('board')
        if board:
            result &=  self.webParser.utils.download_file(board,
                                data.get('detail').get('videos').get('name'),
                                headers={'Referer':data.get('detail').get('videos').get('url')}
                                ) 
             
        video = data.get('detail').get('videos').get('video')
        if video:
            result &=  self.webParser.utils.download_file(video,
                                    data.get('detail').get('videos').get('name'),
                                    fileType='mp4',
                                    headers={'Referer':data.get('detail').get('videos').get('url')}
                                 ) 
        return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly, threadNum):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Porn7')
        self.thread_num = threadNum
#         if self.parseOnly == CParseType.Parse_Entire or self.parseOnly == CParseType.Parse_Detail:
#             self.thread_num = 1
        
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
                    items = a('#list_videos_common_videos_list_items > div > a')
                    
                    for item in items.items():
                        data_p = self.common.parse_item(item)    
                        data_t = {
                            'name'  : data_p.get('brief').get('name'),
                            'url'   : data_p.get('brief').get('url'),
                            'refurl': url
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
    parser.add_argument('-s', type=int, default = 0)
    parser.add_argument('-e', type=int, default = 222)
    parser.add_argument('-f', type=str, default = 'Porn7\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    parser.add_argument('-t', type=int, default=  cpu_count() - 1) 
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.porn7.xxx/rated/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=rating&from={page}', args.s, args.e, args.f, args.p, args.t)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
