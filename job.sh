#!/bin/bash

export PYTHON_HOME="/home/imyin/anaconda2/bin/python"

mypath="$(cd "$(dirname "$0")"; pwd)"
cd $mypath

# crawl contents from web.
cd Scrapy
python ScrapyInterpretation.py
python ScrapyAnnouncement.py

# plot the result
cd ../Analysis
python quota_analysis.py >> analysis.log

# send mail
cd ../Job
python SendMail.py  >> ../Analysis/analysis.log
#python SelectStrategy.py
