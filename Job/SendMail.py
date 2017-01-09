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
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

today_time = sys.argv[1]
data_path = os.path.join(cons.MACD_PLOT_RESULT, today_time)
os.chdir(data_path)
COMMASPACE = cons.SPLIT_ITEM1
for root, dirs, files in os.walk(data_path):
    file_names = files


def run_send(file_names):
    msg = MIMEMultipart()
    msg[u'Subject'] = Header(u"from yous\' hero", u'utf-8')

    for item in file_names:
        mail_msg = """
        <p>""" + item + """</p><p><img src="cid:""" + item + """"></p>
        """
        msg.attach(MIMEText(mail_msg, u'html', u'utf-8'))
        fp = open(item, u'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header(u'Content-ID', u'<' + item + u'>')
        msg.attach(msgImage)

    to_addr = cons.TO_ADDR
    from_addr = cons.FROM_ADDR
    password = cons.PASSWORD
    # Send the email via our own SMTP server.
    s = smtplib.SMTP(cons.SMTP_SERVER, 25)
    s.login(from_addr, password)  # to login SMTP server.
    s.sendmail(from_addr, to_addr, msg.as_string())
    s.quit()

run_send(file_names)
