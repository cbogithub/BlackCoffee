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
import re
import sys
import time

import numpy as np
import pandas as pd
import Utils as utils
from Constants import Constants

LOGGING_PATH = Constants.LOGGING_PATH_BLACK_COFFEE

sys.path.append(LOGGING_PATH)

from JobLogging import JobLogging


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
        self.log.info(u"ScrapyInterpretation's log create success.")

    def spell_urls(self, url):
        urls = []
        urls.append(url)
        for i in range(1, 3):
            urls.append(url + str(i))
        return urls

    def information(self, url):
        urls = self.spell_urls(url)
        publish_time = []
        news_content = []
        news_title = []
        pdf_url = []
        announcements = {}
        rows = 0
        for u in urls:
            bsObj = utils.conn_get(url=u)
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

        announcements[u'publishtime'] = publish_time
        announcements[u'link'] = news_content
        announcements[u'title'] = news_title
        announcements[u'pdfurl'] = pdf_url
        df = pd.DataFrame(announcements, columns=[u'publishtime', u'title', u'link', u'pdfurl'])
        df.sort_values(by=['publishtime'], inplace=True, ascending=False)
        self.log.info(u"Great job, you got {} rows information　today.".format(rows))
        return df

    def update_df_and_write2csv(self, url):
        df = self.information(url)
        self.log.info(u"Let's update the df...")
        stock_code = []
        contents = []
        for item in df.link.values:
            bsObj = utils.conn_get(url=item)
            try:
                code = bsObj.find("meta", {"name": "keywords"}).attrs["content"].split(",")[0]
                # code = code.zfill(6)
                content = bsObj.find("div", {"id": "page_0"}).text.encode('utf-8')
                content = re.sub('\r+', "", content)
                content = re.sub('\n+', "", content)
                content = re.sub(' +', "", content)
                time.sleep(np.random.choice(Constants.RANDOM_NUM))
                stock_code.append(code)
                contents.append(content)
                self.log.info(u'Get the information of {} .'.format(code))
            except Exception as e:
                stock_code.append("")
                contents.append("")
                self.log.warn(u"Get the code failed...\nFillback 'null' to it.")
                continue
        if len(stock_code) > 0:
            df[u'code'] = stock_code
            df[u'content'] = contents
        else:
            fills = np.zeros((len(df),), dtype='S1')
            df[u'code'] = df[u'content'] = fills
        archive_path = Constants.FILE_ARCHIVE + self.today
        if not os.path.isdir(archive_path):
            try:
                os.makedirs(archive_path)
            except:
                pass
        df.to_csv(archive_path + '/' + self.log_name + '.csv', mode='a+')


if __name__ == '__main__':
    time1 = datetime.datetime.now()
    rawUrl = Constants.RAW_URL_OF_INTERPRETATION
    run = ScrapyInterpretation()
    run.update_df_and_write2csv(rawUrl)
    time2 = datetime.datetime.now()
    run.log.info(u"It costs {} sec to run it.".format((time2 - time1).total_seconds()))
