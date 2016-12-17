#!/bin/bash

# Define the variable of time to create table.
current_time=`date +%Y%m`


# Define the variables of mysql.
MYSQL=`which mysql`
database="stock"
table_annou="announcement"
table_inter="interpretation"
passwd="stock"
host="localhost"

my_path=`dirname $PWD`
cd $my_path

# Create table
${MYSQL} -u ${database} -p${passwd} -h ${host} <<EOF 

use stock;
CREATE TABLE IF NOT EXISTS ${table_annou}_${current_time}(
publish_time    CHAR(10),
code            CHAR(6),
content         TEXT,
pdf_url         VARCHAR(500)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS ${table_inter}_${current_time}(
publish_time    CHAR(12),
code            CHAR(6),
title           TEXT,
content         TEXT,
pdf_url         VARCHAR(500)
) DEFAULT CHARSET=utf8;

exit

EOF

if [ $? -eq 0 ]; then
echo "Table created..." >> ./Logs/logs/${current_time}_mysql.log
echo "Table name are ${table_annou}_${current_time} and ${table_inter}_${current_time}." >> ./Logs/logs/${current_time}_mysql.log
else
echo "Table create failed..." >> ./Logs/logs/${current_time}_mysql.log
fi
