# -*- coding:utf-8 -*-
'''
Created on 2018年6月5日

@author: povil
'''
import re
with open("a.log", "rb") as f:
    for line in f.readlines():
        line = line.decode('utf8')
        if not re.match('^\s{0,}#', line):
            print(line)
