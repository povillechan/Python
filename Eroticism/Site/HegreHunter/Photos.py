# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import argparse,os,sys
import os,sys,vthread,re,json
from pyquery import PyQuery as pq
from win32comext.shell.shellcon import SE_ERR_NOASSOC
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,parentdir)

from Common.CWebParser import CParseType,CWebParser,CWebParserMultiUrl,CWebParserSingleUrl
from Common.CWebDataDbUtis import CWebDataDbUtis
from Common.CWebSpiderUtils import CWebSpiderUtils
from copy import deepcopy

parentdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parentdir)

# from CWebParserHunter import CWebParserHunterSingleUrl
# from CWebParserHunter import CWebParserHunterMultiUrl    
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
        super().__init__(url, start, end, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
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
                
                if self.dbUtils.get_db_url(url):
                    continue
                
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)   
                    #items
                    items = a('nav.pagination-a').prev_all('ul li')
            
                    for item in items.items():
                        data = self.common.parse_item(item)                            
                        yield data
                    
                    self.log('parsed url %s' % url)     
                    self.dbUtils.put_db_url(url)  
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

class CWebParserHunterSingleUrl(CWebParserSingleUrl):    
    def __init__(self, url, savePath, parseOnly):
        super().__init__(url, savePath)
        self.utils = CWebSpiderUtils(self.savePath)  
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
                                
                if self.dbUtils.get_db_url(url):
                    continue
                
                html = self.utils.get_page(url)     
                if html:
                    a = pq(html)   
                    #items
                    items = a('ul.gallery-a li')
                    
                    for item in items.items():
                        data = self.common.parse_item(item)                            
                        yield data
                    
                    self.log('parsed url %s' % url)     
                    self.dbUtils.put_db_url(url)      
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
    job_list = [
        ('S', 'https://www.alshunter.com'),
        ('S', 'https://www.centerfoldhunter.com'),
        ('S', 'https://www.domerotica.com'),
        ('S', 'https://www.drommhub.com'),
        ('S', 'https://www.eroticandbeauty.com'),
        ('S', 'https://www.erroticahunter.com'),
        ('S', 'https://www.mplhunter.com'),
        ('S', 'https://www.penthousehub.com'),
        ('S', 'https://www.rylskyhunter.com'),
        ('S', 'https://www.tlehunter.com'),
        ('S', 'https://www.w4bhub.com'),
        ('S', 'https://www.zemanihunter.com'),
        ('S', 'https://www.femangels.com/'),
        ('M', 'https://www.elitebabes.com/archive/page/{page}',  0, 503),
        ('M', 'https://www.femjoyhunter.com/archive/page/{page}', 1, 34),
        ('M', 'https://www.hegrehunter.com/archive/page/{page}', 1, 17),
        ('M', 'https://www.joymiihub.com/archive/page/{page}', 1, 8),
        ('M', 'https://www.jperotica.com/archive/page/{page}', 1, 25),
        ('M', 'https://www.metarthunter.com/archive/page/{page}', 1, 77),
        ('M', 'https://www.pmatehunter.com/archive/page/{page}', 1, 38),
        ('M', 'https://www.xarthunter.com/archive/page/{page}', 1, 9),
#             ('S', 'https://www.elitebabes.com/archive/page/98'),
#             ('S', 'https://www.elitebabes.com/archive/page/100'),
#             ('S', 'https://www.elitebabes.com/archive/page/103'),
#             ('S', 'https://www.elitebabes.com/archive/page/122'),
#             ('S', 'https://www.elitebabes.com/archive/page/130'),
#             ('S', 'https://www.elitebabes.com/archive/page/135'),
#             ('S', 'https://www.elitebabes.com/archive/page/155'),
#             ('S', 'https://www.elitebabes.com/archive/page/157'),
#             ('S', 'https://www.elitebabes.com/archive/page/164'),
#             ('S', 'https://www.elitebabes.com/archive/page/168'),
#             ('S', 'https://www.elitebabes.com/archive/page/179'),
#             ('S', 'https://www.elitebabes.com/archive/page/182'),
#             ('S', 'https://www.elitebabes.com/archive/page/183'),
#             ('S', 'https://www.elitebabes.com/archive/page/184'),
#             ('S', 'https://www.elitebabes.com/archive/page/188'),
#             ('S', 'https://www.elitebabes.com/archive/page/213'),
#             ('S', 'https://www.elitebabes.com/archive/page/214'),
#             ('S', 'https://www.elitebabes.com/archive/page/215'),
#             ('S', 'https://www.elitebabes.com/archive/page/217'),
#             ('S', 'https://www.elitebabes.com/archive/page/332'),
#             ('S', 'https://www.elitebabes.com/archive/page/335'),
#             ('S', 'https://www.elitebabes.com/archive/page/379'),
#             ('S', 'https://www.elitebabes.com/archive/page/387'),
#             ('S', 'https://www.elitebabes.com/archive/page/389'),
#             ('S', 'https://www.elitebabes.com/archive/page/400'),
#             ('S', 'https://www.elitebabes.com/archive/page/402'),
#             ('S', 'https://www.elitebabes.com/archive/page/6'),
#             ('S', 'https://www.elitebabes.com/archive/page/18'),
#             ('S', 'https://www.elitebabes.com/archive/page/80'),
#             ('S', 'https://www.elitebabes.com/archive/page/98'),
#             ('S', 'https://www.elitebabes.com/archive/page/272'),
#             ('S', 'https://www.elitebabes.com/archive/page/380'),
#             ('S', 'https://www.elitebabes.com/archive/page/393'),
#             ('S', 'https://www.elitebabes.com/archive/page/499'),
        ]
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default='Hunter\\{filePath}')
    parser.add_argument('-p', type=int, default='0')
    args = parser.parse_args()
    print(args)
    for job_item in job_list:
        if job_item[0] == 'S':
            job = CWebParserHunterSingleUrl(job_item[1], args.f, args.p)
        else:            
            job = CWebParserHunterMultiUrl(job_item[1], job_item[2], job_item[3], args.f, args.p)
        
        job.call_process()

    
if __name__ == '__main__':   
    Job_Start() 
