#!/usr/bin/env python
# encoding: utf-8

import os
import re

# project_dir = os.path.dirname(os.path.realpath(__file__)) + '/../..'

# 复制当前文件夹下 所有后缀名相同的文件 到当前文件夹/temp文件夹下
source_path = '/Users/lujian/Downloads/3DRT'
dst_dir = 'CSEFTemp'

if __name__ == '__main__':
    if not os.path.exists(source_path + '/' + dst_dir):
        os.system('mkdir ' + source_path + '/' + dst_dir)

    for _, _, files in os.walk(source_path):
        for file in files:
            m = re.match(r'.*\.mb$', file)
            if m:
                os.system('cp -f ' + source_path + '/' + file + ' ' + source_path + '/' + dst_dir)