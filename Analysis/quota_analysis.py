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

import matplotlib
import numpy as np
import pandas as pd
import pymysql
import talib as ta
import tushare as ts
from multiprocessing.dummy import Pool as ThreadPool

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# must use absolute path..
CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

view_days = 14
textsize = 9
today_str_Ymd = sys.argv[1]


# yesterday_str_md = sys.argv[2]


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
            sql = (cons.up_codes_sql.format(cons.inter_table_name, cons.yesterday_str_md, cons.UP))
            x = cursor.execute(sql)
            result = cursor.fetchmany(x)
            codes = {item[u'code']: item[u'pdf_url'] for item in result}
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
    data = ts.get_hist_data(code, end=today_str_Ymd)
    data[u'date'] = data.index
    data[u'code'] = code

    data = data.sort_index(ascending=True)
    return data


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
    date = np.array([datetime.datetime.strptime(item, u'%Y-%m-%d') for item in macd[u'date']])
    ax1.grid(True)
    ax1.plot(date, macds, 'r-')
    ax1.plot(date, macdsignal, 'k-')
    ax1.fill_between(date, hist, 0, facecolor=fillcolor, edgecolor=fillcolor)
    ax1.text(0.025, 0.95, u'MACD(12,26,9)', va=u'top', transform=ax1.transAxes, fontsize=textsize)

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
    ax3.plot(date, close, 'k-')
    ax3.plot(date, upperband, 'g-')
    ax3.plot(date, lowerband, 'g-')
    ax3.plot(date, middleband, 'r-')
    ax3.text(0.38, 0.95, code + u'->BBANDS(5,2,2,0)', va=u'top', transform=ax3.transAxes, fontsize=textsize)
    # ax3.legend(loc=u'best')

    # turn off upper axis tick labels, rotate the lower ones, etc
    for ax in ax3, ax1, ax2:
        if ax != ax2:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            for label in ax.get_xticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment(u'right')

                ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    data_path = os.path.join(cons.MACD_PLOT_RESULT, today_str_Ymd)
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    data_path = os.path.join(data_path, code + u'.png')
    plt.savefig(data_path, format=u'png')
    plt.close()


def get_useful_codes():
    useful_trade = {}
    for code, pdf in get_inter_codes().items():
        df = trade_data(code)
        trade_time = df.date.values[-1]
        last_close = df.close.values[-1]
        macd = get_macd_info(df)
        rsi = get_rsi_info(df)
        bbands = get_bbands_info(df)
        rsi_values = rsi[u'rsi']
        macds = macd[u'macd']
        macdsignal = macd[u'macdsignal']
        upperband = bbands[u'upperband']
        lowerband = bbands[u'lowerband']
        if (trade_time == u'2017-01-06'
            and last_close <= 15
            and rsi_values.iloc[-1] > rsi_values.iloc[-2]
            and upperband.iloc[-1] > upperband.iloc[-2]
            and lowerband.iloc[-1] < lowerband.iloc[-2]
            and macds.iloc[-1] > macds.iloc[-2]
            and macdsignal.iloc[-1] - macds.iloc[-1]) < 0.02:
            useful_trade[code] = pdf
            plot_quota(code, macd, rsi, bbands)
    return useful_trade


def get_today_codes():
    stock_basics = ts.get_today_all()
    return stock_basics.code.values


def get_useful_codes_allday(code):
    df = trade_data(code)
    if len(df) > 60:
        today_time = df.date.values[-1]
        last_close = df.close.values[-1]
        macd = get_macd_info(df)
        rsi = get_rsi_info(df)
        bbands = get_bbands_info(df)
        rsi_values = rsi[u'rsi']
        macds = macd[u'macd']
        macdsignal = macd[u'macdsignal']
        upperband = bbands[u'upperband']
        lowerband = bbands[u'lowerband']
        if (today_time == today_str_Ymd
            and last_close <= 15
            and rsi_values.iloc[-1] > rsi_values.iloc[-2]
            and upperband.iloc[-1] > upperband.iloc[-2]
            and lowerband.iloc[-1] < lowerband.iloc[-2]
            and macds.iloc[-1] > macds.iloc[-2]
            and 0 < (macdsignal.iloc[-1] - macds.iloc[-1]) < 0.025):
            plot_quota(code, macd, rsi, bbands)
            useful_data = df.iloc[-1]
            return useful_data


def insert_to_table_useful(useful_trade):
    connection = conn_mysql()
    try:
        with connection.cursor() as cursor:
            for line in useful_trade:
                if not line is None:
                    sql = cons.insert_useful_trade_sql.format(cons.usefule_table_name)
                    cursor.execute(sql, (line[u'date'],
                                         line[u'code'],
                                         float(line[u'open']),
                                         float(line[u'close']),
                                         float(line[u'high']),
                                         float(line[u'low']),
                                         float(line[u'volume'])))
            connection.commit()
    finally:
        connection.close()


time1 = datetime.datetime.now()
codes = get_today_codes()
pool = ThreadPool(32)
results = pool.map(get_useful_codes_allday, codes)
pool.close()
pool.join()
insert_to_table_useful(results)
time2 = datetime.datetime.now()
print (u"\nIt costs {} sec to run it.\nToday is {}...".format((time2 - time1).total_seconds(), today_str_Ymd))
