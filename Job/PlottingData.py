#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 12/13/16 11:27 PM

@author: imyin

@File: PlottingData
"""
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import talib as tl
import tushare as ts

INTERPRETATION_PATH = os.path.dirname(os.getcwd()) + u'/Scrapy'
sys.path.append(INTERPRETATION_PATH)
from ScrapyInterpretation import ScrapyInterpretation as si

code_lst = si.worth_data()


def trade_data(code):
    return ts.get_k_data(code)


def macd_data(df):
    if len(df) > 100:
        close = df.close.values
        macd, macdsignal, macdhist = tl.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return macd, macdsignal, macdhist


def bbands(df):
    if len(df) > 100:
        close = df.close.values
        upperband, middleband, lowerband = tl.BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    return upperband, middleband, lowerband


def plot_macd(df):
    macd, macdsignal, macdhist = macd_data(df)
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    x = np.arange(len(df))
    ax.grid(True)
    # ax.plot(x, df['close'], '.-', label=u'close')
    # ax.hist(macd)
    ax.plot(x, macdsignal, 'r-', label=u'macdsignal')
    ax.plot(x, macdhist, 'k-', label=u'macdhist')
    ax.legend(loc='best')
    ax.set_xlabel(str(df[u'date'][:].year))
    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.show()


def plot_bbands(df):
    df = df.head(40)
    upperband, middleband, lowerband = bbands(df)
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    x = np.arange(50)
    ax.grid(True)
    ax.plot(x, df['close'], '.-', label=u'close')
    ax.plot(x, lowerband, '.--')
    ax.plot(x, upperband, '.--')
    ax.plot(x, middleband, '^-')
    ax.legend(loc='best')
    fig.autofmt_xdate()
    plt.show()


def format_date(x, data, pos=None):
    this_ind = np.clip(int(x + 0.5), 0, len(data) - 1)
    return data.date[this_ind].strftime('%Y-%m-%d')
