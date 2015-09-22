#!/usr/bin/env python
# encoding: utf-8

import os
import re

source_path = '/Users/lujian/Documents/RO/client-refactory/Develop/Assets/Resources/Script/Net/Protobuf'

if __name__ == '__main__':
    for dir, _, files in os.walk(source_path):
        for file in files:
            m = re.match(r'.*\.lua$', file)
            if m:
                file = file.replace('.lua', '')
                print(file)
                print(dir)
                os.renames(dir + '/' + file + '.lua', dir + '/' + file + '.txt')