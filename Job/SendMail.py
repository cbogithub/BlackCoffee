#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/5/16 10:57 PM

@author: IMYin

@File: SendMail.py
"""
import os
import smtplib
import sys
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# must use absolute path.
import Utils.scrapy_utils

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import constants as cons

today_time = sys.argv[1]
today_str_md = sys.argv[2]

plot_data_path = os.path.join(cons.PLOT_RESULT, today_time)
pdf_data_path = os.path.join(cons.PDF_DOWNLOADED, today_time)
os.chdir(plot_data_path)
COMMASPACE = cons.SPLIT_ITEM1
for root, dirs, files in os.walk(plot_data_path):
    file_names = files


def get_content_dict():
    connection = Utils.scrapy_utils.conn_mysql()
    try:
        with connection.cursor() as cursor:
            sql = (cons.content_dict.format(cons.inter_table_name, today_str_md, cons.UP))
            x = cursor.execute(sql)
            result = cursor.fetchmany(x)
            # Collect the contents of article.
            return {item[u'title']: item[u'content'] for item in result}
    finally:
        connection.close()


def run_send(file_names):
    dict_contents = get_content_dict()
    msg = MIMEMultipart()
    msg[u'Subject'] = Header(u"Today has {} messages.".format(len(file_names)), u'utf-8')

    for item in file_names:
        # Embed the picture in text.
        mail_msg = u'<p>{}<br>{}</p><p><img src="cid:{}"></p>'.format(item, dict_contents[item[6:-4]], item)
        msg.attach(MIMEText(mail_msg, u'html', u'utf-8'))
        fp = open(item, u'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header(u'Content-ID', u'<{}>'.format(item[:6]))
        msg.attach(msgImage)

    # Add attachment into e-mail.
    part = MIMEApplication(open(pdf_data_path + u".zip", u'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=today_time + u".zip")
    msg.attach(part)

    to_addr = cons.TO_ADDR
    from_addr = cons.FROM_ADDR
    password = cons.PASSWORD
    # Send the email via our own SMTP server.
    s = smtplib.SMTP(cons.SMTP_SERVER, 25)
    s.login(from_addr, password)  # to login SMTP server.
    s.sendmail(from_addr, to_addr, msg.as_string())
    s.quit()


run_send(file_names)
