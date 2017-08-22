#!/home/imyin/python_env/newspaper_python3/bin python3
# -*- coding: utf-8 -*-

"""
Created on  3/3/17 11:07 PM

@author: IMYin

@File: constants.py
"""
import datetime
import time

import numpy as np
import pymysql

# define time.
today_time = datetime.date.today()
today_str_Ymd = today_time.strftime(u'%Y-%m-%d')
yesterday_str_md = (today_time - datetime.timedelta(days=1)).strftime(u"%m-%d")

PARENT_PATH = u"/home/imyin/myProject/gitWorkSpace/BlackCoffee"

TASK_LOG_PATH = PARENT_PATH + u"/Logs/logs"
FILE_ARCHIVE = PARENT_PATH + u"/Data/trade"
ANALYSIS_PATH = PARENT_PATH + u"/Analysis"
JOB_PATH = PARENT_PATH + u"/Job"
SCRAPY_PATH = PARENT_PATH + u"/Scrapy"

RAW_URL_OF_INTERPRETATION = u"http://ggjd.cnstock.com/gglist/search/jgjd/"
RAW_URL_OF_ANNOUNCEMENT = u"http://xinpi.cnstock.com/Search.aspx"
RAW_URL_OF_SH_600 = u"http://www.sse.com.cn/disclosure/listedinfo/announcement/#panel-1"
RAW_URL_OF_SZ_300 = u"http://disclosure.szse.cn/m/search0425.jsp"
NEWS_RESOURCE = u"http://ggjd.cnstock.com/gglist/search/qmtbbdj/"

# env path
LOGGING_PATH = PARENT_PATH + u"/Logs"
ANALYSIS_PATH = PARENT_PATH + u"/Analysis"
PLOT_RESULT = PARENT_PATH + u"/Data/plot"
PDF_DOWNLOADED = PARENT_PATH + u"/Data/pdf"
AN_PDF_DOWNLOADED = PARENT_PATH + u"/Data/an_pdf"

# sql sentences
# inter
up_codes_sql = (
    u"SELECT DISTINCT(publish_time),code,title,pdf_url FROM {} WHERE publish_time LIKE '{}%' AND content LIKE '%{}%'")
insert_inter_table_sql = (u"INSERT INTO {} (publish_time, code, title, content, pdf_url) VALUES (%s, %s, %s, %s, %s)")

# announcements
content_dict = (
    u"SELECT DISTINCT(publish_time),title,content FROM {} WHERE publish_time LIKE '{}%' AND content LIKE '%{}%'")
insert_announ_table_sql = (u"INSERT INTO {} (publish_time, code, content, pdf_url) VALUES (%s, %s, %s, %s)")
conn_table_sql = (u"SELECT content,publish_time,code,pdf_url FROM {} WHERE publish_time = '{}' ")

# news
insert_news = (u"INSERT INTO {} (date, collect_time, title, content) VALUES (%s, %s, %s, %s)")
select_news_mail = (u"SELECT title, content from {} where date = '{}' AND collect_time = '{}'")


insert_useful_trade_sql = (
    u"INSERT INTO {} (datetime, code, open, close, high, low, volume) VALUES( %s, %s, %s, %s, %s, %s, %s)")

# Define email relate.
TO_ADDR = [u"imyin127@163.com"]
FROM_ADDR = u"txcg777@sina.com"
PASSWORD = u"BiuBiu777"
SMTP_SERVER = u"smtp.sina.com"

# Table names
current_time_Y = time.strftime(u'%Y', time.localtime(time.time()))
announ_table_name = u"announcement_" + current_time_Y
inter_table_name = u"interpretation_" + current_time_Y
usefule_table_name = u"useful_trade"
news_table_name = u"news_everyday_" + current_time_Y

# Mysql connection information.
mysql_user = u"stock"
mysql_passwd = u"stock"
mysql_host = u"localhost"
stock_db = u"stock"

# symbol
UP = u"看多"
DOWN = u"看空"
NOTHING = u"看平"

# To split
SPLIT_ITEM1 = u","
SPLIT_ITEM2 = u"_"
SPLIT_ITEM3 = u";"
SPLIT_ITEM4 = u"."
SPLIT_ITEM5 = u"+"
SPLIT_ITEM6 = u"/"

# headers
HEADERS = {
    u'Connection': u'Keep-Alive', u'Accept-Language': u'zh-CN,zh;q=0.8', u'Accept-Encoding': u'gzip,deflate,sdch',
    u'Accept': u'*/*', u'Accept-Charset': u'GBK,utf-8;q=0.7,*;q=0.3', u'Cache-Control': u'max-age=0'}

# user agents.
my_user_agent = [
    u'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    u'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    u'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    u'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    u'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    u'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    u'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    u'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    u'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    u'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    u'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    u'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)']


def get_headers():
    HEADERS[u'User-Agent'] = np.random.choice(my_user_agent)
    return HEADERS


def conn_mysql():
    """
    To connect the mysql.
    Attentions: charset is a important parameter.

    :return: connection
    """
    connection = pymysql.connect(host=mysql_host,
                                 user=mysql_user,
                                 password=mysql_passwd,
                                 db=stock_db,
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
