#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 12/15/16 11:12 PM

@author: imyin

@File: quota_analysis
"""
import datetime
import os
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymysql
import talib as ta
import tushare as ts

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m-%d")
view_days = 14
textsize = 9


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
            sql = u"SELECT DISTINCT(publish_time),code,pdf_url " \
                  u"FROM {} WHERE publish_time LIKE '{}%' " \
                  u"AND content LIKE '%{}%'" \
                .format(cons.inter_table_name, yesterday, cons.UP)
            x = cursor.execute(sql)
            result = cursor.fetchmany(x)
            # codes = [item['code'] for item in result if cons.UP in item['content']]
            codes = {item['code']: item['pdf_url'] for item in result}
            # for k,v in codes.items():
            #     print k,v
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
    macd, macdsignal, macdhist = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return pd.DataFrame(
        {u'date': df.date[-view_days:], u'macd': macd[-view_days:], u'macdsignal': macdsignal[-view_days:],
         u'hist': macdhist[-view_days:] / 2})


def get_rsi_info(df):
    """
    calculate rsi quotation.
    :param df:
    :return: rsi
    """
    close = df[u'close'].values
    rsi = ta.RSI(close, timeperiod=12)
    return pd.DataFrame({u'date': df.date[-view_days:], u'rsi': rsi[-view_days:]})


def plot_quota(code, macd, rsi):
    left, width = 0.1, 0.8
    rect1 = [left, 0.35, width, 0.45]
    rect2 = [left, 0.15, width, 0.2]

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax1 = fig.add_axes(rect1, axisbg=axescolor)  # left, bottom, width, height
    ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)

    fillcolor = 'darkgoldenrod'

    # plot macd quotation.
    x = np.arange(len(macd))
    date = np.array([datetime.datetime.strptime(item, '%Y-%m-%d') for item in macd[u'date']])
    ax1.grid(True)
    ax1.plot(date, macd[u'macd'].values, 'r-')
    ax1.plot(date, macd[u'macdsignal'], 'k-')
    ax1.fill_between(date, macd[u'hist'], 0, facecolor=fillcolor, edgecolor=fillcolor)
    ax1.text(0.025, 0.95, u'MACD(12,26,9)', va=u'top', transform=ax1.transAxes, fontsize=textsize)
    ax1.set_title(u"{}'s quotaition".format(code))
    # ax1.legend(loc='best')

    # plot rsi quotation.
    rsi = rsi[u'rsi']
    ax2.grid(True)
    ax2.plot(date, rsi, color=fillcolor)
    ax2.axhline(70, color=fillcolor)
    ax2.axhline(30, color=fillcolor)
    ax2.fill_between(date, rsi, 70, where=(rsi >= 70), facecolor=fillcolor, edgecolor=fillcolor)
    ax2.fill_between(date, rsi, 30, where=(rsi <= 30), facecolor=fillcolor, edgecolor=fillcolor)
    ax2.set_ylim(0, 100)
    ax2.set_yticks([30, 70])
    ax2.text(0.025, 0.95, u'RSI(12)', va=u'top', transform=ax2.transAxes, fontsize=textsize)

    # turn off upper axis tick labels, rotate the lower ones, etc
    for ax in ax1, ax2:
        if ax != ax2:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            for label in ax.get_xticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment('right')

                ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    plt.savefig(cons.MACD_PLOT_RESULT + u'/' + code + u'.png', format=u'png')


for code, pdf in get_inter_codes().items():
    df = trade_data(code)
    plot_quota(code, get_macd_info(df), get_rsi_info(df))
