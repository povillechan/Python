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

        url  = urljoin('https://www.hqbabes.com/', item('a:nth-child(2)').attr('href'))
        name = item('b span').text()
                                           
        data_brief = {
            'url'  : url,
            'name' : self.webParser.utils.format_name(name),
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
   
            previews = b('ul.set.gallery li.item.i a')            
            stills = []
            for preview in previews.items():
                stills.append('https:' + preview.attr('href'))

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
    
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly, threadNum):
        super().__init__(url,savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('HQBabes')
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
               
                while True:
                    html = self.utils.get_page(url)     
                    if html:
                        if self.dbUtils.get_db_url(url):
                            pass
                        else:
                            a = pq(html)     
                            #items
                            items = a('ul.babes_main li')
                            parse_succeed = True
                            for item in items.items():
                                try:                            
                                    name      = item('b a').text()
                                    board     = 'https:' + item('a img').attr('lsrc') + '.jpg'
                                    model_url = urljoin('https://www.hqbabes.com/', item('b a').attr('href'))
                                     
                                    html2 = self.utils.get_page(model_url)
                                    if html2:
                                        b = pq(html2)
                                        modelitems = b('ul.set.babe li')
                                        for modelitem in modelitems.items():
                                            try:
                                                data_p = self.common.parse_item(modelitem)    
                                                data_t = {
                                                    'name'  : self.utils.format_name(name),
                                                    'url'   : model_url,
                                                    'board' : board,
                                                    'refurl': url
                                                    }
                         
                                                data = dict( data_t, **data_p )                                          
                                                yield data
                                            except:
                                                parse_succeed = False
                                                continue
                                except:
                                    parse_succeed = False
                                    continue                 
                            if parse_succeed:
                                self.log('parsed url %s' % url)     
                                self.dbUtils.put_db_url(url)  
                                
                        next_url = a('#pages li a[count="Next Page"]')
                        if next_url:
                            url = urljoin('https://www.hqbabes.com/', next_url.attr('href'))
                            self.log('request %s' %url)  
                        else:
                            break
                    else:
                        self.log('request %s error' %url)      
                        continue   
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log( 'error in parse url %s' % url)         
                continue                   
        
        yield None                     
                    
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default=  'HQBabes\\{filePath}')
    parser.add_argument('-t', type=int, default=  cpu_count() - 1) 
    parser.add_argument('-p', type=int, default=  '0')
    args = parser.parse_args()
    print(args)

    for url in range(ord("A"),ord("Z")+1):
#         print(chr(url))
        job = CWebParserSite("https://www.hqbabes.com/babes/%s/"%chr(url), args.f, args.p, args.t)
        job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 