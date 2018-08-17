# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os,sys
parentdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,parentdir)

from CWebParser import CWebParser

class CWebParserMultiUrl(CWebParser):    
    def __init__(self, url, start, end):
        self.url = url
        self.start = start
        self.end = end
               
    def urls_genarator(self):
        for i in range(self.start, self.end+1):
            yield self.url.format(page=i)
        yield None
        

class CWebParserSingleUrl(CWebParser):    
    def __init__(self, url):
        self.url = url
        self.start = None
        self.end = None    
               
    def urls_genarator(self):
        yield self.url
        return None