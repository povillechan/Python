# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json

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
        try:
            urlsGen = self.urls_genarator()
            while True:
                url = next(urlsGen)
                if not url:
                    return None
                html = self.utils.get_page(url)
                
                if html:                    
                    soup = BeautifulSoup(html, 'lxml')   
                    items = soup.find_all('div', class_="item")
                    
                    for item in items:
                        posterImg = item.find('div', class_='img-holder').find('img').attrs['src']                       
                
                        mid = item.find('div', class_='cover-links').find('a', attrs={'data-lightbox':"lightbox--posterImg"})
                        if not mid:
                            midUrl = None;
                        else:
                            midUrl = mid.attrs['href']
                
                        large = item.find('div', class_='cover-links').find('a', attrs={'data-lightbox':"lightbox--board_image"})
                        if not large:
                            largeUrl = None;
                        else:
                            largeUrl = large.attrs['href']   
                
                        name = item.find('a', class_='open-in-content-overlay').attrs['title'].strip()
                        url = urljoin('http://www.hegre.com/', item.find('a', class_='open-in-content-overlay').attrs['href'])
                        data = {
                			'name'  : self.utils.format_name(name),
                            'small' : posterImg,
                            'mid'   : midUrl,
                            'large' : largeUrl,
                            'url'   : url,
                            'detail': self.process_data_detail(url)
                            }
                        yield data        
        except:
            print('error in parse %s' % url)
            yield None    

        yield None
    
    '''
    parse_page
    
    @author: chenzf
    ''' 

    def parse_page_detail(self, html):    
        data = {}
    
        soup = BeautifulSoup(html, 'lxml')   

        board = None    
        item = soup.find('div', class_="content-overlay-wrapper") 
        if item:
            style_text = item.select_one('div[class="non-members"]').attrs['style']
            board = re.search("url\((.*?)\)", style_text, re.S).group(1)        
        data['board'] = board
                
        DownLoad = []
        items = soup.find_all('div', class_="gallery-zips")
        for item in items:
            DownLoad.append(item.find('a').attrs['href'])
        data['download'] = DownLoad   
        
        data['date'] = soup.find('span', class_="date").string
        return data      
               
    '''
    process_data_detail
    
    @author: chenzf
    '''                  

    def process_data_detail(self, url):
        detail = None
        html = self.utils.get_page(url)
        if html:
            detail = self.parse_page_detail(html)
          
        return detail     
  
    '''
    process_data
    
    @author: chenzf
    '''  
    @vthread.pool(8)
    def process_data(self, data):
        dir_name = self.savePath.format(filePath=data.get('name'))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\info.json', 'w') as f:    
            json.dump(data, f)
        
        for subkeys in ['large', 'mid', 'small']:
            url = data.get(subkeys)    
            if url:
                self.utils.download_file(url,
                                        '%s\\%s' % (data.get('name'), data.get('name'))
                                        )
                break
        
        detail = data.get('detail')
        board = detail.get('board')
        if board:
            self.utils.download_file(board,
                                    '%s\\%s' % (data.get('name'), 'cover')
                                     )
        elif data.get('mid'):
            board = data.get('mid')
            self.utils.download_file(board, 
                                    '%s\\%s' % (data.get('name'), 'cover')
                                    )
    
    
def Job_Start():
    print(__file__, "start!")
    job = CWebParserSite('http://www.hegre.com/photos?galleries_page={page}', 1, 25, 'd:\\Pictures\\WebSpider\\Hegre-Art\\Hegre\\Photos\\{filePath}')
    job.call_process()

    
if __name__ == '__main__':   
    Job_Start()
