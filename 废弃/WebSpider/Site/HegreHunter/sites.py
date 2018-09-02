# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import argparse,os,sys

parentdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parentdir)

from CWebParserHunter import CWebParserHunterSingleUrl
from CWebParserHunter import CWebParserHunterMultiUrl    


def Job_Start():
    print(__file__, "start!")
    job_list = [
        ('S', 'https://www.alshunter.com'),
        ('S', 'https://www.centerfoldhunter.com'),
        ('S', 'https://www.domerotica.com'),
        ('S', 'https://www.drommhub.com'),
        ('S', 'https://www.eroticandbeauty.com'),
        ('S', 'https://www.erroticahunter.com'),
        ('S', 'https://www.mplhunter.com'),
        ('S', 'https://www.penthousehub.com'),
        ('S', 'https://www.rylskyhunter.com'),
        ('S', 'https://www.tlehunter.com'),
        ('S', 'https://www.w4bhub.com'),
        ('S', 'https://www.zemanihunter.com'),
        ('M', 'https://www.elitebabes.com/archive/page/{page}',  0, 501),
        ('M', 'https://www.femjoyhunter.com/archive/page/{page}', 1, 34),
        ('M', 'https://www.hegrehunter.com/archive/page/{page}', 1, 16),
        ('M', 'https://www.joymiihub.com/archive/page/{page}', 1, 9),
        ('M', 'https://www.jperotica.com/archive/page/{page}', 1, 25),
        ('M', 'https://www.metarthunter.com/archive/page/{page}', 1, 78),
        ('M', 'https://www.pmatehunter.com/archive/page/{page}', 1, 39),
        ('M', 'https://www.xarthunter.com/archive/page/{page}', 1, 10),
        ]
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-f', type=str, default='d:\\Pictures\\WebSpider\\Hunter\\{filePath}')
    parser.add_argument('-p', type=int, default='0')
    args = parser.parse_args()
    print(args)
    for job_item in job_list:
        if job_item[0] == 'S':
            job = CWebParserHunterSingleUrl(job_item[1], args.f, args.p)
        else:            
            job = CWebParserHunterMultiUrl(job_item[1], job_item[2], job_item[3], args.f, args.p)
        
        job.call_process()

    
if __name__ == '__main__':   
    Job_Start() 
