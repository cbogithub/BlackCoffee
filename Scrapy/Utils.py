#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/4/16 4:50 PM

@author: IMYin

@File: Utils.py
"""

import requests
from bs4 import BeautifulSoup

from Constants import Constants

HEADERS = Constants.HEADERS

cons = Constants()


def conn_post(url, data=None, proxies=None):
    session = requests.Session()
    # add the header
    HEADERS['User-Agent'] = cons.get_user_agent()
    req = session.post(url, data, headers=HEADERS)
    bsObj = BeautifulSoup(req.text, "lxml")
    return bsObj


def conn_get(url, proxies=None):
    session = requests.Session()
    # add the header
    HEADERS['User-Agent'] = cons.get_user_agent()
    req = session.get(url, headers=HEADERS)
    bsObj = BeautifulSoup(req.text, "lxml")
    return bsObj
