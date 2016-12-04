#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/4/16 9:18 AM

@author: IMYin

@File: ScrapyAnnouncement.py
"""


class ScrapyAnnouncement:
    # initial log
    def __init__(self, log_lev='INFO'):
        date_today = datetime.datetime.now().date()
        log_name = os.path.splitext(os.path.split(sys.argv[0])[1])[0]
        log_dir = Constants.TASK_LOG_PATH_BLACK_COFFEE
        self.today = date_today.strftime("%Y%m%d")
        log_dir += '/' + self.today
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass
                #        self.ignore_error = ignore_error
        mylog = JobLogging(log_name, log_dir)
        self.log = mylog.get_logger()
        self.log.info("ScrapyAnnouncement's log create success")

        # Connection
        def conn(self, url, data, proxies=None):
            session = requests.Session()
            # add the header
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML,like Gecko) Chrome',
                'Connection': 'Keep-Alive', 'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Encoding': 'gzip,deflate,sdch',
                'Accept': '*/*', 'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3', 'Cache-Control': 'max-age=0'}
            req = session.post(url, data, headers=headers)
            bsObj = BeautifulSoup(req.text, "lxml")
            return bsObj
