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
import pymongo
from copy import deepcopy
import vthread

class CWebParserHunterCommon(object):
    def __init__(self, savePath,parseOnly):
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath) 
        self.dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.dbname   = self.dbclient["HegreHunter"]
        self.dbcol    = self.dbname["datas"]   
        self.parseOnly = parseOnly 
   
    def parse_item(self, item):
        
        url = item('a').attr('href')
        discrib = item('a').attr('title')
        if not discrib:
            discrib = item('img').attr('alt')
        result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))


        if self.parseOnly == 1:     
            data = None   
            try:
                data = { 
                    'discrib' :  self.utils.format_name(discrib),
                    'board'   :  [result[0] if result and len(result) >= 2 else None,item('img').attr('src'), result[1] if result and len(result) >= 2 else None],
                    'url'     :  url,
                }
                datatmp = deepcopy(data)
                if self.dbcol.find_one(datatmp):
                    print('a db record already exist!')
                else:
                    print('insert a db record!')
                    self.dbcol.insert_one(datatmp)     
            except Exception as e:
                print('database error')
                print(e)
                
            return data
            
        else:
            b = pq(url)
                
            art_site_info = b('#breadcrumbs li')
            info_string = []
            for it in art_site_info.items(): 
                info_string.append(it.text())
                
            if len(info_string) >=3:
                site, model, name  = info_string[0], info_string[1], info_string[2]
            
            video = None
            video_item = b('video')
            if video_item:
                src = []
    
                for src_item in video_item('source').items():
                    src.append(src_item.attr('src'))
                video={
                        'src': src,
                        'poster':video_item.attr('poster')
                        }  
            else:                                
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
                'video'   :  video      
                }        
                    
            return data            
        
    def process_data(self, data):
#         print(data)
        if data.get('video'):
            sub_dir_name = "%s\\%s\\films\\%s %s" %(data.get('site'), data.get('model'), data.get('model'),data.get('name'))
        else:
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
        
        if data.get('video'):
            for src in data.get('video').get('src'): 
                self.utils.download_file(src,
                            '%s\\%s' % (sub_dir_name, data.get('name')),
                            headers={'Referer':data.get('url')}        
                             )    
                break
            
            self.utils.download_file(data.get('video').get('poster'),
                            '%s\\%s' % (sub_dir_name, data.get('name')),
                            headers={'Referer':data.get('url')}        
                             ) 
            
        else:        
            stills = data.get('stills')
            for i, val in enumerate(stills, start=1): 
                for subVal in val:
                    if subVal:
                        self.utils.download_file(subVal,
                                         '%s\\%s' % (sub_dir_name, str(i)),
                                         headers={'Referer':data.get('url')}        
                                 )   
                        break
                    
    def get_db_item(self, start, len):
        return self.dbcol.find()[int(start):(int(start) + int(len))]     
        
        
class CWebParserHunterMultiUrl(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super(CWebParserMultiUrl, self).__init__(url, start, end)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.common = CWebParserHunterCommon(savePath, parseOnly)    
        self.parseOnly = parseOnly 
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
                    a = pq(html)   
                    #items
                    items = a('nav.pagination-a').prev_all('ul li')
            
                    for item in items.items():
                        try:
                            yield self.common.parse_item(item)
                        except:
                            self.log('error in parse item %s' % url)         
                            continue
                    
                    self.log('parsed url %s' % url)      
                else:
                    self.log('request %s error' %url)         
            except:
                self.log( 'error in parse url %s' % url)         
                yield None    
        
        yield None
    
    '''
    process_image
    
    @author: chenzf
    '''    
    def process_data(self, data):
        if self.parseOnly == 1:
           return 
        self.common.process_data(data)    

class CWebParserHunterSingleUrl(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super(CWebParserSingleUrl, self).__init__(url)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.common = CWebParserHunterCommon(savePath, parseOnly)     
        self.parseOnly = parseOnly            
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
                    a = pq(html)   
                    #items
                    items = a('ul.gallery-a li')
    
                    for item in items.items():
                        try:
                            yield self.common.parse_item(item)
                        except:
                            self.log('error in parse item %s' % url)         
                            continue
                    self.log('parsed url %s' % url)     
                else:
                    self.log('request %s error' %url)         
                                
            except:
                self.log('error in parse url %s' % url)         
                yield None    
            
        yield None
    
    '''
    process_image
    
    @author: chenzf
    '''    
    def process_data(self, data):
        if self.parseOnly == 1:
           return 
        self.common.process_data(data)    
        
        
class CWebParserHunterDb(CWebParser):    
    def __init__(self, url, savePath, start, len, parseOnly):
#         super(CWebParserSingleUrl, self).__init__(url)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.common = CWebParserHunterCommon(savePath, parseOnly)     
        self.parseOnly = parseOnly   
        self.start = start
        self.len = len
                 
    '''
    parse_page
    
    @author: chenzf
    ''' 
    def parse_page(self):
        db_count = 0
        while True: 
            try:
                for item in self.common.get_db_item(self.start, self.len):
                    try:
                        url = item.get('url')
                        board = item.get('board')
                        discrib = item.get('discrib')
                        
                        b = pq(url)
                
                        art_site_info = b('#breadcrumbs li')
                        info_string = []
                        for it in art_site_info.items(): 
                            info_string.append(it.text())
                            
                        if len(info_string) >=3:
                            site, model, name  = info_string[0], info_string[1], info_string[2]
                        
                        video = None
                        video_item = b('video')
                        if video_item:
                            src = []
                
                            for src_item in video_item('source').items():
                                src.append(src_item.attr('src'))
                            video={
                                    'src': src,
                                    'poster':video_item.attr('poster')
                                    }  
                        else:                                
                            previews = b('ul.gallery-b  li')
                            stills = []
                            for preview in previews.items():
                                stills.append([ preview('a').attr('href'), preview('img').attr('src')])
                                
                        data = {    
                            'site'    :  site,
                            'name'    :  self.utils.format_name(name),  
                            'model'   :  self.utils.format_name(model),  
                            'discrib' :  self.utils.format_name(discrib),
                            'board'   :  board,
                            'url'     :  url,
                            'stills'  :  stills,      
                            'video'   :  video      
                            }        
                        db_count +=1
                        print('current db index %s' %db_count)
                        yield data            
                    except:
                        self.log('error in parse item %s' % url)         
                        continue
            except:
                self.log('error in parse url %s' % url)         
                yield None    
        
        yield None
    
    '''
    process_image
    
    @author: chenzf
    '''    
    def process_data(self, data):
        self.common.process_data(data)   