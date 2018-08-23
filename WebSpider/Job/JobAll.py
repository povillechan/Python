# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import importlib
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
import re
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

if __name__ == '__main__':   
#     Job_list = ['Photos.Hegre_Art','Photos.Joymii','Photos.Met_Art','Photos.X_Art','Photos.Rylsky_Art','Photos.Watch_4_Beauty','Photos.Femjoy']
    pool = ProcessPoolExecutor()

    module_list = os.listdir('../Photos/')
    for module_name in module_list:
        if re.search('\.py$', module_name):
            pool.submit(getattr(importlib.import_module("%s.%s"%("Photos",module_name.split('.')[0])), "Job_Start"))
