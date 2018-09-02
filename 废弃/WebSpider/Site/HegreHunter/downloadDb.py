# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import argparse,os,sys

parentdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parentdir)

from CWebParserHunter import CWebParserHunterDb
    
def Job_Start():
    print(__file__, "start!")
    url = 'https://www.zemanihunter.com'
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default = 'd:\\Pictures\\WebSpider\\Hunter\\{filePath}')
    parser.add_argument('-p', type=int, default = '0')
    parser.add_argument('-s', type=int, default = '0')
    parser.add_argument('-l', type=int, default = '100') 
    args = parser.parse_args()
    print(args)

    job = CWebParserHunterDb(url, args.f, args.s, args.l, args.p)
    job.call_process()
    
if __name__ == '__main__':   
    Job_Start() 
