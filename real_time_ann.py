# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 9/4/17 8:22 PM

@auther: imyin

@File: real_time_ann
"""

import datetime
import os
import re
import sys
import time
from multiprocessing.dummy import Pool as ThreadPool
import pandas as pd
from urllib.parse import urlparse
from urllib.request import urlretrieve

import Utils.scrapy_utils as s_utils
import Utils.east_money_utils as e_utils
import constants as cons
from Logs.JobLogging import JobLogging

raw_url = cons.ALL_ANN_EAST_MONEY_URL


class RealTimeAnn:
    # initial log
    def __init__(self, log_lev='INFO'):
        self.URL = cons.RAW_URL_OF_ANN_EAST_MONEY
        self.URL_Net = urlparse(self.URL).netloc
        self.URL_SCHEME = urlparse(self.URL).scheme
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        log_dir = cons.TASK_LOG_PATH
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass
        my_log = JobLogging(self.log_name, log_dir)
        my_log.set_level(log_lev)
        self.log = my_log.get_logger()
        self.log.info("Real time ann's log create success.")

    def info(self, retry=10):
        information = {u'SECURITYFULLNAME': [], u'NOTICETITLE': [], u'NOTICEDATE': [],
                       u'SECURITYCODE': [], u'SECURITYTYPE': [],
                       u'COLUMNNAME': [], u'URL': []}
        driver = e_utils.simulate_web()
        for i in range(retry):
            time.sleep(0.01)
            try:
                driver.get(raw_url)
                break
            except Exception as e:
                self.log.info(e)
                pass
        while True:
            for item in e_utils.get_contents(driver):
                lines = item.find_all('td')
                content_url = lines[3].find("a").attrs['href']
                # 比较信息是否相同
                if content_url != s_utils.get_first_info(execute_sql=cons.east_get_first_info,
                                                         table_name=cons.east_money_ann_table_name,
                                                         column_name='raw_url'):
                    information[u'SECURITYCODE'].append(lines[0].text)
                    information[u'SECURITYFULLNAME'].append(lines[1].text)
                    information[u'NOTICETITLE'].append(lines[3].text)
                    information[u'COLUMNNAME'].append(lines[4].text)
                    information[u'NOTICEDATE'].append(lines[5].text)
                    information[u'SECURITYTYPE'].append(cons.SECURITYTYPE1)
                    information[u'URL'].append(content_url)
                else:
                    break
            if len(information['URL']) % 50 == 0:
                time.sleep(3)
                for i in range(retry):
                    try:
                        driver.find_element_by_xpath(cons.EAST_MONEY_NEXT_PAGE).click()
                        break
                    except Exception as e:
                        self.log.info(e)
                        time.sleep(3)
                        pass
            else:
                break
        driver.close()
        if len(information['URL']) > 0:
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
        else:
            self.log.info("No data now.")
            sys.exit()

    def insert_mysql(self, df):
        self.log.info("Insert values...")
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
                    self.log.info("{} is ok.".format(row['NOTICETITLE']))
            connection.commit()
        finally:
            connection.close()

    def get_data(self, df):
        return [item['NOTICETITLE'] +
                cons.SPLIT_ITEM5 +
                item['URL'] +
                cons.SPLIT_ITEM5 +
                item['COLUMNNAME'] +
                cons.SPLIT_ITEM5 +
                item['NOTICEDATE'] for i, item in df.iterrows()]

    def _url_for_pdf(self, url, retry=10):
        bs_obj = s_utils.conn_get(url)
        for i in range(retry):
            try:
                pdf_url = bs_obj.find("div", {"class": "detail-header"}).find("h1").find("span").find("a").attrs["href"]
                return pdf_url
            except Exception as e:
                self.log.info(e)
                time.sleep(0.01)
                pass

    def _confirm_path(self, son, parent):
        path = os.path.join(son, parent)
        if not os.path.exists(path):
            try:
                os.mkdir(path)
                self.log.info("The path '{}' was created.".format(path))
            except:
                pass
        return path

    def download_it(self, lst_item, retry=10):
        lst_item = re.sub("[:：/]", "_", lst_item)
        lst_item = re.sub("[*]", "", lst_item)
        words = lst_item.split(cons.SPLIT_ITEM5)
        file_name = words[0]
        url = words[1]
        col = words[2]
        publish_time = words[3]
        whole_url = self.URL_SCHEME + "://" + self.URL_Net + url
        pdf_url = self._url_for_pdf(whole_url)
        # 创建下载路径
        ann_pdf_data_path = self._confirm_path(cons.ANN_EAST_MONEY_DOWNLOADED, publish_time)
        type_of_ann_path = self._confirm_path(ann_pdf_data_path, re.sub("/", "_", col))
        download_path = type_of_ann_path + "/" + str(file_name) + ".pdf"
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
                        self.log.info("{} size too small, try again...".format(file_name))
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
    run = RealTimeAnn()
    data = run.info()
    run.insert_mysql(data)
    result_lst = run.get_data(data)
    # 多线程下载
    pool = ThreadPool(16)
    results = pool.map(run.download_it, result_lst)
    pool.close()
    pool.join()
    time2 = datetime.datetime.now()
    run.log.info("We get {} files ...\n".format(len(result_lst)))
    run.log.info("It costs {} sec to download it.\n".format((time2 - time1).total_seconds()))
