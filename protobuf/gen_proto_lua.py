#!/usr/bin/env python
# encoding: utf-8

import os
import re

file_path = os.path.dirname(__file__)
protos_path = file_path + "/client"
luas_path = protos_path + "/lua"

if __name__ == "__main__":
    print("start gen lua...")

    os.system("rm -rf " + luas_path)
    os.system("mkdir -p " + luas_path)

    for p, _, fs in os.walk(protos_path):
        for f in fs:
            m = re.match(r'.*\.proto', f)
            if m:
                os.system("cd " + p)
                os.system("protoc --lua_out=" + luas_path + " " + f)

    for p, _, fs in os.walk(luas_path):
        for f in fs:
            m = re.match(r'.*\.lua', f)
            if m:
                fname = re.sub(r'\.lua', "", f)
                os.renames(p + "/" + fname + ".lua", p + "/" + fname + ".txt")

                f = open(p + "/" + fname + ".txt", "rb")
                data = ""
                for line in f.readlines():
                    line = line.replace('local protobuf = require "protobuf"', 'local protobuf = protobuf')
                    data += line
                    # m = re.match(r'local\s+\S+\s*=\s*require\(')

                f.close()

                f = open(p + "/" + fname + ".txt", "wb")
                f.write(data)
                f.close()