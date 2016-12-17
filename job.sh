#!/bin/bash

mypath="$(cd "$(dirname "$0")"; pwd)"
cd $mypath
cd Scrapy
python ScrapyInterpretation.py

python ScrapyAnnouncement.py

cd ../Job
python SelectStrategy.py

python SendMail.py
