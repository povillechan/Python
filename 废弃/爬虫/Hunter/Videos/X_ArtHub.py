# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from Common import Videos_Single_XArt_Hub
work_url = 'https://www.xarthub.com/'

def Job_Start(url = None):
    print(__file__, "start!")
    if url is None:
        url = work_url
#    total_page = PageCount.page_count(url)
    Videos_Single_XArt_Hub.call_process(url)
    
if __name__ == '__main__':   
    Job_Start()