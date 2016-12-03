#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/3/16 4:52 PM

@author: IMYin

@File: testJavaScript.py
"""

import requests
from bs4 import BeautifulSoup

url = 'http://xinpi.cnstock.com/Search.aspx'
join_group = {"__EVENTTARGET":"pagerQuestion","__EVENTARGUMENT":"5"}
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML,like Gecko) Chrome',
    'Connection': 'Keep-Alive', 'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept': '*/*', 'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3', 'Cache-Control': 'max-age=0'}
session = requests.Session()

req = session.post(url,join_group,headers=headers)
bsObj = BeautifulSoup(req.text, "lxml")
content = bsObj.find_all("ul",{"class":"gg-list"})
for _ in content:
    stock_code = _.find("span",{"class":"code"}).text.encode('utf-8')
    title = _.find_all("a")[1].attrs["title"].encode('utf-8')
    print stock_code
    print title
    break
# print req.content
# req = session.get(url, headers=headers)
