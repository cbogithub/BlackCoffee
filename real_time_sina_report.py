# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 9/7/17 9:09 AM

@auther: imyin

@File: real_time_sina_report
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


class RealTimeSinaReport:
    # initial log
    def __init__(self, log_lev='INFO'):
        self.URL = cons.RAW_URL_OF_ANN_EAST_MONEY
        self.URL_Net = urlparse(self.URL).netloc
        self.URL_SCHEME = urlparse(self.URL).scheme
        self.log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        # self.today = (datetime.datetime.now()).strftime("%Y-%m-%d")
        self.today = sys.argv[1]
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
        self.log.info("Download ann of east money's log create success.")

    def info(self):
        information = {"title": [],
                       "article_url": [],
                       "type": [],
                       "publish_time": [],
                       "institution": [],
                       "author": [],
                       "content": []}
        first_record = s_utils.get_first_info(cons.get_first_sina_report, cons.research_report_table_name,
                                              column_name='article_url')
        page = 1
        while True:
            bsObj = s_utils.conn_get(cons.SIAN_REPORT_URL + self.today + "&p=" + str(page))
            contents = bsObj.find("div", {"class": "main"}).find("table").find_all("tr")[2:]
            for content in contents:
                article = content.find_all("td")
                article_info = article[1].find("a")
                article_url = article_info.attrs["href"]
                if article_url != first_record:
                    information["title"].append(article_info.attrs["title"].encode('latin1').decode('gb2312', 'ignore'))
                    information["article_url"].append(article_url)
                    information["type"].append(article[2].text.encode('latin1').decode('gb2312', 'ignore'))
                    information["publish_time"].append(self.today)
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
                else:
                    break
            time.sleep(0.01)
            if len(information['article_url']) % 40 == 0:
                page += 1
            else:
                break
        if len(information['article_url']) > 0:
            df = pd.DataFrame(information,
                              columns=["title",
                                       "article_url",
                                       "type",
                                       "publish_time",
                                       "institution",
                                       "author",
                                       "content"])
            return df
        else:
            self.log.info("No data now.")
            sys.exit()

    def insert_mysql(self, df):
        self.log.info("Inserting values...")
        connection = s_utils.conn_mysql()
        try:
            with connection.cursor() as cursor:
                # 倒序插入表中
                for index, row in df[::-1].iterrows():
                    sql = cons.insert_reseach_report.format(cons.research_report_table_name)
                    cursor.execute(sql, (row[u'title'],
                                         row[u'article_url'],
                                         row[u'type'],
                                         row[u'publish_time'],
                                         row[u'institution'],
                                         row[u'author'],
                                         row[u'content']))
                    self.log.info("{} was inserted.".format(row['title']))
            connection.commit()
        finally:
            connection.close()

    def write2file_txt(self, df):
        df.drop(["article_url", "publish_time", "author"], axis=1, inplace=True)
        df['filter'] = "-" * 100
        for t in df['type'].drop_duplicates():
            report_path = s_utils.confirm_path(self.report_dir, re.sub("[/]", "_", t))
            new_df = df[df['type'] == t]
            new_df.to_csv(report_path + "/" + self.today + ".csv", sep="\n", mode="a", header=False,
                          index=False, encoding='utf-8')


if __name__ == '__main__':
    time1 = datetime.datetime.now()
    run = RealTimeSinaReport()
    data = run.info()
    run.insert_mysql(data)
    run.write2file_txt(data)
    time2 = datetime.datetime.now()
    run.log.info("We get {} files ...\n".format(len(data)))
    run.log.info("It costs {} sec to run.\n".format((time2 - time1).total_seconds()))
