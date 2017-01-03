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
            sql = (u"SELECT DISTINCT(publish_time),code,pdf_url "
                   u"FROM {} WHERE publish_time LIKE '{}%' "
                   u"AND content LIKE '%{}%'"
                   .format(cons.inter_table_name, yesterday, cons.UP))
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


def get_close_data(df):
    """
    close price.
    :param df:
    :return:
    """
    close = df[u'close'].values
    high = df[u'high'].values
    low = df[u'low'].values
    close = (close + high + low) / 3
    return close


def get_macd_info(df):
    """
    macd =  EMA(12days) - EMA(26days)   red line
    macdsignal = EMA(9days) of MACD     blue line
    macdhist = MACD - MACD signal       hist
    :param df:
    :return: macd, macdsignal, macdhist
    """
    close = get_close_data(df)
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
    close = get_close_data(df)
    rsi = ta.RSI(close, timeperiod=12)
    return pd.DataFrame({u'rsi': rsi[-view_days:]})


def get_bbands_info(df):
    """
    calculate bbands quotation.
    :param df:
    :return: close, upperband, middleband, lowerband
    """
    close = get_close_data(df)
    upperband, middleband, lowerband = ta.BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    return pd.DataFrame({u'close': df.close[-view_days:],
                         u'upperband': upperband[-view_days:],
                         u'middleband': middleband[-view_days:],
                         u'lowerband': lowerband[-view_days:]})


def plot_quota(code, macd, rsi, bbands):
    left, width = 0.1, 0.8

    rect3 = [left, 0.471, width, 0.479]
    rect1 = [left, 0.235, width, 0.240]
    rect2 = [left, 0.11, width, 0.12]

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax1 = fig.add_axes(rect1, axisbg=axescolor)  # left, bottom, width, height
    ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)
    ax3 = fig.add_axes(rect3, axisbg=axescolor, sharex=ax1)

    fillcolor = 'darkgoldenrod'

    # plot macd quotation.
    macds = macd[u'macd']
    macdsignal = macd[u'macdsignal']
    hist = macd[u'hist']
    date = np.array([datetime.datetime.strptime(item, '%Y-%m-%d') for item in macd[u'date']])
    ax1.grid(True)
    ax1.plot(date, macds, 'r-')
    ax1.plot(date, macdsignal, 'k-')
    ax1.fill_between(date, hist, 0, facecolor=fillcolor, edgecolor=fillcolor)
    ax1.text(0.025, 0.95, u'MACD(12,26,9)', va=u'top', transform=ax1.transAxes, fontsize=textsize)
    # ax1.set_title(u"{}'s quotaition".format(code))
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

    # plot bbands quotation.
    close = bbands[u'close']
    upperband = bbands[u'upperband']
    middleband = bbands[u'middleband']
    lowerband = bbands[u'lowerband']
    ax3.grid(True)
    ax3.plot(date, close, 'k-', label=u'close')
    ax3.plot(date, upperband, 'g-')
    ax3.plot(date, lowerband, 'g-')
    ax3.plot(date, middleband, 'r-')
    ax3.text(0.38, 0.95, code + u'->BBANDS(5,2,2,0)', va=u'top', transform=ax3.transAxes, fontsize=textsize)
    ax3.legend(loc='best')

    # turn off upper axis tick labels, rotate the lower ones, etc
    for ax in ax3, ax1, ax2:
        if ax != ax2:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            for label in ax.get_xticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment('right')

                ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    plt.savefig(cons.MACD_PLOT_RESULT + u'/' + code + u'.png', format=u'png')


def get_useful_codes(code, macd, rsi, bbands):
    useful_trade = {}
    for code, pdf in get_inter_codes().items():
        df = trade_data(code)
        macd = get_macd_info(df)
        rsi = (get_rsi_info(df))[u'rsi']
        bbands = get_bbands_info(df)
        macds = macd[u'macd']
        macdsignal = macd[u'macdsignal']
        upperband = bbands[u'upperband']
        lowerband = bbands[u'lowerband']
        if (rsi.iloc[-1] > rsi.iloc[-2]
            and upperband.iloc[-1] > upperband.iloc[-2]
            and lowerband.iloc[-1] < lowerband.iloc[-2]
            and macds.iloc[-1] > macds.iloc[-2]
            and (np.abs(macdsignal.iloc[-1] - macds.iloc[-1]) < 0.02)):
            useful_trade[code] = pdf
            plot_quota(code, macd, rsi, bbands)
    return useful_trade


def insert_to_table_useful(useful_trade):
    connection = conn_mysql()
    try:
        with connection.cursor() as cursor:
            for k, v in useful_trade.items():
                sql = ('INSERT INTO {} (time,code,pdf) VALUES( %s, % s, % s)').format(cons.useful_table_name)
                cursor.execute(sql, (today_str, k, v))
            connection.commit()
    finally:
        connection.close()

    def up_codes():
        up_codes = []
        for code, pdf in get_inter_codes().items():
            df = trade_data(code)
            worths = plot_quota(code, get_macd_info(df), get_rsi_info(df), get_bbands_info(df))
            if worths != None:
                up_codes.append(worths)
        return up_codes()

    print up_codes
