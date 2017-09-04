# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 8/26/17 3:00 PM

@auther: imyin

@File: get_data_ann_east_money
"""

import os
import sys
import time
from urllib.parse import urlparse

import pandas as pd

import Utils.east_money_utils as e_utils
import Utils.scrapy_utils as s_utils
import constants as cons
from Logs.JobLogging import JobLogging


class GetAnnData:
    # initial log
    def __init__(self, log_lev='INFO'):
        self.URL = cons.RAW_URL_OF_ANN_EAST_MONEY
        self.URL_Net = urlparse(self.URL).netloc
        self.URL_SCHEME = urlparse(self.URL).scheme
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        self.today = sys.argv[1]
        self.page_num = 0
        # self.yesterday = '2017-08-26'
        log_dir = cons.TASK_LOG_PATH
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass
        my_log = JobLogging(self.log_name, log_dir)
        my_log.set_level(log_lev)
        self.log = my_log.get_logger()

    def info(self, url, retry=10):
        information = {u'SECURITYFULLNAME': [], u'NOTICETITLE': [], u'NOTICEDATE': [],
                       u'SECURITYCODE': [], u'SECURITYTYPE': [],
                       u'COLUMNNAME': [], u'URL': []}
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
                break
            except Exception as e:
                if i != retry - 1:
                    self.log.info(e)
                    pass
                else:
                    self.log.info(
                        "yesterday has no data.\nGoodbey!\n==========>No data day:{}<==========".format(self.today))
                    sys.exit()
        self.log.info("{} pages to get...".format(self.page_num))
        for page in range(self.page_num):
            for item in e_utils.get_contents(driver):
                lines = item.find_all('td')
                information[u'SECURITYCODE'].append(lines[0].text)
                information[u'SECURITYFULLNAME'].append(lines[1].text)
                information[u'NOTICETITLE'].append(lines[3].text)
                information[u'COLUMNNAME'].append(lines[4].text)
                information[u'NOTICEDATE'].append(self.today)
                information[u'SECURITYTYPE'].append(cons.SECURITYTYPE1)
                information[u'URL'].append(lines[3].find("a").attrs['href'])
            time.sleep(3)
            for i in range(retry):
                try:
                    driver.find_element_by_xpath(cons.EAST_MONEY_NEXT_PAGE).click()
                    break
                except Exception as e:
                    self.log.info(e)
                    time.sleep(3)
                    pass
            self.log.info("the {} page scrapy successful..".format(page + 1))
        driver.close()
        df = pd.DataFrame(information,
                          columns=[u'SECURITYCODE',
                                   u'SECURITYFULLNAME',
                                   u'NOTICETITLE',
                                   u'NOTICEDATE',
                                   u'SECURITYTYPE',
                                   u'COLUMNNAME',
                                   u'URL'])
        df.drop_duplicates(inplace=True)
        df.index = range(len(df))
        return df

    # Use mysql to store information of stock which is crawled by some websites.
    def insert_mysql(self, df):
        connection = s_utils.conn_mysql()
        try:
            with connection.cursor() as cursor:
                # 倒序插入表中
                for index, row in df[::-1].iterrows():
                    sql = cons.insert_east_money_ann_sql.format(cons.east_money_ann_table_name)
                    cursor.execute(sql, (row[u'SECURITYCODE'],
                                         row[u'SECURITYFULLNAME'],
                                         row[u'NOTICETITLE'],
                                         row[u'NOTICEDATE'],
                                         row[u'SECURITYTYPE'],
                                         row[u'COLUMNNAME'],
                                         row[u'URL']))
            connection.commit()
        finally:
            connection.close()


if __name__ == '__main__':
    run = GetAnnData()
    df = run.info(cons.RAW_URL_OF_ANN_EAST_MONEY + run.today + ".html")
    run.insert_mysql(df)
