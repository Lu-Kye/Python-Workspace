#!/usr/bin/env python
# encoding: utf-8

# !/usr/bin/env python
# encoding: utf-8

import os
import re

project_path = '/Users/lujian/Documents/ch-workspace/xxd-js-2'


def print_error(e):
    print '\033[1;31;47m', e, '\033[0m'


def generate(file_path):
    file = open(file_path, 'rb')
    lines = file.readlines()
    data = ''
    for line in lines:
        m = re.match(r'//\s*(\S+)\s[\S]+\s\((.+)\)', line)
        if m:
            field = m.groups()[0]
            note = m.groups()[1]
            data += '\t_' + field + ' : ' + 'null, // ' + note + '\n'
        else:
            data += line

    data += "\n"

    for line in lines:
        m = re.match(r'//\s*(\S+)\s[\S]+\s\((.+)\)', line)
        if m:
            field = m.groups()[0]
            note = m.groups()[1]
            data += '\t' + field + ' : ' + 'data["' + field + '"], // ' + note + '\n'
        else:
            data += line

    return data


if __name__ == '__main__':
    result = False
    source_file_name = raw_input('source_file_name: ')
    for root, _, file_names in os.walk(project_path):
        for file_name in file_names:
            if file_name == source_file_name:
                result = generate(root + '/' + file_name)
                print result

    if not result:
        print_error('can not find file: ' + source_file_name)
