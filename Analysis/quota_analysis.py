#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 12/15/16 11:12 PM

@author: imyin

@File: quota_analysis
"""
import tushare as ts
import talib as tl

def trade_data(code):
    return ts.get_k_data(code)

def gold_line(df):
    close = df[u'close']
    macd, macdsignal, macdhist = tl.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
