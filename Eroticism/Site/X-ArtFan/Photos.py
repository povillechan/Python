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

        url = item('a[rel=bookmark]').attr('href')
        name = item('a[rel=bookmark]').text()
        result = re.findall('[a-zA-z]+://[^\s]*', str(item('img.attachment-bimber-grid-standard').attr('srcset')))
    
        data = { 
            'name' : self.webParser.utils.format_name(name),   
            'url'  : url,    
            'board': [result[1],result[0]]
            }   
        
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data 
        else:                    
            return self.parse_detail_fr_brief(data) 
    
    def parse_detail_fr_brief(self, item):
        data = None     
        url = item.get('url')    
        
        html = self.webParser.utils.get_page(url)   
        if html:
            b = pq(html)                          

            video = None
            player = b('div.flowplayer')
            if player:
                src = json.loads(player.attr('data-item')).get('sources')[0].get('src')     
                board = re.search('background-image: url\((.*?)\)', player.attr('style')).group(1)
                video = {
                   'src':src,
                   'board':board
                   }

            previews = b('div.tiled-gallery-item a')
            stills = []
            for preview in previews.items():
                stills.append(
                   [preview('img').attr('data-large-file'),
                    preview('img').attr('data-medium-file'),
                    preview('img').attr('src')                  
                   ])                 
            
            modelName = None
            for model in b('span.entry-categories-inner span').items():
                modelName = model.text()
                break
            data = {           
               'name' : item.get('name'), 
               'modelName':  self.webParser.utils.format_name(modelName),
               'url'  : url,    
               'board': item.get('board'),
               'video': video,
               'stills':stills
               }  
                
        return data        

    def process_data(self, data):
        result = True
        sub_dir_name = "%s" %(data.get('modelName'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)
            
        boards = data.get('board')
        for board in boards:
            result &=  self.webParser.utils.download_file(board,
                                '%s\\%s\\%s' % (sub_dir_name, data.get('name'), data.get('name')),
                                 )  
            break               
   
     
        stills = data.get('stills')
        for i, val in enumerate(stills, start=1): 
            for subVal in val:
                if subVal:
                    result &= self.webParser.utils.download_file(subVal,
                                     '%s\\%s\\%s' % (sub_dir_name, data.get('name'), str(i))
                             )   
                    break
        
        video = data.get('video')
        if video:  
            result &= self.webParser.utils.download_file(video.get('src'),
                                     '%s\\%s\\%s' % (sub_dir_name, data.get('name'), data.get('name'))
                                     )   
                                      
            result &= self.webParser.utils.download_file(video.get('board'),
                                     '%s\\%s\\%s' % (sub_dir_name, data.get('name'), 'video_preview')
                                     )     
        return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('X-ArtFan')
        
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
                    items = a('li.g1-collection-item')
                    
                    for item in items.items():
                        data = self.common.parse_item(item)                                                 
                        yield data
                    
                    self.log('parsed url %s' % url)     
                    self.dbUtils.put_db_url(url) 
                else:
                    self.log('request %s error' %url)         
            except:
                self.log( 'error in parse url %s' % url)         
                  
        
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
    parser.add_argument('-e', type=int, default = 52)
    parser.add_argument('-f', type=str, default = 'X-ArtFan\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://xartfan.com/page/{page}', args.s, args.e, args.f, args.p)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
