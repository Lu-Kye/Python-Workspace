#!/usr/bin/env python
# encoding: utf-8

import os
import re

file_path = os.path.dirname(__file__)
protos_path = file_path + ""
ignore_path = file_path + "/" + "server"
command = "xCmd.proto"
command_path = file_path + "/"
include = file_path + "/Proto_Include.txt"


class Command:
    def __init__(self, file, file_path):
        self.file = file
        self.file_path = file_path
        self.name = re.sub(r'\.proto', "", file)
        self.lua_name = self.name + "_pb"
        self.enums = {}
        self.parse()

    def parse(self):
        f = open(self.file_path + "/" + self.file, "rb")
        lines = f.readlines()

        cur_enum = None
        cur_enum_content = ""
        start_num = 0
        close_num = 0

        enums = []

        for line in lines:
            # message_names = re.findall(r'.*message\s+(\S+)', str)
            # cmds = re.findall(r'cmd\s*=\s*\d+\s*\[\s*default\s*=\s*(\S+)\s*\]', str)
            # params = re.findall(r'param\s*=\s*\d+\s*\[\s*default\s*=\s*(\S+)\s*\]', str)

            m = re.match(r'.*enum\s+(\S+)', line)
            if m and cur_enum is None:
                cur_enum = m.groups()[0]

            if cur_enum is not None:
                cur_enum_content += line
                m = re.match(r'.*\{.*', line)
                if m:
                    start_num += 1
                m = re.match(r'.*\}.*', line)
                if m:
                    close_num += 1

                if start_num == close_num and start_num != 0 and close_num != 0:
                    enums.append({
                        "name": cur_enum,
                        "content": cur_enum_content
                    })

                    cur_enum = None
                    cur_enum_content = ""
                    start_num = 0
                    close_num = 0

        for enum in enums:
            self.enums[enum["name"]] = {}
            content = enum["content"]
            ms = re.findall(r'(\S+)\s*=\s*(\d+)', content)
            if ms:
                for m in ms:
                    self.enums[enum["name"]][m[0]] = m[1]

    def get_value(self, enum_name, value_name):
        return self.enums[enum_name][value_name]


class Proto:
    def __init__(self, file, file_path):
        self.file = file
        self.file_path = file_path
        self.name = re.sub(r'\.proto', "", file)
        self.lua_name = self.name + "_pb"
        self.messages = []
        self.parse()

    def parse(self):
        f = open(self.file_path + "/" + self.file, "rb")
        lines = f.readlines()

        cur_message = None
        cur_message_content = ""
        start_num = 0
        close_num = 0

        messages = []

        for line in lines:
            # message_names = re.findall(r'.*message\s+(\S+)', str)
            # cmds = re.findall(r'cmd\s*=\s*\d+\s*\[\s*default\s*=\s*(\S+)\s*\]', str)
            # params = re.findall(r'param\s*=\s*\d+\s*\[\s*default\s*=\s*(\S+)\s*\]', str)

            m = re.match(r'.*message\s+(\S+)', line)
            if m and cur_message is None:
                cur_message = m.groups()[0]

            if cur_message is not None:
                cur_message_content += line
                m = re.match(r'.*\{.*', line)
                if m:
                    start_num += 1
                m = re.match(r'.*\}.*', line)
                if m:
                    close_num += 1

                if start_num == close_num and start_num != 0 and close_num != 0:
                    messages.append({
                        "name": cur_message,
                        "content": cur_message_content
                    })

                    cur_message = None
                    cur_message_content = ""
                    start_num = 0
                    close_num = 0

        for message in messages:
            content = message["content"]
            m0 = re.findall(r'(\S+)\s+cmd\s*=\s*\d+\s*\[\s*default\s*=\s*\S+\s*\]', content)
            m1 = re.findall(r'cmd\s*=\s*\d+\s*\[\s*default\s*=\s*(\S+)\s*\]', content)
            m2 = re.findall(r'param\s*=\s*\d+\s*\[\s*default\s*=\s*(\S+)\s*\]', content)
            if m0 and m1 and m2:
                if len(m0) > 1 or len(m1) > 1 or len(m2) > 1:
                    raise NameError(self.file + " " + message["name"] + " has more than one Cmd or Param!!!")

                self.messages.append({
                    "name": message["name"],
                    "command": str(m0[0]),
                    "cmd": str(m1[0]),
                    "param": str(m2[0])
                })


if __name__ == "__main__":
    print("start generate...")

    # generate command
    cmd = Command(command, command_path)

    # generate protos
    protos = []
    for p, _, fs in os.walk(protos_path):
        try:
            p.index(ignore_path)
            continue
        except:            
            for f in fs:
                m = re.match(r'.*\.proto', f)
                if not m or f == command:
                    continue

                proto = Proto(f, p)
                protos.append(proto)


    # data
    data = 'autoImport("' + cmd.lua_name + '") \n'
    # import
    for proto in protos:
        data += 'autoImport("' + proto.lua_name + '") \n'

    # get cmds
    proto_cmds = {}
    for proto in protos:
        proto_name = proto.lua_name
        messages = proto.messages
        for message in messages:
            msg_name = message["name"]
            msg_cmd = cmd.get_value(message["command"], message["cmd"])
            msg_param = message["param"]
            try:
                proto_cmds[msg_cmd]
            except:
                proto_cmds[msg_cmd] = {}
            proto_cmds[msg_cmd][msg_param] = proto_name + "." + msg_name


    # proto config
    data += "Proto_Include = { \n"
    for cmd_value, params in proto_cmds.items():
        data += "\t[" + cmd_value + "]" + " = {"
        for param_value, message in params.items():
            data += "[" + param_value + "]" + " = " + message + ","
        data += "}, \n"
    data += "} \n"

    # write to file
    f = open(include, "wb")
    f.write(data)
    f.close()

    print("generate success...")