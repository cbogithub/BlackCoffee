# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 8/30/17 8:18 PM

@auther: imyin

@File: sina_research_report
"""
import datetime
import time
import os
import re
import sys
from urllib.parse import urlparse
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
import constants as cons
from Logs.JobLogging import JobLogging
from Utils import scrapy_utils as s_utils


class SinaResearchReport:
    # initial log
    def __init__(self, log_lev='INFO'):
        self.URL = cons.RAW_URL_OF_ANN_EAST_MONEY
        self.URL_Net = urlparse(self.URL).netloc
        self.URL_SCHEME = urlparse(self.URL).scheme
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        self.yesterday = sys.argv[1]
        self.page_num = 0
        self.report_dir = cons.RESEARCH_REPORT_PATH
        if not os.path.exists(self.report_dir):
            os.mkdir(self.report_dir)
        log_dir = cons.TASK_LOG_PATH
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        my_log = JobLogging(self.log_name, log_dir)
        my_log.set_level(log_lev)
        self.log = my_log.get_logger()
        self.log.info("Sina report's log create success.")

    def info(self):
        information = {"title": [],
                       "article_url": [],
                       "type": [],
                       "publish_time": [],
                       "institution": [],
                       "author": [],
                       "content": []}
        for i in range(1, self._get_pages() + 1):
            bsObj = s_utils.conn_get(cons.SIAN_REPORT_URL + self.yesterday + "&p=" + str(i))
            contents = bsObj.find("div", {"class": "main"}).find("table").find_all("tr")[2:]
            for content in contents:
                article = content.find_all("td")
                article_info = article[1].find("a")
                article_url = article_info.attrs["href"]
                information["title"].append(article_info.attrs["title"].encode('latin1').decode('gb2312', 'ignore'))
                information["article_url"].append(article_url)
                information["type"].append(article[2].text.encode('latin1').decode('gb2312', 'ignore'))
                information["publish_time"].append(self.yesterday)
                information["institution"].append(
                    article[4].find("a").find("div").find("span").text.encode('latin1').decode('gb2312', 'ignore'))
                information["author"].append(
                    article[5].find("div").find("span").text.encode('latin1').decode('gb2312', 'ignore'))
                try:
                    content_bs = s_utils.conn_get(article_url)
                    content_text = content_bs.find("div", {"class": "blk_container"}).find("p").text
                    content_text = content_text.encode('latin1').decode('gb2312', 'ignore')
                    content_text = re.sub("\n+", "\n", content_text)
                    content_text = re.sub(" +", " ", content_text)
                    information["content"].append(content_text)
                except Exception as e:
                    self.log.info("\n{}".format(e))
                    information["content"].append("")
                    pass
            self.log.info("the {} page scrapy successful..".format(i))
            time.sleep(0.01)
        df = pd.DataFrame(information,
                          columns=["title",
                                   "article_url",
                                   "type",
                                   "publish_time",
                                   "institution",
                                   "author",
                                   "content"])
        return df

    def insert_mysql(self, df):
        connection = s_utils.conn_mysql()
        try:
            with connection.cursor() as cursor:
                for index, row in df.iterrows():
                    sql = cons.insert_reseach_report.format(cons.research_report_table_name)
                    cursor.execute(sql, (row['title'],
                                         row['article_url'],
                                         row['type'],
                                         row['publish_time'],
                                         row['institution'],
                                         row['author'],
                                         row['content']))
            connection.commit()
        finally:
            connection.close()

    def _get_pages(self, retry=3):
        bsObj = s_utils.conn_get(cons.SIAN_REPORT_URL + self.yesterday)
        for i in range(retry):
            try:
                page_num = \
                    bsObj.find("div", {"class": "page"}).find("tr").find("td").find("div",
                                                                                    {"class": "pagebox"}).find_all(
                        "span", {
                            "class": "pagebox_next"})[-1].find("a").attrs["onclick"]
                page_num = re.search("(\d+)", page_num)
                page_num = page_num.group()
                return int(page_num)
            except Exception as e:
                if i != retry - 1:
                    self.log.info(e)
                    pass
                else:
                    self.log.info("==========>No data day:{}<==========".format(self.yesterday))
                    sys.exit()

    def write2file_txt(self, df):
        df.drop(["article_url", "publish_time", "author"], axis=1, inplace=True)
        df['filter'] = "-" * 100
        for t in df['type'].drop_duplicates():
            report_path = s_utils.confirm_path(self.report_dir, re.sub("[/]", "_", t))
            new_df = df[df['type'] == t]
            new_df.to_csv(report_path + "/" + self.yesterday + ".csv", sep="\n", mode="a", header=False,
                          index=False, encoding='utf-8')


if __name__ == '__main__':
    report = SinaResearchReport()
    data = report.info()
    report.insert_mysql(data)
    report.write2file_txt(data)
    # report.insert_mysql(report.info())
    # result_dict = report.get_article_type()
    # pool = ThreadPool(32)
    # pool.map(report.write2file, result_dict)
    # pool.close()
    # pool.join()
