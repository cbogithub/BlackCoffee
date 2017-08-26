# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 8/26/17 3:00 PM

@auther: imyin

@File: download_ann_east_money
"""

import datetime
import os
import sys
import time
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup

import Utils.east_money_utils as e_utils
import Utils.scrapy_utils as s_utils
import constants as cons
from Logs.JobLogging import JobLogging


class DownloadAnn:
    # initial log
    def __init__(self, log_lev='INFO'):
        self.URL = cons.RAW_URL_OF_ANN_EAST_MONEY
        self.URL_Net = urlparse(self.URL).netloc
        self.URL_SCHEME = urlparse(self.URL).scheme
        date_today = datetime.datetime.now().date()
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        log_dir = cons.TASK_LOG_PATH
        # self.today = date_today.strftime("%Y-%m-%d")
        self.today = '2017-08-26'
        # log_dir += '/' + self.today
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass
        my_log = JobLogging(self.log_name, log_dir)
        my_log.set_level(log_lev)
        self.log = my_log.get_logger()
        self.log.info("downlaod ann of east money's log create success.")

    def connect_internet(self, driver, url, retry=3):
        for i in range(retry):
            time.sleep(0.01)
            try:
                driver.get(url)
                break
            except Exception as e:
                self.log.info(e)
                pass

    def info(self, url, retry=10):
        information = {u'SECURITYFULLNAME': [], u'SECURITYSHORTNAME': [], u'NOTICETITLE': [], u'NOTICEDATE': [],
                       u'SECURITYVARIETYCODE': [], u'SECURITYTYPECODE': [], u'SECURITYCODE': [], u'SECURITYTYPE': [],
                       u'TRADEMARKETCODE': [], u'TRADEMARKET': [], u'COMPANYCODE': [], u'COLUMNNAME': [], u'URL': []}
        driver = e_utils.simulate_web()
        for i in range(retry):
            time.sleep(0.01)
            try:
                driver.get(url)
                break
            except Exception as e:
                self.log.info(e)
                pass
        for i in range(retry):
            try:
                self.page_num = int(driver.find_element_by_xpath(cons.EAST_MONEY_LAST_PAGE).text)
                print(self.page_num)
                break
            except Exception as e:
                if i != retry-1:
                    self.log.info(e)
                    pass
                else:
                    self.log.info("today has no data.\nGoodbey!\n==========>No data day:{}<==========".format(self.today))
                    sys.exit()
        for page in range(self.page_num):
            bsObj = BeautifulSoup(driver.page_source, "lxml")
            find_lst = e_utils.re_lst(bsObj.text)
            for line in e_utils.mk_dict(find_lst):
                temp_dict = {t[0].replace("\"", ""): t[1].replace("\"", "") for t in line if
                             t[1].replace("\"", "") != "null"}
                information[u'SECURITYFULLNAME'].append(temp_dict[u'SECURITYFULLNAME'])
                information[u'SECURITYSHORTNAME'].append(temp_dict[u'SECURITYSHORTNAME'])
                information[u'NOTICETITLE'].append(temp_dict[u'NOTICETITLE'])
                information[u'NOTICEDATE'].append(self.today)
                information[u'SECURITYVARIETYCODE'].append(temp_dict[u'SECURITYVARIETYCODE'])
                information[u'SECURITYTYPECODE'].append(temp_dict[u'SECURITYTYPECODE'])
                information[u'SECURITYCODE'].append(temp_dict[u'SECURITYCODE'])
                information[u'SECURITYTYPE'].append(temp_dict[u'SECURITYTYPE'])
                information[u'TRADEMARKETCODE'].append(temp_dict[u'TRADEMARKETCODE'])
                information[u'TRADEMARKET'].append(temp_dict[u'TRADEMARKET'])
                information[u'COMPANYCODE'].append(temp_dict[u'COMPANYCODE'])
                information[u'COLUMNNAME'].append(temp_dict[u'COLUMNNAME'])
                information[u'URL'].append(temp_dict[u'Url'])
            time.sleep(3)
            for i in range(retry):
                time.sleep(3)
                try:
                    driver.find_element_by_xpath(cons.EAST_MONEY_NEXT_PAGE).click()
                    break
                except Exception as e:
                    self.log.info(e)
                    pass

        return pd.DataFrame(information,
                            columns=[u'SECURITYFULLNAME', u'SECURITYSHORTNAME', u'NOTICETITLE',
                                     u'NOTICEDATE', u'SECURITYVARIETYCODE', u'SECURITYTYPECODE',
                                     u'SECURITYCODE', u'SECURITYTYPE', 'TRADEMARKETCODE',
                                     u'TRADEMARKET', u'COMPANYCODE', u'COLUMNNAME', u'URL'])

    # Use mysql to store information of stock which is crawled by some websites.
    def insert_mysql(self, df):
        connection = s_utils.conn_mysql()
        try:
            with connection.cursor() as cursor:
                for index, row in df.iterrows():
                    sql = cons.insert_east_money_ann_sql.format(cons.east_money_ann_table_name)
                    cursor.execute(sql, (row[u'SECURITYFULLNAME'],
                                         row[u'SECURITYSHORTNAME'],
                                         row[u'NOTICETITLE'],
                                         row[u'NOTICEDATE'],
                                         row[u'SECURITYVARIETYCODE'],
                                         row[u'SECURITYTYPECODE'],
                                         row[u'SECURITYCODE'],
                                         row[u'SECURITYTYPE'],
                                         row[u'TRADEMARKETCODE'],
                                         row[u'TRADEMARKET'],
                                         row[u'COMPANYCODE'],
                                         row[u'COLUMNNAME'],
                                         row[u'URL']))
                    connection.commit()
        finally:
            connection.close()


if __name__ == '__main__':
    run = DownloadAnn()
    df = run.info(cons.RAW_URL_OF_ANN_EAST_MONEY + run.today + ".html")
    run.insert_mysql(df)
