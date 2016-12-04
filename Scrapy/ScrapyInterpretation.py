#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/1/16 7:51 PM

@author: IMYin

@File: ScrapyInterpretation.py

@Python Version: 2.7
"""

import datetime
import os
import sys
import time

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

from Constants import Constants

LOGGING_PATH = Constants.LOGGING_PATH_BLACK_COFFEE

sys.path.append(LOGGING_PATH)

from JobLogging import JobLogging

class ScrapyInterpretation:
    # initial log
    def __init__(self, log_lev='INFO'):
        date_today = datetime.datetime.now().date()
        log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        log_dir = Constants.TASK_LOG_PATH_BLACK_COFFEE
        self.today = date_today.strftime("%Y%m%d")
        log_dir += '/' + self.today
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass
                #        self.ignore_error = ignore_error
        mylog = JobLogging(log_name, log_dir)
        mylog.set_level(log_lev)
        self.log = mylog.get_logger()
        self.log.info("ScrapyInterpretation's log create success.")

    def spell_urls(self, url):
        urls = []
        for i in range(3):
            urls.append(url + str(i))
        return urls

    # Connection
    def conn(self, url, proxies=None):
        session = requests.Session()
        # add the header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML,like Gecko) Chrome',
            'Connection': 'Keep-Alive', 'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept': '*/*', 'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3', 'Cache-Control': 'max-age=0'}
        req = session.get(url, headers=headers)
        bsObj = BeautifulSoup(req.text, "lxml")
        return bsObj

    def information(self, url):
        urls = self.spell_urls(url)
        publish_time = []
        news_content = []
        news_title = []
        pdf_url = []
        announcements = {}
        rows = 0
        for u in urls:
            bsObj = self.conn(u)
            try:
                content = bsObj.find("div", "main-list").find("ul", "new-list").find_all('li')
                time.sleep(3)
                for _ in content:
                    try:
                        publish_time.append(_.find("span").text.encode('utf-8'))
                        news_content.append(_.find("a").attrs["href"].encode('utf-8'))
                        news_title.append(_.find("a").attrs["title"].encode('utf-8'))
                        pdf_url.append(_.find("a", {"class": "download"}).attrs["href"].encode('utf-8'))
                        rows += 1
                    except Exception as e:
                        self.log.warn("Get the content failed!--->There is no words.")
                        continue
            except Exception as e:
                self.log.warn("There is no content, see you later, honey........\n" + e.message)
                continue

        announcements['publishtime'] = publish_time
        announcements['contents'] = news_content
        announcements['title'] = news_title
        announcements['pdfurl'] = pdf_url
        df = pd.DataFrame(announcements, columns=['publishtime', 'title', 'contents', 'pdfurl'])
        df.sort_values(by=['publishtime'], inplace=True, ascending=False)
        self.log.info("Great job, you got " + str(rows) + " rows information　today.")
        # print(df.head())
        return df

    def update_df(self, url):
        df = self.information(url)
        stock_code = []
        for item in df.contents.values:
            bsObj = self.conn(item)
            try:
                code = bsObj.find("div", {"class":"stock-search-bd"}).find("div").attrs["value"]
                time.sleep(3)
                try:
                    stock_code.append(code)
                except Exception as e:
                    self.log.warn("Get the code failed...")
                    stock_code.append(np.nan)
                    continue
            except Exception as e:
                self.log.warn("There is no content, see you later, honey........\n" + e.message)
                continue
        if len(stock_code) > 0:
            df['code'] = stock_code
        else:
            df['code'] = np.zeros((len(df),), dtype='S1')
        return df





if __name__ == '__main__':
    rawUrl = Constants.RAWURL
    run = ScrapyInterpretation()
    run.information(rawUrl)
