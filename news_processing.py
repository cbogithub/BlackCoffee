# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 8/29/17 8:31 PM

@auther: imyin

@File: news_processing
"""

import datetime
import os
import re
import sys
import time
from urllib.parse import urlparse

import newspaper
import pandas as pd

import Utils.scrapy_utils as s_utils
import constants as cons
from Logs.JobLogging import JobLogging


class News:
    # initial log
    def __init__(self, log_lev='INFO'):
        self.contents = {"article_title": [], "article_text": []}
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
        self.log.info("News's log create success.")

    def get_article(self, url):
        article = newspaper.Article(url, language=u'zh')
        try:
            article.download()
            article.parse()
        except Exception as e:
            self.log.info(u"Something go wrong:\n{}\nCannot download it...".format(e))
            pass
        article_title = article.title
        article_text = article.text
        return article_title, article_text

    def get_content(self, time_now, retry=3):
        try:
            builder = newspaper.build(cons.NEWS_RESOURCE, language=u'zh')
            news_size = builder.size()
            if news_size > 0:
                for item in builder.articles:
                    for _ in range(retry):
                        time.sleep(0.01)
                        article_title, article_text = self.get_article(item.url)
                        if len(article_text) != 0 and len(article_title) != 0:
                            break
                        elif len(article_text) != 0 and (_ == (retry - 1) and len(article_title) == 0):
                            article_title = item.url
                    self.contents["article_title"].append(article_title)
                    self.contents["article_text"].append(re.sub("[\n]", " ", article_text))
                    self.log.info(u"{}--->{}".format(article_title, article_text))
                self.log.info(u"There are {} news...".format(news_size))
                self.log.info(u"-" * 100)
                df = pd.DataFrame(self.contents, columns=['article_title', 'article_text'])
                df['publish_time'] = time_now
                return df
            else:
                self.log.info(u"There is nothing to get...")
                sys.exit()
        except Exception as e:
            self.log.info(u"Something go wrong: \n{}".format(e))
            pass


def write_to_csv(df, today_date):
    data_dir = os.path.join(cons.FILE_ARCHIVE, "news")
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    df['filter'] = "-" * 100
    df.to_csv(data_dir + "/" + today_date + ".csv", sep="\n", mode="a", header=False, encoding='utf-8', index=False)


def insert_to_mysql(lines):
    connection = s_utils.conn_mysql()
    try:
        with connection.cursor() as cursor:
            for index, row in lines.iterrows():
                sql = cons.insert_news.format(cons.news_table_name)
                cursor.execute(sql, (cons.today_str_Ymd,
                                     row['publish_time'],
                                     row['article_title'],
                                     row['article_text']))
        connection.commit()
    finally:
        connection.close()


if __name__ == '__main__':
    current_time = (datetime.datetime.now()).strftime(u'%H:%M')
    today_date = (datetime.datetime.now()).strftime("%Y%m%d")
    get_news = News()
    if current_time != u"23:50":
        contents = get_news.get_content(current_time)
        if len(contents) > 0:
            write_to_csv(contents, today_date)
