#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/6/16 8:06 PM

@author: IMYin

@File: SelectStrategy.py
"""

import tushare as ts
import os, sys, datetime

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

date_today = datetime.datetime.now().date()
today = date_today.strftime("%Y%m%d")
# basic data
basic = ts.get_stock_basics()
# market quotations
hq = ts.get_today_all()
# current stock price
hq["trade"] = hq.apply(lambda x: x.settlement if x.trade == 0 else x.trade, axis=1)
# 分别选取流通股本、总股本、每股公积金、每股收益
base_data = basic[['outstanding', 'totals', 'reservedPerShare', 'esp']]
# 选取股票代码、名称、当前价格、总市值、流通市值
hqdata = hq[['code', 'name', 'trade', 'mktcap', 'nmc']]

# 设置行情数据code为index列
hqdata = hqdata.set_index('code')

# 合并两个数据表
data = base_data.merge(hqdata, left_index=True, right_index=True)

# 选股条件
# 将总市值和流通市值换成亿元单位
data['mktcap'] = data['mktcap'] / 10000
data['nmc'] = data['nmc'] / 1000
# 设置过滤条件
# 每股公积金
res = data.reservedPerShare >= 5
# 流通股本 <= 3亿
out = data.outstanding <= 30000
# 每股收益　>= 5毛
eps = data.esp >= 0.5
# 总市值　< 100亿
mktcap = data.mktcap <= 100

# merge
allcrit = res & out & eps & mktcap
selected = data[allcrit]
print(selected)
archive_path = cons.FILE_ARCHIVE
if not os.path.isdir(archive_path):
    try:
        os.makedirs(archive_path)
    except:
        pass
data_path = os.path.join(archive_path, today + 'selected.csv')
selected.to_csv(data_path, encoding='utf-8',
                columns=['name', 'trade', 'reservedPerShare', 'outstanding', 'esp', 'mktcap', 'nmc'])
