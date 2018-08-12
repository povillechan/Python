# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import vthread

class CWebParser(object):
    
    def __init__(self, url, start=None, end=None):
        self.url = url
        self.start = start
        self.end = end
    '''
    parse_page
    
    @author: chenzf
    ''' 
    def parse_page(self, urlsGen):
        return None
    
    '''
    process_image
    
    @author: chenzf
    '''    
    @vthread.pool(8)  
    def process_data(self, data):
        pass
    
    '''
    process
    
    @author: chenzf
    '''     
    def process(self):
        try:
            datas = self.parse_page()  
            while True:
                data = next(datas)
                if data:
                    self.process_data(data)
                else:
                    break
        except:
            print('error occured in parse image')
    
               
    def urls_genarator(self):
        return None
        
    def call_process(self):
        self.process()