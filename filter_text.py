#!/usr/bin/env python
# encoding: utf-8

# !/usr/bin/env python
# encoding: utf-8

import os
import re

src_file_path = 'dirty/dirty.txt'
dst_file_path = 'dirty/dirty.json'

if __name__ == '__main__':
    # read
    words = []
    file = open(src_file_path, "rb")
    lines = file.readlines()
    for line in lines:
        m = re.match(r'.\s*([^\|\s]*)\|?', line)
        if m:
            words.append(m.groups()[0])

    # data
    data = '[ \n'
    for word in words:
        data += '"' + word + '"'

        if words.index(word) != len(words) - 1:
            data += ', \n'
        else:
            data += '\n'
    data += '] \n'

    # write
    file = open(dst_file_path, "wb")
    file.write(data)