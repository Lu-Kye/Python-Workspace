#!/usr/bin/env python
# encoding: utf-8

source_config = '''
nickname text16 (主角昵称)
town_id int16 (主角当前城镇)
role_id int8 (主角模板)
role_lv int16 (主角等级)
role_exp int64 (主角经验)
vip_level int16 (VIP等级)
ingot int64 (元宝)
coins int64 (铜钱)
heart_num int16 (玩家爱心数)
physical int16 (玩家体力值)
physical_buy_count int8 (今日体力已购次数)
get_heart_count int8 (今日领取爱心次数)
coins_buy_count int16 (今日铜钱购买次数)
batch_bought_coins int16 (今日铜钱购买次数)
func_key int16 (玩家当前的功能权值)
played_key int16 (玩家当前已播放开启功能的权值)
town_lock int32 (当前的城镇权值)
mission_key int32 (拥有的区域钥匙数)
mission_max_order int8 (已开启区域的最大序号)
mission_level_max_lock int32 (已开启的关卡最大权值)
hard_level_lock int32 (已开启的难度关卡最大权值)
quest_id int16 (任务ID)
quest_state int8 (任务状态)
'''

import re
import sys

dst_file = 'result/' + re.search(r'([^/]*)\.', sys.argv[0]).groups()[0]


def upper_id(pname):
    pname = pname.title().replace('Id', 'ID').replace('_', '')
    return pname[0].lower() + pname[1:len(pname)]


if __name__ == '__main__':
    data = ''
    lines = source_config.split('\n')
    for line in lines:
        m = re.match(r'(\S*)', line)
        if m:
            pname = m.groups()[0]

            if len(pname) == 0:
                continue

            upper_pname = upper_id(pname)
            set_fname = 'set' + upper_pname[0].upper() + upper_pname[1:len(upper_pname)]
            get_fname = upper_pname

            # set
            data += set_fname + ' : function (value) { \n'
            data += '\tthis._info["' + pname + '"] = value; \n'
            data += '}, \n'

            # get
            data += get_fname + ' : function () { \n'
            data += '\treturn this._info["' + pname + '"]; \n'
            data += '}, \n'

    # write
    file = open(dst_file, 'wb')
    file.write(data)