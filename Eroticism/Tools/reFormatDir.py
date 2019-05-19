# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''

import os
import sys


def isdir(path):
    result = False
    for dirpath, dirnames, filenames in os.walk(path):
        # print(dirpath.replace(sys.argv[1], ""))
        if path == dirpath:
            continue
        result = True

    return result


def format_name(name):
    name = name.strip()
    patterns = [('\"', '_'),
                (',', '_'),
                (':', '_'),
                ('!', '_'),
                ('?', '_'),
                ('/', '_'),
                ('|', '_'),
                ('#', '_'),
                ('[', '_'),
                (']', '_'),
                ('\r', '_'),
                ('\n', '_'),
                ('*', '_'),
                ('.', '_'),
                ]
    for pattern in patterns:
        name = name.replace(pattern[0], pattern[1])
    return name


if len(sys.argv) >= 2 and sys.argv[1] != "":
    for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
        # print(dirpath, isdir(dirpath))
        if not isdir(dirpath):
            oldpath = os.path.basename(dirpath)
            newpath = format_name(oldpath)
            if oldpath != newpath:
                print("old:", oldpath)
                print("new:", newpath)
                dirname = os.path.dirname(dirpath)
                os.rename(os.path.join(dirname, oldpath), os.path.join(dirname, newpath))
