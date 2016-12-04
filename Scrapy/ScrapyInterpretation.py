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
import requests
from bs4 import BeautifulSoup

from Constants import Constants

logging_path = Constants.LOGGING_PATH_BLACK_COFFEE

sys.path.append(logging_path)

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
        self.log = mylog.get_logger()
        self.log.info("ScrapyInterpretation's log create success")

    def spellUrls(self, url):
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
        urls = self.spellUrls(url)
        publish_time = []
        news_content = []
        news_title = []
        pdf_url = []
        announcements = {}
        for url in urls:
            bsObj = self.conn(url)
            time.sleep(3)
            try:
                content = bsObj.find("div", "main-list").find("ul", "new-list").find_all('li')
                for _ in content:
                    try:
                        publish_time.append(_.find("span").text.encode('utf-8'))
                        news_content.append(_.find("a").attrs["href"].encode('utf-8'))
                        news_title.append(_.find("a").attrs["title"].encode('utf-8'))
                        pdf_url.append(_.find("a", {"class": "download"}).attrs["href"].encode('utf-8'))
                        self.log.info("Get the content successful!!!")
                    except Exception as e:
                        self.log.warn("Get the content failed!--->There is no words.")
                        continue
            except Exception as e:
                self.log.warn("There is no content, see you later, honey........\n" + e.message)

        announcements['PublishTime'] = publish_time
        announcements['NewsContent'] = news_content
        announcements['NewsTitle'] = news_title
        announcements['PDFUrl'] = pdf_url
        df = pd.DataFrame(announcements)
        df.sort_values(by=['PublishTime'], inplace=True, ascending=False)
        # print(df.head())
        df.to_csv(Constants.FILE_ACHIVE + self.today, header=False)
        return df


if __name__ == '__main__':
    rawUrl = Constants.RAWURL
    run = ScrapyInterpretation()
    run.information(rawUrl)
