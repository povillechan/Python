# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParserSingleUrl import CWebParserSingleUrl
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
                  
                    data['board_image'] = board_image
                    data['name'] = name
                       
                    #poster_image
                    poster_image  = soup.find('div', class_="poster_image")
                    if poster_image:
                        poster_image = poster_image.find('img').attrs['src']
                
                    data['poster_image'] = poster_image
                    
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
#             galleries_dict = []
#             galleries = soup.find(id = 'galleries-wrapper')
#         
#             if galleries:
#                 items = galleries.find_all('div', class_='item')
#                 for item in items:
#                     date_item = item.find('small').string.replace(' ','-').replace(',','-').replace('--','-').split('-')
#                     date = date_item[2] +'-'+ date_item[0]+'-'+ date_item[1]
#                     
#                     mid = item.find('a', attrs={'data-lightbox':"lightbox--poster_image"})
#                     if not mid:
#                         mid_url = None;
#                     else:
#                         mid_url = mid.attrs['href']
#                         
#                     large = item.find('a', attrs={'data-lightbox':"lightbox--board_image"})
#                     if not large:
#                         large_url = None;
#                     else:
#                         large_url = large.attrs['href']        
#                     
#                     galleries_dict.append({
#                         'name':  utils.format_name(item.find('img').attrs['alt']),
#                         'url': urljoin('http://www.hegre.com/', item.find('a').attrs['href']),
#                         'small': item.find('img').attrs['src'],
#                         'mid': mid_url,
#                         'large': large_url,
#                         'date':date            
#                         })
        return None
        
    def parse_massages(self, soup):
#             massages_dict=[]
#             massages = soup.find(id = 'massages-wrapper')
#             if massages:
#                 items = massages.find_all('div', class_='item')
#                 for item in items:
#                     mid = item.find('a', attrs={'data-lightbox':"lightbox--poster_image"})
#                     if not mid:
#                         mid_url = None;
#                     else:
#                         mid_url = mid.attrs['href']
#                         
#                     large = item.find('a', attrs={'data-lightbox':"lightbox--board_image"})
#                     if not large:
#                         large_url = None;
#                     else:
#                         large_url = large.attrs['href']        
#                     
#                     massages_dict.append({
#                         'name': utils.format_name(item.find('img').attrs['alt']),
#                         'url': urljoin('http://www.hegre.com/', item.find('a').attrs['href']),
#         #              'small': item.find('img').attrs['src'],
#                         'mid': mid_url,
#                         'large': large_url,      
#                         })
        return None
 
                
    def parse_films(self, soup):
#             films_dict=[]
#             films = soup.find(id = 'films-wrapper')
#             if films:
#                 items = films.find_all('div', class_='item')
#                 for item in items:
#                     mid = item.find('a', attrs={'data-lightbox':"lightbox--poster_image"})
#                     if not mid:
#                         mid_url = None;
#                     else:
#                         mid_url = mid.attrs['href']
#                         
#                     large = item.find('a', attrs={'data-lightbox':"lightbox--board_image"})
#                     if not large:
#                         large_url = None;
#                     else:
#                         large_url = large.attrs['href']        
#                     
#                     films_dict.append({
#                         'name': utils.format_name(item.find('img').attrs['alt']),
#                         'url': urljoin('http://www.hegre.com/', item.find('a').attrs['href']),
#                         'small': item.find('img').attrs['src'],
#                         'mid': mid_url,
#                         'large': large_url,      
#                         })
        return None

    '''
    process_image
    
    @author: chenzf
    '''  
    def process_data(self, data):
        print(data)
#             dir_name = utils.dir_path.format(file_path=data.get('name'))
#             if not os.path.exists(dir_name):
#                 os.makedirs(dir_name)
#                 
#             
#             with open(dir_name+'\\info.json', 'w') as f:    
#                 json.dump(data, f)
#                 
#             url = data.get('poster_image')
#             utils.download_file(url, utils.get_file_path(url, data.get('name') + '\\poster_image'))
#                
#             url = data.get('board_image')
#             utils.download_file(url, utils.get_file_path(url, data.get('name') + '\\board_image'))
#             
#             for keys in ['galleries', 'films','massages']:
#                 for keys_item in data.get(keys):
#                     dir_name = utils.dir_path.format(file_path=data.get('name')+'\\'+ keys+'\\'+ keys_item.get('name'))            
#         
#                     if not os.path.exists(dir_name):
#                         os.makedirs(dir_name)
#         
#                     for subkeys in ['large']:
#                         url = keys_item.get(subkeys)
#         #
#                         if url:
#                             utils.download_file(url, utils.get_file_path(url, data.get('name')+'\\'+ keys+'\\'+ keys_item.get('name') + '\\board'))
#                             break
#         
#                     for subkeys in ['mid','small']:
#                         url = keys_item.get(subkeys)
#         #
#                         if url:
#                             utils.download_file(url, utils.get_file_path(url, data.get('name')+'\\'+ keys+'\\'+ keys_item.get('name') + '\\' + keys_item.get('name')))
#                             break 
        pass
  
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
