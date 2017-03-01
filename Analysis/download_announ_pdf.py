#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 3/1/17 7:53 PM

@author: imyin

@File: download_announ_pdf
"""

import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
from urllib import urlretrieve

# must use absolute path..
CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

today_str_Ymd = sys.argv[1]
tomorrow_str_Ymd = sys.argv[2]

an_pdf_data_path = os.path.join(cons.AN_PDF_DOWNLOADED, today_str_Ymd)
if not os.path.exists(an_pdf_data_path):
    os.mkdir(an_pdf_data_path)


def get_announ_codes():
    connection = cons.conn_mysql()
    try:
        with connection.cursor() as cursor:
            sql = (cons.conn_table_sql.format(cons.announ_table_name, tomorrow_str_Ymd))
            x = cursor.execute(sql)
            result = cursor.fetchmany(x)
            codes = {item['content']: item[u'pdf_url']
                                   + cons.SPLIT_ITEM5
                                   + item[u'content'] for item in result}
    finally:
        connection.close()
        return codes

def download_it(info):
    words_announ = announ_codes[info].split(cons.SPLIT_ITEM5)
    an_file_name = words_announ[1]
    an_pdf = words_announ[0]
    urlretrieve(an_pdf, an_pdf_data_path + u"/" + an_file_name + u".pdf")

announ_codes = get_announ_codes()

# for item in announ_codes:
#     download_it(item)
pool = ThreadPool(32)
results = pool.map(download_it, announ_codes)
pool.close()
pool.join()

