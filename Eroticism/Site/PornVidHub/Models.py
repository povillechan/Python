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

class CWebParserPornVidHubCommon(object):
    def __init__(self, webParser):
        self.webParser = webParser
#    
    def parse_item(self, item):    
#         data = None      
#         url = item('a').attr('href')
#         discrib = item('a').attr('title')
#         if not discrib:
#             discrib = item('img').attr('alt')
#         result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))
# 
#         if self.webParser.parseOnly == CParseType.Parse_Brief:  
#             data = { 
#                 'url'     :  url,
#                 'discrib' :  self.webParser.utils.format_name(discrib),
#                 'board'   :  [result[0] if result and len(result) >= 2 else None,item('img').attr('src'), result[1] if result and len(result) >= 2 else None],
#             }             
#         else:
        step = 0
        try:
            data = {}
            step = 1
            name = None
            modelurl = None
            board = None
            if item('a.thumb'):
                modelurl = urljoin('http://www.pornvidhub.com/',  item('a.thumb').attr('href'))                     
                name = item('a.title').text()
                board = item('img').attr('src')                                 
                  
            data['name']  = name
            data['url']   = modelurl        
            data['board'] = board                               
#                           
            step = 2
            if modelurl:
                videos_all = self.parse_video(data, modelurl)  
                step = 3
                while True:
                    try:
                        video_one = next(videos_all)
                        if not video_one:
                            step = 4
                            break                                     
    #                         
    #                                     if isLast:
    #                                         data['videos'] = video_one
    #                                         self.save_info(data)
    #                                         step = 5
    #                                     else:    
                        data_temp = deepcopy(data)
                        data_temp['videos'] = video_one     
    #                                         
    # #                                         if self.parseOnly == 1:
    # #                                             try:
    # #                                                 datatmp = deepcopy(data_temp)
    # #                                                 if self.common.dbBriefJob.find_one(datatmp) or self.common.dbBriefJobParsed.find_one(datatmp):
    # #                                                     print('a db record already exist!')
    # #                                                 else:
    # #                                                     print('insert a db record!')
    # #                                                     self.common.dbBriefJob.insert_one(datatmp)     
    # #                                                     self.log('parsed url %s' % url)      
    # #                                             except Exception as e:
    # #                                                 print('database error')
    # #                                                 print(e) 
                        step = 5
                        yield data_temp
                        step = 6    
    #                             else:
    #                                 data['videos'] = []                            
    #                                 yield data 
    #                             step = 7
                    except Exception as e:
                        self.webParser.log('parse video error')
                        print(e) 
                        continue
        except Exception as e:
            print(e)
            self.webParser.log('error in parse content in step' % step)
            yield None
                        
        yield None         

    def parse_detail_fr_brief(self, item):
        data = deepcopy(item)

        url = data.get('videos').get('url')
        if url:
            video, still= self.parse_video_detail(url)
                        
            video_item =  {
                            'name'   :  data.get('videos').get('name'),
                            'url'    :  url,
                            'video'  :  video,     
                            'stills' :  still                      
                            }      
            data['videos'] =  video_item     
            return data

        return None
                        
    def parse_video(self, data, url):
#         videos_dict = []
#                 
#         browser = CWebSpiderUtils(None)
#         browser.init_chrome()
        
        while True:
            html = self.webParser.utils.get_page(url)    
            page=pq(html)
            items = page('.listThumbs li')
    
            for item in items.items():                              
                    url = urljoin('http://www.pornvidhub.com/', item('a.title').attr['href'])
                    if self.webParser.parseOnly == CParseType.Parse_Brief:
                        video_item =  {
                            'name'  :  self.webParser.utils.format_name(item('a.title').attr['title']),
                            'url'   :  url,            
                        }                              
                            
                        yield video_item
                    else:
                        if url:
                            video, still= self.parse_video_detail(url)
                        else:
                            video  = None
                            still = []
                        
                        video_item =  {
                            'name'  :  self.webParser.utils.format_name(item('a.title').attr['title']),
                            'url'   :  url,
                            'video' :  video,     
                            'stills' :  still                      
                            }      
                        yield video_item
#                         videos_dict.append(video_item)

            next_btn = page('span.numbers').nextAll('a.nav')
            if next_btn:
                url = urljoin('http://www.pornvidhub.com/',  next_btn.attr['href']) 
            else:
                break
                
#         browser.close_chrome()
#         yield videos_dict, True
        
        yield None
    
    def parse_video_detail(self, url):
        html = self.webParser.utils.get_page(url)       
        if not html:
            return None,[]
#             
#         html = browser.get_chrome(url, '#player #html5')  
#         if not html:
#             return None,[]
        
        soup = BeautifulSoup(html,'lxml') 
        Stills = []
        stills = soup.find(id='tabPhotos').find_all('img')
        for still in stills:  
            small_url = still.attrs['src']  
            if not small_url:
                small_url = still.attrs['data-src']
            thumb = re.search('.*?/(\d+x\d+/).*?', small_url, re.S)
            if thumb:
                large_url  = small_url.replace(thumb.group(1),"")
            else:
                large_url = None                
                
            Stills.append([ large_url, small_url ])
          
        video = None
        video_script = re.search('var q=.*?:"(.*?)"', html, re.S)
        if video_script:
            video = video_script.group(1)
        return video, Stills    
      
    '''
    process_image
    
    @author: chenzf
    '''  
#     @vthread.pool(8)
    def process_data(self, data):
        result = True
        if self.webParser.parseOnly == CParseType.Parse_Brief:
           return 
       
        board = data.get('board')
        if board:
            result &= self.webParser.utils.download_file(board,
                                    '%s\\%s' % (data.get('name'), data.get('name'))
                                     )                         

        result &= self.process_videos(data)

        return result
    
    def process_videos(self, data):
        videos = data.get('videos')
        modelName = data.get('name')
        result = True

        stills = videos.get('stills')
        for i, val in enumerate(stills, start=1): 
            for subVal in val:
                if subVal:
                    result &= self.webParser.utils.download_file(subVal,
                                '%s\\%s\\%s' % (modelName, videos.get('name'), str(i))
                                 )   
                    break  
                
        video = videos.get('video')
        if video:
            result &= self.webParser.utils.download_file(video,
                                '%s\\%s\\%s' % (modelName, videos.get('name'), videos.get('name')),
                                headers={'Referer':data.get('url')}       
                                 )   

        return result
        
        
class CWebParserSite(CWebParserMultiUrl):
        
    def __init__(self, url, start, end, savePath, parseOnly):
        super(CWebParserMultiUrl, self).__init__(url, start, end)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserPornVidHubCommon(self)    
        self.dbUtils = CWebDataDbUtis("PornVidHub")    
        
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
                    return None
                
                html = self.utils.get_page(url)                
                if html:        
                    soup = pq(html)     
                    items = soup('.listProfiles li')

                    for item in items.items():
                        data = {}               
                        try:
                            data_gen = self.common.parse_item(item)
                            while True:
                                data = next(data_gen)
                                if not data:
                                    break
                                
                                yield data                        

                        except:
                            self.log( 'error in item in url %s' % url)         
                            continue     
                    self.log('parsed url %s' % url)  
                else:
                    self.log('request %s error' %url)         
            except:
                self.log( 'error in parse url %s' % url)         
                yield None    
        yield None            

    def parse_brief(self):
        return self.parse_page()
    
    def parse_detail(self):
        for item in self.dbUtils.get_db_item():
#             try:
#                 data = self.common.parse_detail_fr_brief(item) 
#                 yield data
#                 else:
#                     continue                                
#             except:
#                 self.log('error in parse item')         
#                 continue   
            data = deepcopy(item) 
            data.pop('_id')
            yield data
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
    parser.add_argument('-e', type=int, default=  168)
    parser.add_argument('-f', type=str, default=  'd:\\Pictures\\WebSpider\\PornVidHub\\Models\\{filePath}')
    parser.add_argument('-p', type=int, default=  '0')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('http://www.pornvidhub.com/stars?p={page}', args.s, args.e, args.f, args.p)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
