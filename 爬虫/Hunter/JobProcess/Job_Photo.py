# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import importlib
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from Photos import Hegre_Art, Joymii, Met_Art, X_Art

if __name__ == '__main__':   
    Job_list = ['Photos.Hegre_Art','Photos.Joymii','Photos.Met_Art','Photos.X_Art','Photos.Rylsky_Art','Photos.Watch_4_Beauty','Photos.Femjoy']
    pool = ProcessPoolExecutor()
        
#     pool = Pool(3)   
 #    getattr(importlib.import_module("Photos.Hegre_Art"), "Job_Start")()
    for job in Job_list:
        pool.submit(getattr(importlib.import_module(job), "Job_Start"))
#         pool.apply_async(main,(item,))
#     pool.submit(Joymii.Job_Start())
#     pool.submit(Met_Art.Job_Start())
#     pool.submit(X_Art.Job_Start())
# 
#     pool.map(main,[i  for i in range(0,2)])
# 
#     pool.close()
#     pool.join()