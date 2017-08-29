# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 8/27/17 2:05 PM

@auther: imyin

@File: download_ann_east_money
"""
import datetime
import os
import re
import sys
import time
from multiprocessing.dummy import Pool as ThreadPool
from urllib.parse import urlparse
from urllib.request import urlretrieve

import Utils.scrapy_utils as s_utils
import constants as cons
from Logs.JobLogging import JobLogging


class DownloadAnn:
    # initial log
    def __init__(self, log_lev='INFO'):
        self.URL = cons.RAW_URL_OF_ANN_EAST_MONEY
        self.URL_Net = urlparse(self.URL).netloc
        self.URL_SCHEME = urlparse(self.URL).scheme
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        self.today = sys.argv[1]
        self.an_pdf_data_path = os.path.join(cons.ANN_EAST_MONEY_DOWNLOADED, self.today)
        if not os.path.exists(self.an_pdf_data_path):
            os.mkdir(self.an_pdf_data_path)
        log_dir = cons.TASK_LOG_PATH
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass
        my_log = JobLogging(self.log_name, log_dir)
        my_log.set_level(log_lev)
        self.log = my_log.get_logger()
        self.log.info("Download ann of east money's log create success.")

    def _get_column_name(self):
        connection = s_utils.conn_mysql()
        try:
            with connection.cursor() as cursor:
                sql = (cons.get_column_names.format(cons.east_money_ann_table_name, self.today, cons.SECURITYTYPE1))
                x = cursor.execute(sql)
                result = cursor.fetchmany(x)
                types = [item['columnname'] for item in result]
            return types
        finally:
            connection.close()

    def _get_data_for_column_name(self, column_name):
        connection = s_utils.conn_mysql()
        try:
            with connection.cursor() as cursor:
                sql = (cons.get_data_for_column_name.format(cons.east_money_ann_table_name, column_name, self.today,
                                                            cons.SECURITYTYPE1))
                x = cursor.execute(sql)
                result = cursor.fetchmany(x)
                data = {item['noticetitle']: item['url'] for item in result}
            return data
        finally:
            connection.close()

    def _url_for_pdf(self, url, retry=10):
        bsObj = s_utils.conn_get(url)
        for i in range(retry):
            try:
                pdf_url = bsObj.find("div", {"class": "detail-header"}).find("h1").find("span").find("a").attrs["href"]
                return pdf_url
            except Exception as e:
                self.log.info(e)
                time.sleep(0.01)
                pass

    def iterator_of_data(self):
        result = {}
        for column_name in self._get_column_name():
            for title, url in self._get_data_for_column_name(column_name).items():
                result[title] = url + cons.SPLIT_ITEM5 + column_name
        return result

    def download_it(self, file_name, retry=30):
        file_rename = re.sub("[:：/]", "_", file_name)
        file_rename = re.sub("[\*]", "", file_rename)
        info_dict = self.iterator_of_data()
        words = info_dict[file_name].split(cons.SPLIT_ITEM5)
        url = words[0]
        col = words[1]
        whole_url = self.URL_SCHEME + "://" + self.URL_Net + url
        pdf_url = self._url_for_pdf(whole_url)
        type_of_ann_path = os.path.join(self.an_pdf_data_path, re.sub("/", "_", col))
        if not os.path.exists(type_of_ann_path):
            os.mkdir(type_of_ann_path)
        download_path = type_of_ann_path + "/" + file_rename + ".pdf"
        for _ in range(retry):
            time.sleep(0.01)
            try:
                urlretrieve(pdf_url, download_path)
                if os.path.getsize(download_path) / 1024 > 2.0:
                    self.log.info("Downloaded {} successful...".format(file_name))
                    break
                else:
                    if _ != retry - 1:
                        self.log.info("Try it {} times again ---> {} ".format(_ + 2, file_name))
                    else:
                        self.log.info("{} download failed！\nSize to small!".format(file_name))
            except Exception as e:
                if _ != retry - 1:
                    self.log.info(e)
                    time.sleep(0.01)
                    pass
                else:
                    self.log.info("{} download failed！".format(file_name))
                    pass


if __name__ == '__main__':
    time1 = datetime.datetime.now()
    run = DownloadAnn()
    result_dict = run.iterator_of_data()
    pool = ThreadPool(16)
    results = pool.map(run.download_it, result_dict)
    pool.close()
    pool.join()
    time2 = datetime.datetime.now()
    run.log.info("We get {} files ...\n".format(len(result_dict)))
    run.log.info("It costs {} sec to download it.\n".format((time2 - time1).total_seconds()))
    run.log.info("=======================>DOWNLOAD PDF ({}) is OK!<=======================".format(run.today))
