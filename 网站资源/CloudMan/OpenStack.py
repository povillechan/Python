# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from Common import CWebParser
import re

class CWebParserSite(CWebParser):
    
    def __init__(self, savePath, startUrl, nextUrlCss):
        self.savePath = savePath
        self.setUp()
        self.setRule(startUrl, nextUrlCss)
        self.searchedList = []

    def getSavePageName(self, title):
        result = re.search('.*?(\uff08\d+\uff09)' ,title, re.S)
        if result:
            pageName = result.group(1)+'-' + title.replace(result.group(1), "")
        else:
            pageName = title
        pageName = pageName.replace('\"','_').replace(':','_').replace(',','_').replace('/','_').replace('\u200B','')
        return pageName
     
def Job_Start():
    print(__file__, "start!")
    job = CWebParserSite('D:\\Temp\\2\\', 'https://www.cnblogs.com/CloudMan6/p/6241589.html', ['#post_next_prev > a'])
    job.run()
    
if __name__ == '__main__':   
    Job_Start() 