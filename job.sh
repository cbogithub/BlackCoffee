#!/bin/bash

TODAY_DATE=`date +%Y-%m-%d`
export PYTHON_HOME="/home/imyin/anaconda2/bin/python"

my_path="$(cd "$(dirname "$0")"; pwd)"
cd ${my_path}

# crawl contents from web.
cd Scrapy
python ScrapyInterpretation.py
python ScrapyAnnouncement.py

# plot the result
cd ../Analysis
python quota_analysis.py ${TODAY_DATE} >> analysis.log 2>&1

# send mail
cd ../Job
python SendMail.py ${TODAY_DATE}
#python SelectStrategy.py
