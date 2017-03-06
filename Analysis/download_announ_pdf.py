#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 3/1/17 7:53 PM

@author: imyin

@File: download_announ_pdf
"""

import os
import sys
import time
import datetime
from multiprocessing.dummy import Pool as ThreadPool
from urllib import urlretrieve

# must use absolute path..
CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

today_str_Ymd = sys.argv[1]

an_pdf_data_path = os.path.join(cons.AN_PDF_DOWNLOADED, today_str_Ymd)
if not os.path.exists(an_pdf_data_path):
    os.mkdir(an_pdf_data_path)


def get_announ_codes():
    connection = cons.conn_mysql()
    try:
        with connection.cursor() as cursor:
            sql = (cons.conn_table_sql.format(cons.announ_table_name, today_str_Ymd))
            x = cursor.execute(sql)
            result = cursor.fetchmany(x)
            codes = {item['content']: item[u'pdf_url']
                                      + cons.SPLIT_ITEM5
                                      + item[u'content'] for item in result}
    finally:
        connection.close()
        return codes


def download_it(info, retry=10):
    words_announ = announ_codes[info].split(cons.SPLIT_ITEM5)
    an_file_name = words_announ[1]
    an_pdf = words_announ[0]
    download_path = an_pdf_data_path + u"/" + an_file_name + u".pdf"
    for _ in range(retry):
        time.sleep(0.01)
        urlretrieve(an_pdf, download_path)
        if os.path.getsize(download_path) / 1024 > 2.0:
            break


announ_codes = get_announ_codes()

# for item in announ_codes:
#     download_it(item)
time1 = datetime.datetime.now()
pool = ThreadPool(8)
results = pool.map(download_it, announ_codes)
pool.close()
pool.join()
time2 = datetime.datetime.now()
print (u"\nIt costs {} sec to run it.\nToday is {}...".format((time2 - time1).total_seconds(), today_str_Ymd))