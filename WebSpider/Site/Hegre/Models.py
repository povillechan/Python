# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParserUrl import CWebParserSingleUrl
from Common.CWebSpiderUtils import CWebSpiderUtils

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import vthread

class CWebParserSite(CWebParserSingleUrl):
        
    def __init__(self, url, savePath):
        super(CWebParserSingleUrl, self).__init__(url)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)
               
    '''
    parse_page
    
    @author: chenzf
    ''' 
    def parse_page(self):
        try:
            urlsGen = self.urls_genarator()
            while True: 
                url = next(urlsGen)
                if not url:
                    return None
                
                html = self.utils.get_page(url)                
                if html:          
                    data = {}
                    soup = BeautifulSoup(html, 'lxml')   
                    #board_image
                    board_image  = soup.find('div', class_="board_image")
                    if board_image:
                        name  = board_image.find('img').attrs['alt'].strip()
                        board_image = board_image.find('img').attrs['src']     
                    else:
                        board_image = None
                  
                    data['board'] = board_image
                    data['name'] = name
                       
                    #poster_image
                    poster_image  = soup.find('div', class_="poster_image")
                    if poster_image:
                        poster_image = poster_image.find('img').attrs['src']
                    else:
                        poster_image = None
                
                    data['poster'] = poster_image
                    
                    #products  
                    details = soup.find('div', class_="details")
                    counts = details.find('div', class_="counts")
                    items = counts.find_all('a')
                    products = []
                    for item in items:
                        products.append(item.get_text().strip())
                                
                    data['products'] = products
                    
                    #profile    
                    labels = soup.find('div', class_="labels")
                    rows = labels.find_all('div', class_="row")
                    profile = []
                    for row in rows:
                        profile.append(row.get_text().strip().replace('\n', '')) 
                    data['profile'] = profile     
                                                  
                    data['galleries'] = self.parse_galleries(soup)            
                    data['films'] = self.parse_films(soup)      
                    data['massages'] = self.parse_massages(soup)      
                    yield data        
        except:
            print('error in parse %s' % url)
            yield None    

        yield None
        
        
    def parse_galleries(self, soup):
        galleries_dict = []
        galleries = soup.find(id = 'galleries-wrapper')
     
        if galleries:
            items = galleries.find_all('div', class_='item')
            for item in items:
                date_item = item.find('small').string.replace(' ','-').replace(',','-').replace('--','-').split('-')
                date = date_item[2] +'-'+ date_item[0]+'-'+ date_item[1]
                 
                mid = item.find('a', attrs={'data-lightbox':"lightbox--poster_image"})
                if not mid:
                    mid_url = None;
                else:
                    mid_url = mid.attrs['href']
                     
                large = item.find('a', attrs={'data-lightbox':"lightbox--board_image"})
                if not large:
                    large_url = None;
                else:
                    large_url = large.attrs['href']     
                    
                url = urljoin('http://www.hegre.com/', item.find('a').attrs['href'])
                html = self.utils.get_page(url)    
                soup = BeautifulSoup(html, 'lxml')   
                
                cover = soup.find('div', class_='non-members', attrs={"style": re.compile('background-image.*?')})
                if cover:
                    cover = re.search('.*?url\((.*?)\)', cover.attrs['style']).group(1)
                else:
                    cover = None
                       
                galleries_dict.append({
                    'name'  :  self.utils.format_name(item.find('img').attrs['alt']),
                    'url'   :  url,
                    'board' :  [cover, large_url],
                    'poster':  [mid_url, item.find('img').attrs['src']],
                    'date'  :  date                               
                    })
        return galleries_dict
        
    def parse_massages(self, soup):
        massages_dict=[]
        massages = soup.find(id = 'massages-wrapper')
        
        if massages:
            items = massages.find_all('div', class_='item')
            for item in items:
                mid = item.find('a', attrs={'data-lightbox':"lightbox--poster_image"})
                if not mid:
                    mid_url = None;
                else:
                    mid_url = mid.attrs['href']
                     
                large = item.find('a', attrs={'data-lightbox':"lightbox--board_image"})
                if not large:
                    large_url = None;
                else:
                    large_url = large.attrs['href']                 
                                
                url = urljoin('http://www.hegre.com/', item.find('a').attrs['href'])
                video, date, cover= self.parse_massages_detail(url)
                         
                massages_dict.append({
                    'name'   :  self.utils.format_name(item.find('img').attrs['alt']),
                    'url'    :  url,
                    'board'  :  [cover, large_url, item.find('img').attrs['src']],
                    'poster' :  [],
                    'video'  :  video,
                    'date'   :  date     
                    })
        return massages_dict
 
    def parse_massages_detail(self, url):
        data = {}
        html = self.utils.get_page(url)    
        soup = BeautifulSoup(html, 'lxml')   

        item  = soup.find('div', class_="video-player-wrapper")
        
        board = None
        if item:       
            style_text  = item.attrs['style']
            board  = re.search("url\(\'(.*?)\'\)", style_text, re.S).group(1) 
    
        Full = []
        items = soup.find_all('div', class_="resolution content ")
        for item in items:
            Full.append(item.find('a').attrs['href'])
        data['full'] = Full
        
        Trailer = []
        items = soup.find_all('div', class_="resolution trailer top-resolution")
        for item in items:
            Trailer.append(item.find('a').attrs['href'])
        data['trailer'] = Trailer
        
        item =soup.find('div',class_='video-stills')
        Stills = []
        if item:
            stills = item.find_all('div', class_="img-holder")
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
        date = soup.find('span', class_="date").string
        return data, date, board
            
    def parse_films(self, soup):
        films_dict=[]
        films = soup.find(id = 'films-wrapper')
        if films:
            items = films.find_all('div', class_='item')
            for item in items:
                mid = item.find('a', attrs={'data-lightbox':"lightbox--poster_image"})
                if not mid:
                    mid_url = None;
                else:
                    mid_url = mid.attrs['href']
                     
                large = item.find('a', attrs={'data-lightbox':"lightbox--board_image"})
                if not large:
                    large_url = None;
                else:
                    large_url = large.attrs['href']        
                                                
                url = urljoin('http://www.hegre.com/', item.find('a').attrs['href'])
                video, date, cover= self.parse_films_detail(url)
                         
                films_dict.append({
                    'name'   :  self.utils.format_name(item.find('img').attrs['alt']),
                    'url'    :  url,
                    'board'  :  [cover,large_url],
                    'poster' :  [mid_url, item.find('img').attrs['src']],
                    'video'  :  video,
                    'date'   :  date     
                    })
        return films_dict


    def parse_films_detail(self, url):
        data = {}
    
        html = self.utils.get_page(url)    
        soup = BeautifulSoup(html, 'lxml')    
        board = None
            
        item  = soup.find('div', class_="video-player-wrapper") 
        if item:       
            style_text  = item.attrs['style']
            board  = re.search("url\(\'(.*?)\'\)", style_text, re.S).group(1)
    
        if board:  
            pass
        else:
            item  = soup.find('div', class_="content-overlay-wrapper") 
            if item:
                style_text  = item.select_one('div[class="non-members"]').attrs['style']
                board  = re.search("url\((.*?)\)", style_text, re.S).group(1)
    
        Full = []
        items = soup.find_all('div', class_="resolution content ")
        for item in items:
            Full.append(item.find('a').attrs['href'])
        data['full'] = Full
        
        Trailer = []
        items = soup.find_all('div', class_="resolution trailer top-resolution")
        for item in items:
            Trailer.append(item.find('a').attrs['href'])
        data['trailer'] = Trailer
        
        item =soup.find('div',class_='video-stills')
        Stills = []
        if item:
            stills = item.find_all('div', class_="img-holder")
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
        date = soup.find('span', class_="date").string
        return data, date, board
    
    '''
    process_image
    
    @author: chenzf
    '''  
    @vthread.pool(8)
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
                                    '%s\\%s' % (data.get('name'), 'poster')
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
            for poster in posters:
                if poster:
                    self.utils.download_file(poster,
                                    '%s\\%s\\%s\\%s' % (modelName, 'galleries', item.get('name'), 'poster')
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
    '''     
    urls_genarator
    
    @author: chenzf
    '''                
    def urls_genarator(self):
        html = self.utils.get_page(self.url)
        soup = BeautifulSoup(html, 'lxml')
        item_div = soup.find_all('div', class_="item")   
        
        for item in item_div:
            url  = urljoin('http://www.hegre.com/',  item.find('a', class_='artwork').attrs['href'].strip())
            yield url
        return None

    
def Job_Start():
    print(__file__, "start!")
    job = CWebParserSite('https://www.hegre.com/models', 'd:\\Pictures\\WebSpider\\Hegre-Art\\Hegre\\Models\\{filePath}')
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
