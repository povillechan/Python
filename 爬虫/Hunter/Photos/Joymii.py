# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
from Common import Photos
from Common import Photos_Single
from Common import PageCount

work_url = 'https://www.joymiihub.com/archive'

def Job_Start(url = None):
    print(__file__, "start!")
    if url is None:
        url = work_url
#    total_page = PageCount.page_count(url)
    Photos.call_process('%s/%s' %(url,"page/{page}/"), 1, 9)
    
if __name__ == '__main__':   
    Job_Start()