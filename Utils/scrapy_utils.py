#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/4/16 4:50 PM

@author: IMYin

@File: scrapy_utils.py
"""

import time

import numpy as np
import pymysql
import requests
from bs4 import BeautifulSoup

import constants as cons


def conn_post(url, data=None, proxies=None, retry=10):
    """
    In order to solve JavaScript relate problem, use post function.
    :param url:
    :param data:
    :param proxies:
    :return: bsObj
    """
    session = requests.Session()
    for i in range(retry):
        try:
            headers = get_headers()
            req = session.post(url, data, headers=headers)
            bsObj = BeautifulSoup(req.text, "lxml")
            return bsObj
        except:
            time.sleep(0.01)


def conn_get(url, proxies=None, retry=10):
    """
    Use get function to connect the url.
    :param url:
    :param proxies:
    :return: bsObj
    """
    session = requests.Session()
    for i in range(retry):
        try:
            headers = get_headers()
            req = session.get(url, headers=headers)
            bsObj = BeautifulSoup(req.text, "lxml")
            return bsObj
        except:
            time.sleep(0.01)
            pass


def get_headers():
    cons.HEADERS[u'User-Agent'] = np.random.choice(cons.my_user_agent)
    return cons.HEADERS


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
