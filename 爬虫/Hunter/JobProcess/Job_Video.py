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

# from Video import Hegre_Art, Joymii, Met_Art, X_Art

if __name__ == '__main__':   
    Job_list = ['Videos.Hegre_Art','Videos.Joymii','Videos.Met_Art','Videos.X_Art','Videos.Rylsky_Art','Videos.Watch_4_Beauty','Videos.Femjoy']
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