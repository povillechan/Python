# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json
import argparse
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParserUrl import CWebParserMultiUrl
from Common.CWebSpiderUtils import CWebSpiderUtils

from bs4 import BeautifulSoup
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
                    yield None
                
                html = self.utils.get_page(url)                
                if html:        
                    soup = BeautifulSoup(html, 'lxml')     
                    contents = soup.select('#block-system-main .node-grid .grid-meta')

                    for content in contents:
                        data = {}               
                        try:
                            step = 1
                            name = None
                            modelurl = None
                            if content.find('a'):
                                name = content.find('a').text
                                modelurl = urljoin('http://www.hegregirls.com/',  content.find('a').attrs['href'])                     
                           
                            nick = None
                            if content.find('div', class_='nick'):
                                nick = content.find('div', class_='nick').text
                                
                            products = None
                            if content.find('span', class_='stats'):
                                products = content.find('span', class_='stats').text
                                
                            data['name']  = name
                            data['url']   = modelurl                             
                            data['nick']  = nick
                            data['products']   = products
                            
                            step = 2
                            htmlModel =  self.utils.get_page(modelurl) 
                            if htmlModel:
                                soupModel = BeautifulSoup(htmlModel, 'lxml')                                 
                                                           
                                step = 3
                                board_image  = soupModel.find('div', class_="field-name-model-board")
                                if board_image:
                                    board_image = board_image.find('img').attrs['src']     
                              
                                data['board'] = board_image
                                
                                step = 4
                                #poster_image
                                poster_image  = soupModel.find('div', class_="box border")
                                if poster_image:
                                    poster_image = poster_image.find('img').attrs['src']
                            
                                data['poster'] = poster_image                            
                               
                                step = 5
                                #profile                            
                                labels = soupModel.find('div', class_="box border")
                                rows = labels.find_all('li')
                                profile = []
                                for row in rows:
                                    profile.append(row.get_text().strip().replace('\n', '')) 
                                data['profile'] = profile                     
                                step = 6
                                #detail product                                                  
                                data['galleries'] = self.parse_galleries(soupModel)   
                                step = 7         
                                data['films'] = self.parse_films(soupModel)
                                step = 8      
                                data['massages'] = self.parse_massages(soupModel)     
                                step = 9 
                            
                            yield data   
                        except:
                            errMsg = 'error in parse %s , step %s' % (modelurl, step)
                            print(errMsg)
                            self.log(errMsg)         
            except:
                print('error in parse %s' % url)
                yield None    

        yield None
        
        
    def parse_galleries(self, soup):
        galleries_dict = []
        items = soup.select('#main-content .content .content .grid-4')
        for item in items:
            if re.search('galleries', item.attrs['about']):
                date = ""
                for s in item.find(class_="release-date").strings:
                    date += s
                 
                mid = item.find('img')
                if not mid:
                    mid_url = None;
                else:
                    mid_url = mid.attrs['src']
                     
                if mid:
                    large = mid.parent
                    large_url = large.attrs['rel'][0] 
                else:
                    large_url = None;   
                    
                url = urljoin('http://www.hegregirls.com/', item.attrs['about'])
                detailurl = item.select('.preview-link a')
                if detailurl:
                    detailurl = detailurl[0]               
                    freeurl = urljoin('http://www.hegregirls.com/', detailurl.attrs['href'])                                    
                    info, poster= self.parse_galleries_detail(freeurl)
                else:
                    info  = None
                    poster = []
                       
                galleries_dict.append({
                    'name'  :  self.utils.format_name(item.find('img').attrs['title']),
                    'url'   :  url,
                    'board' :  [large_url, mid_url],
                    'poster':  poster,
                    'info'  :  info,
                    'date'  :  date                               
                    })
        return galleries_dict
    
    def parse_galleries_detail(self, url):
        data = {}
        html = self.utils.get_page(url)    
        soup = BeautifulSoup(html, 'lxml') 
        
        board = soup.select('#preview-board img')
        if board:
            board = board[0].attrs['src'] 
             
        board_small = soup.find('div', class_='grid-12 alpha')
        if board_small:
            board_small = board_small.find('img')
            if board_small:
                board_small = board_small.attrs['src']
        
        poster = [board, board_small]
        
        Stills = []
        stills = soup.find_all('div', class_="grid-4")
        for still in stills:  
            small = still.find('img')
            if not small:
                small_url = None;
            else:
                small_url = small.attrs['src']   
                  
            large = still.find('a')
            if not large:
                large_url = None;
            else:
                large_url = large.attrs['href']   
 
            Stills.append([ large_url, small_url ])
                
        data['stills'] = Stills   
        
        return data, poster     
        
        
    def parse_massages(self, soup):
        massages_dict=[]
        items = soup.select('#main-content .content .content .grid-4')
        for item in items:
            if re.search('massages', item.attrs['about']):          
                mid = item.find('img')
                if not mid:
                    mid_url = None;
                else:
                    mid_url = mid.attrs['src']
                     
                large = item.find(class_='hegre-poster-zoom')
                if large:
                    large_url = large.attrs['href']
                else:
                    large_url = None;                               
                    
                url = urljoin('http://www.hegregirls.com/', item.attrs['about'])                              
                video, poster= self.parse_massages_detail(url)
                         
                massages_dict.append({
                    'name'   :  self.utils.format_name(item.find('img').attrs['alt']),
                    'url'    :  url,
                    'board'  :  [large_url, mid_url],
                    'poster' :  poster,
                    'video'  :  video,   
                    })
        return massages_dict    
 
    def parse_massages_detail(self, url):
        return self.parse_films_detail(url)
            
    def parse_films(self, soup):
        films_dict = []
        items = soup.select('#main-content .content .content .grid-4')
        for item in items:
            if re.search('films', item.attrs['about']):               
                mid = item.find('img')
                if not mid:
                    mid_url = None;
                else:
                    mid_url = mid.attrs['src']
                     
                large = item.find(class_='hegre-poster-zoom')
                if large:
                    large_url = large.attrs['href']
                else:
                    large_url = None;   
                    
                url = urljoin('http://www.hegregirls.com/', item.attrs['about'])                              
                video, poster= self.parse_films_detail(url)
                         
                films_dict.append({
                    'name'   :  self.utils.format_name(item.find('span').attrs['content']),
                    'url'    :  url,
                    'board'  :  [large_url, mid_url],
                    'poster' :  poster,
                    'video'  :  video, 
                    })
        return films_dict


    def parse_films_detail(self, url):
        data = {}
    
        html = self.utils.get_page(url)    
        soup = BeautifulSoup(html, 'lxml')    
        
        poster = []   
        item  = soup.find('video', class_="hegre-video") 
        if item:       
            poster.append(item.attrs['poster'])
            
        item = soup.find('div',class_='video-feature')
        if item:
            img = item.find('img')
            if img:
                poster.append(img.attrs['src'])
    
        Full = []
        data['full'] = Full       

        Trailer = []  
        video = soup.find('source')
        if video:
            Trailer.append(video.attrs['src'])
        data['trailer'] = Trailer

        Stills = []
        data['stills'] = Stills        

        return data, poster
    
    '''
    process_image
    
    @author: chenzf
    '''  
#     @vthread.pool(8)
    def process_data(self, data):
#         print(data)
        dir_name = self.savePath.format(filePath=data.get('name'))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)
            
        board = data.get('board')
        if board:
            self.utils.download_file(board,
                                    '%s\\%s' % (data.get('name'), 'board')
                                     )                         
            
        poster = data.get('poster')
        if poster:
            self.utils.download_file(poster,
                                    '%s\\%s' % (data.get('name'), data.get('name'))
                                     )   

        self.process_galleries(data)
        self.process_massages(data)
        self.process_films(data)
  
    def process_galleries(self, data):
        galleries = data.get('galleries')
        modelName = data.get('name')
        
        for item in galleries:
            boards = item.get('board')
            for board in boards:
                if board:
                    self.utils.download_file(board,
                                    '%s\\%s\\%s\\%s' % (modelName, 'galleries', item.get('name'), 'board')
                                     )      
                    break                   
            
            posters = item.get('poster')
            for i, val in enumerate(posters, start=1):
#             for poster in posters:
                if val:
                    self.utils.download_file(val,
                                    '%s\\%s\\%s\\%s_%s' % (modelName, 'galleries', item.get('name'), 'poster', str(i))
                                     )   
      
                        
            info = item.get('info')
            if info:
                stills = info.get('stills')
                for i, val in enumerate(stills, start=1): 
                    for subVal in val:
                        if subVal:
                            self.utils.download_file(subVal,
                                    '%s\\%s\\%s\\%s' % (modelName, 'galleries', item.get('name'), str(i))
                                     )   
                            break  
    
    def process_massages(self, data):
        massages = data.get('massages')
        modelName = data.get('name')
        
        for item in massages:
            boards = item.get('board')
            for board in boards:
                if board:
                    self.utils.download_file(board,
                                    '%s\\%s\\%s\\%s' % (modelName, 'massages', item.get('name'), 'board')
                                     )      
                    break                   
            
            posters = item.get('poster')
            for poster in posters:
                if poster:
                    self.utils.download_file(poster,
                                    '%s\\%s\\%s\\%s' % (modelName, 'massages', item.get('name'), 'poster')
                                     )   
                    break
            
            video = item.get('video')
            stills = video.get('stills')
            for i, val in enumerate(stills, start=1): 
                for subVal in val:
                    if subVal:
                        self.utils.download_file(subVal,
                                    '%s\\%s\\%s\\%s' % (modelName, 'massages', item.get('name'), str(i))
                                     )   
                        break  
                    
            trailers = video.get('trailer')
            for trailer in trailers:
                if trailer:
                    self.utils.download_file(trailer,
                                    '%s\\%s\\%s\\%s' % (modelName, 'massages', item.get('name'), item.get('name'))
                                     )   
                    break
    
    def process_films(self, data):
        films = data.get('films')
        modelName = data.get('name')
        
        for item in films:
            boards = item.get('board')
            for board in boards:
                if board:
                    self.utils.download_file(board,
                                    '%s\\%s\\%s\\%s' % (modelName, 'films', item.get('name'), 'board')
                                     )      
                    break                   
            
            posters = item.get('poster')
            for poster in posters:
                if poster:
                    self.utils.download_file(poster,
                                    '%s\\%s\\%s\\%s' % (modelName, 'films', item.get('name'), 'poster')
                                     )   
                    break
            
            video = item.get('video')
            stills = video.get('stills')
            for i, val in enumerate(stills, start=1): 
                for subVal in val:
                    if subVal:
                        self.utils.download_file(subVal,
                                    '%s\\%s\\%s\\%s' % (modelName, 'films', item.get('name'), str(i))
                                     )   
                        break  
                    
            trailers = video.get('trailer')
            for trailer in trailers:
                if trailer:
                    self.utils.download_file(trailer,
                                    '%s\\%s\\%s\\%s' % (modelName, 'films', item.get('name'), item.get('name'))
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
    
    job = CWebParserSite('http://hegregirls.com/models?page={page}', args.s, args.e, args.f)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
