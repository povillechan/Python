# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
from Common import Videos

work_url = 'https://www.metarthunter.com/archive'

def Job_Start(url = None):
    print(__file__, "start!")
    if url is None:
        url = work_url
#    total_page = PageCount.page_count(url)
    Videos.call_process('%s/%s' %(url,"page/{page}/"), 1, 78)
    
if __name__ == '__main__':   
    Job_Start()