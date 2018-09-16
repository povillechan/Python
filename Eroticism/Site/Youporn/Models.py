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
        url   = item.attr('href')
        name  = item.attr('title')
        board = item('img').attr('src')
        
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            data = { 
                'name' : self.webParser.utils.format_name(name), 
                'url'  : url
            }   
        else:
            html = self.webParser.utils.get_page_by_chrome(url, 'video', headless=False)   
            if html:
                b = BeautifulSoup(html, 'lxml')                         
                 
                video  = b.select_one('video.fp-engine').get('src')  

                board = None
                board_url = re.search('preview_url: \'(https.*?)\'', html, re.S)
                if board_url:
                    board = board_url.group(1)

                data = { 
                    'name' : self.webParser.utils.format_name(name), 
                    'url'  : url,
                    'board': board,
                    'video': video
                }      
                    
        return data 
    
    def parse_detail_fr_brief(self, item):
        data = deepcopy(item)
        
        url = item.get('url')
        html = self.webParser.utils.get_page_by_chrome(url, 'video', headless=False)    
        if html:
            b = BeautifulSoup(html, 'lxml')                         
             
            video  = b.select_one('video.fp-engine').get('src')  

            board = None
            board_url = re.search('preview_url: \'(https.*?)\'', html, re.S)
            if board_url:
                board = board_url.group(1)

            data['board'] = board
            data['video'] = video
                  
        return data         

    def process_data(self, data):
        result = True
        sub_dir_name = "" 
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
#         with open(dir_name + '\\info.json', 'w') as f:    
#             json.dump(data, f)
           
        board = data.get('board')
        if board:
            result &=  self.webParser.utils.download_file(board,
                                     data.get('name'),
                                headers={'Referer':data.get('url')}
                                 ) 
             
        video = data.get('video')
        if video:
            result &=  self.webParser.utils.download_file(video,
                                     data.get('name'),
                                headers={'Referer':data.get('url')}
                                 ) 
        return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Youporn')
        
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
                    items = a('div.fifteen-column > div > div.three-column > a')
                    
                    for item in items.items():
                        
                        model_url   = urljoin('https://www.youporn.com/', item.attr('href'))
                        model_name  = item('img').attr('alt')
                        model_board = item('img').attr('data-original')
                        
                        while True:
                            model_html = self.utils.get_page(model_url)     
                            if model_html:
                                b = pq(model_html)
                                print(model_html)
                                
                                video_items = b('div.video-box > a.video-box-image')
                                for video_item in video_items.items():
                                    data = self.common.parse_item(video_item)   
                                    
                                    data['model_url']   = model_url
                                    data['model_name']  = model_name       
                                    data['model_board'] = model_board                  
                                    yield data
                                
                                self.dbUtils.put_db_url(model_url)        
                            break
                    self.log('parsed url %s' % url)      
                    self.dbUtils.put_db_url(url) 
                else:
                    self.log('request %s error' %url)         
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
    
                
                    
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-s', type=int, default = 1)
    parser.add_argument('-e', type=int, default = 204)
    parser.add_argument('-f', type=str, default = 'Youporn\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.youporn.com/pornstars/?page={page}', args.s, args.e, args.f, args.p)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
