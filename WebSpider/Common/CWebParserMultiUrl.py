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
        for i in range(self.start, self.end):
            yield self.url.format(page=i)
        yield None