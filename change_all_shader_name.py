__author__ = 'lujian'

import os
import re

source_path = "/Users/lujian/Documents/RO/client-refactory/Develop/Assets/DevelopTest/Lu/mu-resources/Shader"
prefix = "Lu/MU"

if __name__ == "__main__":
    for d, _, fs in os.walk(source_path):
        for f in fs:
            m = re.match('.+\.shader$', f)
            if not m:
                continue
            file_path = os.path.join(d, f)
            file = open(file_path, "rb")
            lines = file.readlines()

            data = ""
            for line in lines:
                # Shader "TerrainForMobile/3TexturesDiffuseSimple" {
                m = re.match('.*Shader\s+\"(\S+)\"', line)
                if m:
                    line = line.replace(m.groups()[0], prefix + m.groups()[0].replace(prefix, ""))
                data += line

            file.close()

            file = open(file_path, "wb")
            file.write(data)
            file.close()
