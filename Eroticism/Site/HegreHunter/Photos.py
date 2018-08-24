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
        ('M', 'https://www.joymiihub.com/archive/page/{page}', 1, 8),
        ('M', 'https://www.jperotica.com/archive/page/{page}', 1, 25),
        ('M', 'https://www.metarthunter.com/archive/page/{page}', 1, 77),
        ('M', 'https://www.pmatehunter.com/archive/page/{page}', 1, 38),
        ('M', 'https://www.xarthunter.com/archive/page/{page}', 1, 9),
#             ('S', 'https://www.elitebabes.com/archive/page/98'),
#             ('S', 'https://www.elitebabes.com/archive/page/100'),
#             ('S', 'https://www.elitebabes.com/archive/page/103'),
#             ('S', 'https://www.elitebabes.com/archive/page/122'),
#             ('S', 'https://www.elitebabes.com/archive/page/130'),
#             ('S', 'https://www.elitebabes.com/archive/page/135'),
#             ('S', 'https://www.elitebabes.com/archive/page/155'),
#             ('S', 'https://www.elitebabes.com/archive/page/157'),
#             ('S', 'https://www.elitebabes.com/archive/page/164'),
#             ('S', 'https://www.elitebabes.com/archive/page/168'),
#             ('S', 'https://www.elitebabes.com/archive/page/179'),
#             ('S', 'https://www.elitebabes.com/archive/page/182'),
#             ('S', 'https://www.elitebabes.com/archive/page/183'),
#             ('S', 'https://www.elitebabes.com/archive/page/184'),
#             ('S', 'https://www.elitebabes.com/archive/page/188'),
#             ('S', 'https://www.elitebabes.com/archive/page/213'),
#             ('S', 'https://www.elitebabes.com/archive/page/214'),
#             ('S', 'https://www.elitebabes.com/archive/page/215'),
#             ('S', 'https://www.elitebabes.com/archive/page/217'),
#             ('S', 'https://www.elitebabes.com/archive/page/332'),
#             ('S', 'https://www.elitebabes.com/archive/page/335'),
#             ('S', 'https://www.elitebabes.com/archive/page/379'),
#             ('S', 'https://www.elitebabes.com/archive/page/387'),
#             ('S', 'https://www.elitebabes.com/archive/page/389'),
#             ('S', 'https://www.elitebabes.com/archive/page/400'),
#             ('S', 'https://www.elitebabes.com/archive/page/402'),
#             ('S', 'https://www.elitebabes.com/archive/page/6'),
#             ('S', 'https://www.elitebabes.com/archive/page/18'),
#             ('S', 'https://www.elitebabes.com/archive/page/80'),
#             ('S', 'https://www.elitebabes.com/archive/page/98'),
#             ('S', 'https://www.elitebabes.com/archive/page/272'),
#             ('S', 'https://www.elitebabes.com/archive/page/380'),
#             ('S', 'https://www.elitebabes.com/archive/page/393'),
#             ('S', 'https://www.elitebabes.com/archive/page/499'),
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
