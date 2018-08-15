# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from Common import CWebParser

def Job_Start():
    print(__file__, "start!")
    job = CWebParser('D:\\Temp\\1\\', 'http://www.cnblogs.com/yuanchenqi/articles/8719520.html', ['#post_next_prev > a:nth-child(2)','#post_next_prev > a:nth-child(5)'])
    job.run()
    
if __name__ == '__main__':   
    Job_Start() 