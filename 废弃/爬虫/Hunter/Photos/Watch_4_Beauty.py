# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from Common import Photos_Single

work_url = 'https://www.w4bhub.com/'

def Job_Start(url = None):
    print(__file__, "start!")
    if url is None:
        url = work_url

    Photos_Single.call_process(url)
    
if __name__ == '__main__':   
    Job_Start()