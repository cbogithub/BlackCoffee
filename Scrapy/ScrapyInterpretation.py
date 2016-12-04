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
import re
import string

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from Constants import Constants

LOGGING_PATH = Constants.LOGGING_PATH_BLACK_COFFEE

sys.path.append(LOGGING_PATH)

from JobLogging import JobLogging

HEADERS = {
    'Connection': 'Keep-Alive', 'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept': '*/*', 'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3', 'Cache-Control': 'max-age=0'}


class ScrapyInterpretation:
    # initial log
    def __init__(self, log_lev='INFO'):
        date_today = datetime.datetime.now().date()
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        log_dir = Constants.TASK_LOG_PATH_BLACK_COFFEE
        self.today = date_today.strftime("%Y%m%d")
        log_dir += '/' + self.today
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass
        mylog = JobLogging(self.log_name, log_dir)
        mylog.set_level(log_lev)
        self.log = mylog.get_logger()
        self.log.info("ScrapyInterpretation's log create success.")
        self.headers = self.get_user_agent()

    def spell_urls(self, url):
        urls = []
        urls.append(url)
        for i in range(1, 3):
            urls.append(url + str(i))
        return urls

    def get_user_agent(self):
        my_user_agent = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)']
        user_aget = np.random.choice(my_user_agent)
        return user_aget

    # Connection
    def conn(self, url, proxies=None):
        session = requests.Session()
        # add the header
        HEADERS['User-Agent'] = self.get_user_agent()
        req = session.post(url, headers=HEADERS)
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
                time.sleep(np.random.choice(Constants.RANDOM_NUM))
                for _ in content:
                    try:
                        publish_time.append(_.find("span").text.encode('utf-8'))
                        news_content.append(_.find("a").attrs["href"].encode('utf-8'))
                        news_title.append(_.find("a").attrs["title"].encode('utf-8'))
                        pdf_url.append(_.find("a", {"class": "download"}).attrs["href"].encode('utf-8'))
                        rows += 1
                    except Exception as e:
                        self.log.warn(u"Get the content failed!--->There is no words.")
                        continue
            except Exception as e:
                self.log.warn(u"There is no content, see you later, honey........\n" + e.message)
                continue

        announcements['publishtime'] = publish_time
        announcements['link'] = news_content
        announcements['title'] = news_title
        announcements['pdfurl'] = pdf_url
        df = pd.DataFrame(announcements, columns=['publishtime', 'title', 'link', 'pdfurl'])
        df.sort_values(by=['publishtime'], inplace=True, ascending=False)
        self.log.info(u"Great job, you got {} rows information　today.".format(rows))
        return df

    def update_df_and_write2csv(self, url):
        df = self.information(url)
        self.log.info(u"Let's update the df...")
        stock_code = []
        contents = []
        companys = []
        for item in df.link.values:
            bsObj = self.conn(item)
            try:
                info = bsObj.find("meta", {"name": "keywords"}).attrs["content"].split(",")
                code = info[0]
                company = info[1]
                # code = code.zfill(6)
                content = bsObj.find("div", {"id": "page_0"}).text.encode('utf-8')
                content = re.sub('\r+', "", content)
                content = re.sub('\n+', "", content)
                content = re.sub(' ', "", content)
                time.sleep(np.random.choice(Constants.RANDOM_NUM))
                stock_code.append(code)
                contents.append(content)
                companys.append(company)
                self.log.info(u'Get the information of {} .'.format(company))
                continue
            except Exception as e:
                stock_code.append("")
                contents.append("")
                self.log.warn(u"Get the code failed...\nFillback 'null' to it.")
                continue
        if len(stock_code) > 0:
            df['company'] = companys
            df['code'] = stock_code
            df['content'] = contents
        else:
            fills = np.zeros((len(df),), dtype='S1')
            df['company'] = df['code'] = df['content'] = fills
        achive_path = Constants.FILE_ACHIVE + self.today
        if not os.path.isdir(achive_path):
            try:
                os.makedirs(achive_path)
            except:
                pass
        df.to_csv(achive_path + '/' + self.log_name + '.csv', mode='a+')


if __name__ == '__main__':
    time1 = datetime.datetime.now()
    rawUrl = Constants.RAWURL
    run = ScrapyInterpretation()
    run.update_df_and_write2csv(rawUrl)
    time2 = datetime.datetime.now()
    run.log.info(u"It costs {} sec to run it.".format((time2 - time1).total_seconds()))
