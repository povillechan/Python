# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os,sys,vthread,re,json
from pyquery import PyQuery as pq
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,parentdir)

from Common.CWebParser import CWebParser
from Common.CWebParserUrl import CWebParserMultiUrl,CWebParserSingleUrl
from Common.CWebSpiderUtils import CWebSpiderUtils

class CWebParserHunterMultiUrl(CWebParserMultiUrl):    
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
                    a = pq(html)   
                    #items
                    items = a('nav.pagination-a').prev_all('ul li')
                
                    for item in items.items():
                        if item.hasClass('vid'):
                            continue
                        
                        url = item('a').attr('href')
                        discrib = item('a').attr('title')
                        result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))
            
                        b = pq(url)
                            
                        art_site_info = b('#breadcrumbs li')
                        info_string = []
                        for it in art_site_info.items(): 
                            info_string.append(it.text())
                            
                        if len(info_string) >=3:
                            site, model, name  = info_string[0], info_string[1], info_string[2]
                        
                        previews = b('ul.gallery-b  li')
                        stills = []
                        for preview in previews.items():
                            stills.append([ preview('a').attr('href'), preview('img').attr('src')])
                               
                        data = {    
                            'site'    :  site,
                            'name'    :  self.utils.format_name(name),  
                            'model'   :  self.utils.format_name(model),  
                            'discrib' :  self.utils.format_name(discrib),
                            'board'   :  [result[0] if result and len(result) >= 2 else None,item('img').attr('src'), result[1] if result and len(result) >= 2 else None],
                            'url'     :  url,
                            'stills'  :  stills,          
                            }            
                        yield data
            except:
                print('error in parse %s' % url)
                yield None    
        
        yield None
    
    '''
    process_image
    
    @author: chenzf
    '''    
    @vthread.pool(8)  
    def process_data(self, data):
#         print(data)
        sub_dir_name = "%s\\%s\\galleries\\%s %s" %(data.get('site'), data.get('model'), data.get('model'),data.get('name'))
        dir_name = self.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\..\\info.json', 'w') as f:    
            json.dump(data, f)
            
        boards = data.get('board')
        for board in boards:
            if board:
                self.utils.download_file(board,
                                        '%s\\%s' % (sub_dir_name, data.get('name')),
                                        headers={'Referer':data.get('url')}        
                                         )     
                break                     
          
        stills = data.get('stills')
        for i, val in enumerate(stills, start=1): 
            for subVal in val:
                if subVal:
                    self.utils.download_file(subVal,
                                     '%s\\%s' % (sub_dir_name, str(i)),
                                     headers={'Referer':data.get('url')}        
                             )   
                    break    

class CWebParserHunterSingleUrl(CWebParserSingleUrl):    
    def __init__(self, url):
        self.url = url
        self.start = None
        self.end = None    