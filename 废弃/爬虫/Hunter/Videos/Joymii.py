# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from Common import Videos
work_url = 'https://www.joymiihub.com/archive'

def Job_Start(url = None):
    print(__file__, "start!")
    if url is None:
        url = work_url
#    total_page = PageCount.page_count(url)
    Videos.call_process('%s/%s' %(url,"page/{page}/"), 1, 9)
    
if __name__ == '__main__':   
    Job_Start()