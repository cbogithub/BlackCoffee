#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/4/16 4:50 PM

@author: IMYin

@File: Utils.py
"""

import os
import sys

import requests
from bs4 import BeautifulSoup

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import constants as cons


def conn_post(url, data=None, proxies=None):
    """
    In order to solve JavaScript relate problem, use post function.
    :param url:
    :param data:
    :param proxies:
    :return: bsObj
    """
    session = requests.Session()
    headers = cons.get_headers()
    req = session.post(url, data, headers=headers)
    bsObj = BeautifulSoup(req.text, "lxml")
    return bsObj


def conn_get(url, proxies=None):
    """
    Use get function to connect the url.
    :param url:
    :param proxies:
    :return: bsObj
    """
    session = requests.Session()
    headers = cons.get_headers()
    req = session.get(url, headers=headers)
    bsObj = BeautifulSoup(req.text, "lxml")
    return bsObj
