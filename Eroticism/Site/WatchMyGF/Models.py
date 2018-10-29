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
        url = item('a').attr('href')
        name = item('a').attr('title')
        still = item('img').attr('src')
        stills = []
        result = re.search('(https.*?/)\d.jpg',still, re.S).group(1)

        for i in range(1,6):
            stills.append(
                result + str(i)+'.jpg'                          
                )
#             
#         data = { 
#             'productName' : self.webParser.utils.format_name(name),   
#             'productUrl'  : url,
#             'stills'      : stills
#             }   
#         
#         if self.webParser.parseOnly == CParseType.Parse_Brief:                             
#             return data 
#         else:                    
#             return self.parse_detail_fr_brief(data) 
#         
        data_brief = { 
            'name' : self.webParser.utils.format_name(name),      
            'url'  : url,    
            'stills': stills,
            }   
        
        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data 
        else:                    
            return self.parse_detail_fr_brief(data) 
        
    
    def parse_detail_fr_brief(self, item):
        data = None
        
        url = item.get('brief').get('url')
        html = self.webParser.utils.get_page_by_chrome(url, 'video.fp-engine', headless=False)     
        if html:
            b = BeautifulSoup(html, 'lxml')                         
             
            video  = b.select_one('video.fp-engine').get('src')    
            
            data_detail = {
                    'videos': {
                        'name' : item.get('brief').get('name'),
                        'url'  : item.get('brief').get('url'),
                        'video': video,
                        'stills':item.get('brief').get('stills'),
                        }
                    }
                                       
            data = deepcopy(item)
            data['detail'] = data_detail
        return data          
# 
#     def process_data(self, data):
#         result = True
#         sub_dir_name = "%s\\%s" %(data.get('model'), data.get('productName'))
#        
#         dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
#         if not os.path.exists(dir_name):
#             os.makedirs(dir_name)
#         
#         with open(dir_name + '\\info.json', 'w') as f:    
#             json.dump(data, f)
#             
#         stills = data.get('stills')
#         for i, subVal in enumerate(stills, start=1):
#             if subVal:
#                 result &= self.webParser.utils.download_file(subVal,
#                                  '%s\\%s' % (sub_dir_name, str(i)),
#                                 headers={'Referer':data.get('productUrl')}
#                          )   
# 
#                 
#         video = data.get('video')
#         if video:
#             result &=  self.webParser.utils.download_file(video,
#                                 '%s\\%s' % (sub_dir_name, data.get('productName')),
#                                 headers={'Referer':data.get('productUrl')}
#                                  ) 
#  
#         return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly, threadNum):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('WatchMyGF')
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
                    items = a('span.model_items')
                    
                    for item in items.items():
                        modelurlText = item.attr('onclick')
                        modelurl = re.search('\'(http.*?)\'', modelurlText, re.S).group(1)
                        model = item.attr('title')

                        html2 = self.utils.get_page(modelurl)      
                        if html2:
                            b = pq(html2)
                            items_model = b('div.content div.item')
                            for item_model in items_model.items():
#                                 data = self.common.parse_item(item_model) 
#                                 if data:
#                                     data['url']   = modelurl      
#                                     data['model'] = model
#                                       
#                                 yield data
                                data_p = self.common.parse_item(item_model)    
                                data_t = {
                                    'name' :  model,
                                    'url'  :  modelurl,
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
    parser.add_argument('-s', type=int, default = 1)
    parser.add_argument('-e', type=int, default = 34)
    parser.add_argument('-f', type=str, default = 'WatchMyGF\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    parser.add_argument('-t', type=int, default=  cpu_count() - 1) 
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://watch-my-gf.com/girls.html?mode=async&function=get_block&block_id=list_models_models_list&section=&sort_by=avg_videos_popularity&from={page}', args.s, args.e, args.f, args.p, args.t)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
