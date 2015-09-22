#!/usr/bin/env python
# encoding: utf-8

import os
import re

# fla dir
fla_dir = '/Users/lujian/Documents/mobile-art/剧情/表情'

# dst file
dst_file = 'result/expression_config.js'

# ccbi dir
ccbi_dir = '/Users/lujian/Documents/mobile-out/trunk/ccbi动画/B - 表情'

if __name__ == '__main__':
    # generate configs
    configs = []
    for _, _, files in os.walk(fla_dir):
        for file in files:
            m = re.match(r'^(\d+)_([^\.]+)\.fla$', file)
            if m:
                configs.append({
                    'id': int(m.groups()[0]),
                    'name': str(m.groups()[1])
                })

    # sort
    configs = sorted(configs, key=lambda config: config['id'])

    # write
    data = ''
    for config in configs:
        data += '{id: ' + str(config['id']) + ', name: "' + config['name'] + '"}, \n'
    file = open(dst_file, 'wb')
    file.write(data)

    # rename
    for root, _, files in os.walk(ccbi_dir):
        for file in files:
            m = re.match(r'.*_([^\.]+\.ccbi)', file)
            if m:
                file_name = m.groups()[0]
                os.rename(root + '/' + file, root + '/' + file_name)