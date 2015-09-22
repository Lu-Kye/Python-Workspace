#!/usr/bin/env python
# encoding: utf-8

# sourceFileName = "/Users/lujian/Documents/python-workspace/1111.csv"
# targetFileName = "/Users/lujian/Documents/python-workspace/1111_Encoded.csv"

import re
import os

BLOCKSIZE = 1048576


def change_encode(source, target):
    source = open(source)
    target = open(target, "w")
    target.write(unicode(source.read(), 'iso-8859-1').encode('utf-8'))


if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))
    des_path = path + '/Temp'
    if not os.path.isdir(des_path):
        os.mkdir(des_path)

    for _, _, files in os.walk(path):
        for file in files:
            m = re.match(r'.*\.csv$', file)
            if m:
                change_encode(path + '/' + file, des_path + '/' + file)