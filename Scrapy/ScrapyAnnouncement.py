#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/4/16 9:18 AM

@author: IMYin

@File: ScrapyAnnouncement.py
"""
import datetime
import os
import sys
import time
from urlparse import urlparse

import numpy as np
import pandas as pd
import pymysql.cursors

import Utils as utils

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

LOGGING_PATH = cons.LOGGING_PATH
sys.path.append(LOGGING_PATH)
from JobLogging import JobLogging

URL = cons.RAW_URL_OF_ANNOUNCEMENT
URL_Net = urlparse(URL).netloc
URL_SCHEME = urlparse(URL).scheme


class ScrapyAnnouncement:
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
        self.log.info("ScrapyAnnouncement's log create success.")

    def info(self):
        publish_time = []
        news_title = []
        pdf_url = []
        stock_code = []
        for item in range(1, 9):
            data = {"__EVENTTARGET": "pagerQuestion", "__EVENTARGUMENT": str(item)}
            bsObj = utils.conn_post(URL, data=data)
            try:
                content = bsObj.find("ul", {"class": "gg-list"}).find_all("li")
                time.sleep(np.random.rand(1))
                for item in content:
                    try:
                        con = item.find_all("a")
                        s_code = item.find("span", {"class": "code"}).text.encode('utf-8')
                        stock_code.append(s_code.strip("\n"))
                        pdf_url.append(URL_SCHEME + "://" + URL_Net + "/" + con[1].attrs["href"])
                        news_title.append(con[1].attrs["title"].encode('utf-8'))
                        published = item.find("span", {"class": "time"}).text.encode('utf-8')
                        publish_time.append(published.strip("()"))
                    except Exception as e:
                        pass
            except Exception as e:
                pass

        announcements = {u'publishtime': publish_time, u'code': stock_code, u'title': news_title, u'pdfurl': pdf_url}
        df = pd.DataFrame(announcements, columns=[u'publishtime', u'code', u'title', u'pdfurl'])

        return df
        # Write content to file.csv

        # archive_path = cons.FILE_ARCHIVE + self.today
        # if not os.path.isdir(archive_path):
        #     try:
        #         os.makedirs(archive_path)
        #     except:
        #         pass
        # data_path = os.path.join(archive_path, self.log_name + ".csv")
        # df.to_csv(data_path)
        # self.log.info(u"Save data to {} successful.".format(data_path))

    # Use mysql to store information of stock which is crawled by some websites.
    def insert_to_table(self, df):
        connection = pymysql.connect(host=cons.mysql_host,
                                     user=cons.mysql_user,
                                     password=cons.mysql_passwd,
                                     db=cons.stock_db,
                                     charset='utf8',  # set the mysql character is utf-8 !!!
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                for index, row in df.iterrows():
                    sql = cons.insert_announ_table_sql.format(cons.announ_table_name)
                    cursor.execute(sql, (
                        row[u'publishtime'], row[u'code'], row[u'title'], row[u'pdfurl']))
                    self.log.info(
                        u"Got the '{}, {}, {}, {}' into table: {}".format(row[u'publishtime'], row[u'code'],
                                                                          row[u'title'].decode('utf-8'),
                                                                          row[u'pdfurl'], cons.announ_table_name))
            connection.commit()
            self.log.info(u"Great job, you got {} rows information　today.".format(len(df)))
        finally:
            connection.close()


if __name__ == '__main__':
    time1 = datetime.datetime.now()
    rawUrl = cons.RAW_URL_OF_INTERPRETATION
    run = ScrapyAnnouncement()
    run.insert_to_table(run.info())
    time2 = datetime.datetime.now()
    run.log.info(u"It costs {} sec to run it.".format((time2 - time1).total_seconds()))
    run.log.info(u"-" * 100)
