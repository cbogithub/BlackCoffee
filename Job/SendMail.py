#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/5/16 10:57 PM

@author: IMYin

@File: SendMail.py
"""
import datetime
import os
import smtplib
import sys
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

COMMASPACE = ', '
date_today = datetime.datetime.now().date()
today = date_today.strftime("%Y%m%d")
archive_path = cons.FILE_ARCHIVE
data_path = os.path.join(archive_path, today + 'selected.csv')
msg = MIMEMultipart()
msg['Subject'] = Header("from yous\' hero", 'utf-8')
df = pd.read_csv(data_path, index_col=False)
info = df.to_string().encode('utf-8')

msg.attach(MIMEText(info, 'plain', 'utf-8'))

with open(data_path) as f:
    mime = MIMEBase('file', 'csv', filename='selected.csv')
    mime.add_header('Content-Disposition', 'attachment', filename='selected.csv')
    mime.add_header('Content-ID', '<0>')
    mime.add_header('X-Attachment-Id', '0')
    mime.set_payload(f.read())
    encoders.encode_base64(mime)
    msg.attach(mime)

to_addr = cons.TO_ADDR
from_addr = cons.FROM_ADDR
password = cons.PASSWORD
# Send the email via our own SMTP server.
s = smtplib.SMTP(cons.SMTP_SERVER, 25)
s.login(from_addr, password)  # to login SMTP server.
s.sendmail(from_addr, COMMASPACE.join(to_addr), msg.as_string())
s.quit()
