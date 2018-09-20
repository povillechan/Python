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
        url =  item('a').attr('href')
        result = re.search('.*?(\?\d+x\d+x\d+)', item('a').attr('href'))
        if result:
            url = url.replace(result.group(1),'')        
        
        url   =  urljoin('http://www.hotxart.com/', url)   
        name  =  item('img').attr('alt')          
          
        data = { 
            'url'  : url,
            'name' : self.webParser.utils.format_name(name),   
            'board': board    
        }   
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data 
        else:                    
            return self.parse_detail_fr_brief(data)   
    
    def parse_detail_fr_brief(self, item):
        data = None     
        url = item.get('url')        
        html = self.webParser.utils.get_page(url, headers={'Referer':'http://www.hotxart.com/'})        
        
        if html:
            b = pq(html)                          

            photos = b('body table:nth-child(2) table td>a')
            stills = []
            for photo in photos.items():
                detail_url = urljoin('http://www.hotxart.com/', photo.attr('href')) 
                small = photo('img').attr('src')
                detail_html = self.webParser.utils.get_page(detail_url)   
                large = None
                if detail_html:
                    c = pq(detail_html)                        
                    large = c('span.galprov img').attr('src')
                    
                stills.append([large, small])
            
            if len(stills) > 0:
                data = {    
                'url'  : item.get('url'),
                'name' : item.get('name'),   
                'board': item.get('board'),
                'stills' :  stills
                } 
        return data         

    def process_data(self, data):
#         print(data)
        result = True
        sub_dir_name = "%s" %(data.get('name'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)
            
        board = data.get('board')
        result &=  self.webParser.utils.download_file(board,
                                '%s\\%s' % (sub_dir_name, data.get('name')),
                                headers={'Referer':'http://www.hotxart.com/'}
                                 )                 
        
   
     
        stills = data.get('stills')
        for i, val in enumerate(stills, start=1): 
            for subVal in val:
                if subVal:
                    result &= self.webParser.utils.download_file(subVal,
                                     '%s\\%s' % (sub_dir_name, str(i)),
                                     headers={'Referer':'http://www.hotxart.com/'}
                             )   
                    break
        
        return result      
        
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('HotXArt')
        
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
                
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)   
                    #items
                    items = a('ul.picmain li')
                    for item in items.items():
                        data = self.common.parse_item(item)                            
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
    parser.add_argument('-f', type=str, default=  'HotXArt\\{filePath}')
    parser.add_argument('-p', type=int, default=  '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('http://www.hotxart.com/', args.f, args.p)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
