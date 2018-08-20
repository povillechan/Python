# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import argparse,os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from CWebParserHunter import CWebParserHunterMultiUrl
    
def Job_Start():
    print(__file__, "start!")
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-s', type=int, default = 1)
    parser.add_argument('-e', type=int, default= 16)
    parser.add_argument('-f', type=str, default= 'd:\\Pictures\\WebSpider\\Hunter\\{filePath}')
    args = parser.parse_args()
    print(args)

    job = CWebParserHunterMultiUrl('https://www.hegrehunter.com/archive/page/{page}', args.s, args.e, args.f)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
