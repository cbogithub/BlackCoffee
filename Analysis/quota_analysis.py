#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 12/15/16 11:12 PM

@author: imyin

@File: quota_analysis
"""
import os
import sys

import pymysql
import talib as tl
import tushare as ts
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons


def conn_mysql():
    """
    To connect the mysql.
    Attentions: charset is a important parameter.

    :return: connection
    """
    connection = pymysql.connect(host=cons.mysql_host,
                                 user=cons.mysql_user,
                                 password=cons.mysql_passwd,
                                 db=cons.stock_db,
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def get_inter_codes():
    connection = conn_mysql()
    try:
        with connection.cursor() as cursor:
            sql = u"SELECT code, content FROM {}".format(cons.inter_table_name)
            x = cursor.execute(sql)
            result = cursor.fetchmany(x)
            codes = [item['code'] for item in result if cons.UP in item['content']]
            # print len(codes)
    finally:
        connection.close()
        return codes


# def get_announ_codes():
#     connection = conn_mysql()
#     try:
#         with connection.cursor() as cursor:
#             sql = u"SELECT code, content FROM {}".format(cons.announ_table_name)
#             x = cursor.execute(sql)
#             result = cursor.fetchmany(x)
#             codes = [item['code'] for item in result if cons.UP in item['content']]
#             # print len(codes)
#     finally:
#         connection.close()
#         return codes


def trade_data(code):
    return ts.get_k_data(code)


def get_macd_info(df):
    """
    macd =  EMA(12days) - EMA(26days)   red line
    macdsignal = EMA(9days) of MACD     blue line
    macdhist = MACD - MACD signal       hist
    :param df:
    :return: macd, macdsignal, macdhist
    """
    close = df[u'close'].values
    high = df[u'high'].values
    low = df[u'low'].values
    close = (close + high + low) / 3
    macd, macdsignal, macdhist = tl.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return pd.DataFrame({u'macd': macd[-7:], u'macdsignal': macdsignal[-7:], u'hist': macdhist[-7:] / 2})


def plot_macd(code, macd_seven):
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    x = np.arange(len(macd_seven))
    ax.grid(True)
    ax.plot(x, macd_seven[u'macd'].values, 'r-', label=u'macd')
    ax.plot(x, macd_seven[u'macdsignal'], 'k-', label=u'macdsignal')
    ax.legend(loc='best')
    plt.savefig(cons.MACD_PLOT_RESULT + u'/' + code + u'.png', format='png')


for item in get_inter_codes():
    df = trade_data(item)
    plot_macd(item, get_macd_info(df))
