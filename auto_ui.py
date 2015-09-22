#!/usr/bin/env python
# encoding: utf-8

import os
import re

project_path = '/Users/lujian/Documents/ch-workspace/xxd-js-2'
result_file_name = 'auto_getset.js'


def print_error(e):
    print '\033[1;31;47m', e, '\033[0m'


def generate(file, root):
    data = '// uis created by buildUI \n'
    lines = file.readlines()
    for line in lines:
        m = re.search(r'name:\s"(.*)"', line)
        if m:
            property_name = m.groups()[0]
            data += "_ui_" + property_name + " : null,\n"
    file.close()

    result_file_path = root + '/' + result_file_name
    file = open(result_file_path, 'wb')
    file.write(data)
    file.close()

    print 'Generate success : (' + result_file_path + ')'
    return True


if __name__ == '__main__':
    result = False
    source_file_name = raw_input('source_file_name: ')
    for root, _, file_names in os.walk(project_path):
        for file_name in file_names:
            if file_name == source_file_name:
                print 'Generate start...'
                result = generate(open(root + '/' + file_name, 'rb'), root)

    if not result:
        print_error('can not find file: ' + source_file_name)
