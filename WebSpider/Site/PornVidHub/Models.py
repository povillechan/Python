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

from Common.CWebParserUrl import CWebParserMultiUrl
from Common.CWebSpiderUtils import CWebSpiderUtils
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import vthread

class CWebParserSite(CWebParserMultiUrl):
        
    def __init__(self, url, start, end, savePath):
        super(CWebParserMultiUrl, self).__init__(url, start, end)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)
             
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
                    contents = soup('.listProfiles li')

                    for content in contents.items():
                        data = {}               
                        try:
                            step = 1
                            name = None
                            modelurl = None
                            board = None
                            if content('a.thumb'):
                                modelurl = urljoin('http://www.pornvidhub.com/',  content('a.thumb').attr('href'))                     
                                name = content('a.title').text()
                                board = content('img').attr('src')                                 
                                 
                            data['name']  = name
                            data['url']   = modelurl        
                            data['board'] = board                    
                             
                            step = 2
                            if modelurl:
                                videos_all = self.parse_video(modelurl)  
                                step = 3
                                while True:
                                    video_one, isLast = next(videos_all)
                                    if not video_one:
                                        step = 4
                                        break                                     
                       
                                    if isLast:
                                        data['videos'] = video_one
                                        self.save_info(data)
                                        step = 5
                                    else:    
                                        data_temp = deepcopy(data)
                                        data_temp['videos'] = video_one                                     
                                        yield data_temp
                                        step = 6    
                            else:
                                data['videos'] = []                            
                                yield data 
                            step = 7

                        except:
                            errMsg = 'error in parse %s , step %s' % (modelurl, step)
                            print(errMsg)
                            self.log(errMsg)         
            except:
                print('error in parse %s' % url)
                yield None    

        yield None
        
        
    def parse_video(self, url):
        videos_dict = []
                
        browser = CWebSpiderUtils(None)
        browser.init_chrome()
        
        while True:
            html = self.utils.get_page(url)    
            page=pq(html)
            items = page('.listThumbs li')
    
            for item in items.items():                              
                    url = urljoin('http://www.pornvidhub.com/', item('a.title').attr['href'])
                    if url:
                        video, still= self.parse_video_detail(url, browser)
                    else:
                        video  = None
                        still = []
                    
                    video_item =  {
                        'name'  :  self.utils.format_name(item('a.title').attr['title']),
                        'url'   :  url,
                        'video' :  video,     
                        'stills' :  still                      
                        }      
                    yield [video_item], False
                    videos_dict.append(video_item)
                    
            next_btn = page('span.numbers').nextAll('a.nav')
            if next_btn:
                url = urljoin('http://www.pornvidhub.com/',  next_btn.attr['href']) 
            else:
                break
                
        browser.close_chrome()
        yield videos_dict, True
        
        yield None, False
    
    def parse_video_detail(self, url, browser):
        html = browser.get_chrome(url, '#player #html5')  
        if not html:
            return None,[]
        
        soup = BeautifulSoup(html,'lxml') 
        Stills = []
        stills = soup.find(id='tabPhotos').find_all('img')
        for still in stills:  
            small_url = still.attrs['src']                        
            thumb = re.search('.*?/(\d+x\d+/).*?', small_url, re.S)
            if thumb:
                large_url  = small_url.replace(thumb.group(1),"")
            else:
                large_url = None                
                
            Stills.append([ large_url, small_url ])
          
        soup = pq(html) 
        video_text = soup('#player #html5')
        if video_text:
            video = video_text.attr['src']
        return video, Stills          
    
      
    '''
    process_image
    
    @author: chenzf
    '''  
#     @vthread.pool(8)
    def process_data(self, data):
#         self.save_info(data)
#         print(data.get('videos')[0].get('name'))
        board = data.get('board')
        if board:
            self.utils.download_file(board,
                                    '%s\\%s' % (data.get('name'), data.get('name'))
                                     )                         

        self.process_videos(data)
   
    def process_videos(self, data):
        videos = data.get('videos')
        modelName = data.get('name')
        
        for item in videos:
            stills = item.get('stills')
            for i, val in enumerate(stills, start=1): 
                for subVal in val:
                    if subVal:
                        self.utils.download_file(subVal,
                                    '%s\\%s\\%s' % (modelName, item.get('name'), str(i))
                                     )   
                        break  
                    
            video = item.get('video')
            if video:
                self.utils.download_file(video,
                                    '%s\\%s\\%s' % (modelName, item.get('name'), item.get('name')),
                                    headers={'Referer':data.get('url')}       
                                     )   
                break
                    
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-s', type=int, default = 1)
    parser.add_argument('-e', type=int, default= 168)
    parser.add_argument('-f', type=str, default= 'd:\\Pictures\\WebSpider\\PornVidHub\\Models\\{filePath}')
    args = parser.parse_args()
    print(args)

    job = CWebParserSite('http://www.pornvidhub.com/stars?p={page}', args.s, args.e, args.f)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
