# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os,sys,vthread,re,json
from pyquery import PyQuery as pq
from win32comext.shell.shellcon import SE_ERR_NOASSOC
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,parentdir)

from Common.CWebParser import CParseType,CWebParser,CWebParserMultiUrl,CWebParserSingleUrl
from Common.CWebDataDbUtis import CWebDataDbUtis
from Common.CWebSpiderUtils import CWebSpiderUtils
from copy import deepcopy

class CWebParserHunterCommon(object):
    def __init__(self, webParser):
        self.webParser = webParser
#    
    def parse_item(self, item):   
        data = None     
        url = item('a').attr('href')
        discrib = item('a').attr('title')
        if not discrib:
            discrib = item('img').attr('alt')
        result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))

        if self.webParser.parseOnly == CParseType.Parse_Brief:     
            data = { 
                'url'     :  url,
                'discrib' :  self.webParser.utils.format_name(discrib),
                'board'   :  [result[0] if result and len(result) >= 2 else None,item('img').attr('src'), result[1] if result and len(result) >= 2 else None],
            }             
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
            stills = []
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
                for preview in previews.items():
                    stills.append([ preview('a').attr('href'), preview('img').attr('src')])
                    
            data = {    
                'site'    :  site,
                'name'    :  self.webParser.utils.format_name(name),  
                'model'   :  self.webParser.utils.format_name(model),  
                'discrib' :  self.webParser.utils.format_name(discrib),
                'board'   :  [result[0] if result and len(result) >= 2 else None,item('img').attr('src'), result[1] if result and len(result) >= 2 else None],
                'url'     :  url,
                'stills'  :  stills,      
                'video'   :  video      
                }        
                
        return data 
    
    
    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('url')
        board = item.get('board')
        discrib = item.get('discrib')
        html = self.webParser.utils.get_page(url)     
        if html:
            b = pq(html)
     
            art_site_info = b('#breadcrumbs li')
            info_string = []
            for it in art_site_info.items(): 
                info_string.append(it.text())
                
            if len(info_string) >=3:
                site, model, name  = info_string[0], info_string[1], info_string[2]
            
            video = None
            video_item = b('video')
            stills = []
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
                for preview in previews.items():
                    stills.append([ preview('a').attr('href'), preview('img').attr('src')])
                    
            data = {    
                'site'    :  site,
                'name'    :  self.webParser.utils.format_name(name),  
                'model'   :  self.webParser.utils.format_name(model),  
                'discrib' :  discrib,
                'board'   :  board,
                'url'     :  url,
                'stills'  :  stills,      
                'video'   :  video      
                }          

        return data             

    def process_data(self, data):
#         print(data)
        result = True
        if data.get('video'):
            sub_dir_name = "%s\\%s\\films\\%s %s" %(data.get('site'), data.get('model'), data.get('model'),data.get('name'))
        else:
            sub_dir_name = "%s\\%s\\galleries\\%s %s" %(data.get('site'), data.get('model'), data.get('model'),data.get('name'))
       
        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(dir_name + '\\..\\info.json', 'w') as f:    
            json.dump(data, f)
            
        boards = data.get('board')
        for board in boards:
            if board:
                result &=  self.webParser.utils.download_file(board,
                                        '%s\\%s' % (sub_dir_name, data.get('name')),
                                        headers={'Referer':data.get('url')}        
                                         )  

                break                     
        
        if data.get('video'):
            for src in data.get('video').get('src'): 
                result &=  self.webParser.utils.download_file(src,
                            '%s\\%s' % (sub_dir_name, data.get('name')),
                            headers={'Referer':data.get('url')}        
                             )    
                break
            
            result &= self.webParser.utils.download_file(data.get('video').get('poster'),
                            '%s\\%s' % (sub_dir_name, data.get('name')),
                            headers={'Referer':data.get('url')}        
                             ) 
            
        else:        
            stills = data.get('stills')
            for i, val in enumerate(stills, start=1): 
                for subVal in val:
                    if subVal:
                        result &= self.webParser.utils.download_file(subVal,
                                         '%s\\%s' % (sub_dir_name, str(i)),
                                         headers={'Referer':data.get('url')}        
                                 )   
                        break
        
        return result
        
        
class CWebParserHunterMultiUrl(CWebParserMultiUrl):    
    def __init__(self, url, start, end, savePath, parseOnly):
        super(CWebParserMultiUrl, self).__init__(url, start, end)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserHunterCommon(self)    
        self.dbUtils = CWebDataDbUtis('HegreHunter')

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
                        data = self.common.parse_item(item)                            
                        yield data
                    
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
        while True: 
            try:
                for item in self.dbUtils.get_db_item():
                    data = self.common.parse_detail_fr_brief(item)       
                    yield data                                
            except:
                self.log('error in parse url %s' % url)         
                yield None    
         
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
            self.dbUtils.switch_db_item(item)
            datatmp = deepcopy(data)
            self.dbUtils.insert_db_detail_item(datatmp)

class CWebParserHunterSingleUrl(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super(CWebParserSingleUrl, self).__init__(url)
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.parseOnly = CParseType(parseOnly)  
        self.common = CWebParserHunterCommon(self)    
        self.dbUtils = CWebDataDbUtis('HegreHunter')
        
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
                        data = self.common.parse_item(item)                            
                        yield data
                    
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
        while True: 
            try:
                for item in self.dbUtils.get_db_item():
                    data = self.common.parse_detail_fr_brief(item)       
                    yield data                                
            except:
                self.log('error in parse item')         
                yield None    
         
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
            self.dbUtils.switch_db_item(item)
            datatmp = deepcopy(data)
            self.dbUtils.insert_db_detail_item(datatmp)
         
class CWebParserHunterDb(CWebParser):    
    def __init__(self, savePath, parseOnly):
        self.savePath = savePath
        self.utils = CWebSpiderUtils(savePath)  
        self.parseOnly = parseOnly  
        self.common = CWebParserHunterCommon(self)    
        self.dbUtils = CWebDataDbUtis('HegreHunter')
                          
    '''
    parse_page
     
    @author: chenzf
    ''' 
    def parse_page(self):
        while True: 
            try:
                if self.parseOnly == 1:
                    for item in self.dbUtils.get_db_item():
                        try:
                            url = item.get('url')
                            board = item.get('board')
                            discrib = item.get('discrib')
                            html = self.utils.get_page(url)     
                            if html:
                                b = pq(html)
                         
                                art_site_info = b('#breadcrumbs li')
                                info_string = []
                                for it in art_site_info.items(): 
                                    info_string.append(it.text())
                                     
                                if len(info_string) >=3:
                                    site, model, name  = info_string[0], info_string[1], info_string[2]
                                 
                                video = None
                                stills = []
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
                                self.dbUtils.switch_db_item(item)
                                datatmp = deepcopy(data)
                                self.dbUtils.insert_db_detail_item(datatmp)
                                yield data
                                
                        except:
                            self.log('error in parse item %s' % url)         
                            continue
                else:
                    for item in self.dbUtils.get_db_detail_item():
                        data = deepcopy(item)
                        data.pop("_id")
                        yield data
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
        
        if self.common.process_data(data):
            self.dbUtils.switch_db_detail_item(data)