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
        url = item('a.title').attr('href')
        name = item('a.title').attr('title')
                        
        data = { 
            'productName' : self.webParser.utils.format_name(name),   
            'productUrl'  : url
            }   
            
        if self.webParser.parseOnly == CParseType.Parse_Brief:                             
            return data 
        else:                    
            return self.parse_detail_fr_brief(data) 
    
    def parse_detail_fr_brief(self, item):
        data = None
        
        url = item.get('productUrl')
        html = self.webParser.utils.get_page(url)   
        if html:
            b = pq(html)                          
            
            video  = []
            videos = b('#videoPlayer')
            for vid in videos('source').items():
                video.append(vid.attr('src'))
            
            stills = []
            poster = videos.attr('poster')
            result = re.search('https.*?(\d+b).jpg', poster, re.S)
            large  = poster.replace(result.group(1), '{index}b')
            small  = poster.replace(result.group(1), '{index}')

            for i in range(1,11):
                stills.append(
                    [
                    large.format(index=i),
                    small.format(index=i)                            
                    ])

            data = deepcopy(item)
            data['video']= video
            data['stills']= stills

        return data        

    def process_data(self, data):
        result = True
        sub_dir_name = "%s\\%s" %(data.get('model'), data.get('productName'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)
            
        board = data.get('board')
        if board:
            result &=  self.webParser.utils.download_file(board,
                                '%s\\..\\%s' % (sub_dir_name, data.get('model')),
                                headers={'Referer':data.get('url')}
                                 )  
     
        stills = data.get('stills')
        for i, val in enumerate(stills, start=1): 
            for subVal in val:
                if subVal:
                    result &= self.webParser.utils.download_file(subVal,
                                     '%s\\%s' % (sub_dir_name, str(i)),
                                    headers={'Referer':data.get('productUrl')}
                             )   
                    break    
                
        videos = data.get('video')
        for video in videos:
            result &=  self.webParser.utils.download_file(video,
                                '%s\\%s' % (sub_dir_name, data.get('productName')),
                                headers={'Referer':data.get('productUrl')}
                                 ) 
            break      
 
        return result      
        
class CWebParserSite(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserSiteCommon(self)    
        self.dbUtils = CWebDataDbUtis('Xerotica')
        
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
                    items = a('div.content div.modelItem')
                    
                    for item in items.items():
                        modelurl = item('a.title').attr('href')
                        model = item('a.title').text()
                        board = item('img').attr('src')
                        
                        html2 = self.utils.get_page(modelurl)      
                        if html2:
                            b = pq(html2)
                            items_model = b('div.content div.item')
                            for item_model in items_model.items():
                                data = self.common.parse_item(item_model) 
                                if data:
                                    data['url']   = modelurl      
                                    data['model'] = model
                                    data['board'] = board                                          
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
    parser.add_argument('-e', type=int, default = 136)
    parser.add_argument('-f', type=str, default = 'Xerotica\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('https://www.xerotica.com/models/page{page}.html', args.s, args.e, args.f, args.p)
    job.call_process() 
    
if __name__ == '__main__':   
    Job_Start() 
