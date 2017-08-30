#!/bin/bash

# Define the variable of time to create table.
current_time=`date +%Y%m`
#current_time=201709
current_year=`date +%Y`

# Define the variables of mysql.
MYSQL=`which mysql`
database="stock"
table_annou="announcement"
table_inter="interpretation"
table_east_money="east_money_ann"
research_report="sina_research_report"
passwd="stock"
host="localhost"

my_path=`dirname $PWD`
cd $my_path

# Create table
${MYSQL} -u ${database} -p${passwd} -h ${host} <<EOF >> ./Logs/logs/${current_year}_mysql.log

use stock;
#CREATE TABLE IF NOT EXISTS ${table_annou}_${current_time}(
#publish_time    CHAR(10),
#code            CHAR(6),
#content         TEXT,
#pdf_url         VARCHAR(500)
#) DEFAULT CHARSET=utf8;
#
#CREATE TABLE IF NOT EXISTS ${table_inter}_${current_time}(
#publish_time    CHAR(12),
#code            CHAR(6),
#title           TEXT,
#content         TEXT,
#pdf_url         VARCHAR(500)
#) DEFAULT CHARSET=utf8;

CREATE TABLE ${table_east_money}_${current_time}(
securitycode          VARCHAR(6)    COMMENT '证券代码',
securityfullname      VARCHAR(30)   COMMENT '证券的全名称',
noticetitle           VARCHAR(200)  COMMENT '公告的标题',
noticedate            VARCHAR(10)   COMMENT '公告发布时间',
securitytype          VARCHAR(10)   COMMENT '证券类型',
columnname            VARCHAR(50)   COMMENT '公告类型',
url                   VARCHAR(400)  COMMENT '公告的url地址'
) COMMENT='表注释'
DEFAULT CHARSET=utf8;

CREATE TABLE ${research_report}_${current_year}(
title                 VARCHAR(300)     COMMENT '研报标题',
article_url           VARCHAR(300)     COMMENT '研报内容的url',
type                  VARCHAR(100)     COMMENT '研报类型',
publish_time          VARCHAR(10)      COMMENT '发布时间',
institution           VARCHAR(100)     COMMENT '发布机构',
author                VARCHAR(100)     COMMENT '作者',
content               VARCHAR(5000)    COMMENT '研报内容'
) COMMENT='表注释'
DEFAULT CHARSET=utf8;

exit

EOF

if [ $? -eq 0 ]; then
echo "Table created..." >> ./Logs/logs/${current_year}_mysql.log
echo "Table name is ${table_east_money}_${current_time}." >> ./Logs/logs/${current_year}_mysql.log
else
echo "Table create failed... ${current_time}" >> ./Logs/logs/${current_year}_mysql.log
fi