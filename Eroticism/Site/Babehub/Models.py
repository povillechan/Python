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

        url = item('a').attr('href')
        model = item('span').text().replace(item('span span').text(), '')
        board = item('img').attr('src')
        productName = item('a').attr('title')    
                         
        data_brief = { 
            'name' : self.webParser.utils.format_name(model),   
            'url'  : url,    
            'board': board,
            'productName': self.webParser.utils.format_name(productName),   
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

#             previews = b('ul.gallery-e li')
#             stills = []
#             for preview in previews.items():
#                 stills.append(
#                     [
#                     preview('a').attr('href'),
#                     preview('img').attr('src'),
#                     ])                 
# 
# 
#             data = { 
#                 'modelName' : item.get('modelName'),   
#                 'url'  : url,    
#                 'board': item.get('board'),
#                 'productName': item.get('productName'), 
#                 'stills': stills
#                 }  
            board = None   
            video = None
            video_item = b('video source')
            if video_item.items(0):
                video = video_item.attr('src') 
                board = b('video').attr('poster')
                                   
            stills = []            
            previews = b('ul.gallery-e li')
            for preview in previews.items():
                stills.append(preview('a').attr('href'))
                
#                 }
            data_detail = None
            if video:
                data_detail = {
                    'videos': {
                        'name' : self.webParser.utils.format_name(item.get('brief').get('productName')),
                        'url'  : item.get('brief').get('url'),
                        'board': board,
                        'video': video,
                        'stills':stills,
                        }
                    }
            else:
                data_detail = {
                    'galleries': {
                        'name' : self.webParser.utils.format_name(item.get('brief').get('productName')),
                        'url'  : item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'stills':stills,
                        }
                    }  
                                                
            data = deepcopy(item)
            data['detail'] = data_detail
        return data         

#     def process_data(self, data):
#         result = True
#         sub_dir_name = "%s\\galleries\\%s" %(data.get('modelName'), data.get('productName'))
#        
#         dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
#         if not os.path.exists(dir_name):
#             os.makedirs(dir_name)
#         
#         with open(dir_name + '\\info.json', 'w') as f:    
#             json.dump(data, f)
#             
#         board = data.get('board')
#         if board:
#             result &=  self.webParser.utils.download_file(board,
#                                 '%s\\%s' % (sub_dir_name, data.get('productName')),
#                                 headers={'Referer':'https://www.babehub.com/'}
#                                  )  
#      
#         stills = data.get('stills')
#         for i, val in enumerate(stills, start=1): 
#             for subVal in val:
#                 if subVal:
#                     result &= self.webParser.utils.download_file(subVal,
#                                      '%s\\%s' % (sub_dir_name, str(i)),
#                                      headers={'Referer':data.get('url')}
#                              )   
#                     break        
#  
#         return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('BabeHub')
        
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
                    items = a('ul.gallery-d li')
                    
                    for item in items.items():
                        data_p = self.common.parse_item(item)    
                        data_t = {
                            'name' :  data_p.get('brief').get('name'),
                            'url'  :  data_p.get('brief').get('url'),
                            'board':  data_p.get('brief').get('board'),
                            }

                        data = dict( data_t, **data_p )                                                                                
                        yield data
                    
                    self.log('parsed url %s' % url)     
                    self.dbUtils.put_db_url(url) 
                else:
                    self.log('request %s error' %url)         
            except:
                self.log( 'error in parse url %s' % url)         
                  
        
        yield None  
           
                    
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-s', type=int, default = 0)
    parser.add_argument('-e', type=int, default = 131)
    parser.add_argument('-f', type=str, default = 'BabeHub\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.babehub.com/page/{page}/', args.s, args.e, args.f, args.p)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
