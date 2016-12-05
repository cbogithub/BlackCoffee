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

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

LOGGING_PATH = cons.LOGGING_PATH
sys.path.append(LOGGING_PATH)
from JobLogging import JobLogging


class ScrapyInterpretation:
    # initial log
    def __init__(self, log_lev='INFO'):
        date_today = datetime.datetime.now().date()
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        log_dir = cons.TASK_LOG_PATH
        self.today = date_today.strftime("%Y%m%d")
        # log_dir += '/' + self.today
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
        for u in urls:
            bsObj = utils.conn_get(url=u)
            try:
                content = bsObj.find("div", "main-list").find("ul", "new-list").find_all('li')
                time.sleep(np.random.rand(1))
                for _ in content:
                    try:
                        publish_time.append(_.find("span").text.encode('utf-8'))
                        news_content.append(_.find("a").attrs["href"].encode('utf-8'))
                        news_title.append(_.find("a").attrs["title"].encode('utf-8'))
                        pdf_url.append(_.find("a", {"class": "download"}).attrs["href"].encode('utf-8'))
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        announcements = {u'publish_time': publish_time, u'link': news_content, u'title': news_title,
                         u'pdf_url': pdf_url}
        return announcements

    def update_df_and_write2csv(self, url):
        announcements = self.information(url)
        stock_code = []
        contents = []
        for item in announcements[u'link']:
            bsObj = utils.conn_get(url=item)
            try:
                code = bsObj.find("meta", {"name": "keywords"}).attrs["content"].split(",")[0]
                # code = code.zfill(6)
                content = bsObj.find("div", {"class": "explain-box"}).text.encode('utf-8')
                content = re.sub('\r+', "", content)
                content = re.sub('\n+', "", content)
                content = re.sub(' +', "", content)
                time.sleep(np.random.rand(1))
                stock_code.append(code)
                contents.append(content)
            except Exception as e:
                stock_code.append("")
                contents.append("")
        if len(stock_code) > 0:
            announcements[u'code'] = stock_code
            announcements[u'content'] = contents
        else:
            fills = np.zeros((len(announcements[u'link']),), dtype='S1')
            announcements[u'code'] = fills
            announcements[u'content'] = fills

        df = pd.DataFrame(announcements, columns=[u'publish_time', u'code', u'title', u'content', u'pdf_url'])
        self.log.info(u"Great job, you got {} rows information today.".format(len(df)))
        df.sort_values(by=['publish_time'], inplace=True, ascending=False)
        archive_path = cons.FILE_ARCHIVE + self.today
        if not os.path.isdir(archive_path):
            try:
                os.makedirs(archive_path)
            except:
                pass
        data_path = os.path.join(archive_path, self.log_name + ".csv")
        df.to_csv(data_path)
        self.log.info(u"Save data to {} successful.".format(data_path))


if __name__ == '__main__':
    time1 = datetime.datetime.now()
    rawUrl = cons.RAW_URL_OF_INTERPRETATION
    run = ScrapyInterpretation()
    run.update_df_and_write2csv(rawUrl)
    time2 = datetime.datetime.now()
    run.log.info(u"It costs {} sec to run it.".format((time2 - time1).total_seconds()))
    run.log.info(u"-" * 100)
