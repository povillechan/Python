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

        url  = urljoin('https://www.redtube.com/', item('span.video_thumb_wrap a').attr('href'))
        name = item('div.video_title a').text()
                                           
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
     
        html = self.webParser.utils.get_page(url, headers={'Referer':'https://www.redtube.com'})        
        if html:
            mediaDefinition = re.search('mediaDefinition:.*?\[(.*?)\]', html, re.S)
            if mediaDefinition:
                video_str = mediaDefinition.group(1).replace('\\', '')
                video_url = re.findall('\"(https:.*?)\"', video_str, re.S)
                if video_url:    
                    data_detail = {
                        'videos': {
                            'name'  : item.get('brief').get('name'),
                            'url'   : item.get('brief').get('url'),
                            'video' : video_url[0]
                            }
                        }
                    data = deepcopy(item)
                    data['detail'] = data_detail                 

        return data      
    

    def get_sub_dir_name(self,data):
        sub_dir_name = ""
        return sub_dir_name
    
    def process_data(self, data):
#         print(data)
        result = True
        sub_dir_name = self.get_sub_dir_name(data)
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # videos
        videos = data.get('detail').get('videos')
        if videos:               
            video = videos.get('video')
            if video:
                result &=  self.webParser.utils.download_file(video,
                                    '%s\\videos\\%s' % (sub_dir_name, videos.get('name')),
                                    headers={'Referer':videos.get('url')}        
                                     )      
                
        return result  
    
class CWebParserSite(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url,savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('RedTube')
        
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
                    break
                                
                if self.dbUtils.get_db_url(url):
                    continue                 
               
                while True:
                    html = self.utils.get_page(url)     
                    if html:
                        if self.dbUtils.get_db_url(url):
                            pass
                        else:
                            a = pq(html)     
                            #items
                            items = a('#block_browse li>div')
                            parse_succeed = None
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
                 
                            if parse_succeed and items.items()>0:
                                self.log('parsed url %s' % url)     
                                self.dbUtils.put_db_url(url)  
                                
                        next_url = a('#wp_navNext').attr('href')
                        if next_url:
                            url = urljoin('https://www.redtube.com/', next_url)
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
        
        
    def urls_genarator(self):
        html = self.utils.get_page(self.url)     
        if html:
            a = pq(html)
            categorys = a('#categories_list_block li div.category_item_info a')
            for category in categorys.items():
                yield urljoin("https://www.redtube.com", category.attr('href'))
        yield None                      
                    
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default=  'RedTube\\{filePath}')
    parser.add_argument('-p', type=int, default=  '0')
    args = parser.parse_args()
    print(args)

    for url in range(ord("A"),ord("Z")+1):
#         print(chr(url))
        job = CWebParserSite("https://www.redtube.com/categories", args.f, args.p)
        job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
