CREATE DATABASE stock CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

GRANT ALL ON stock.* TO 'stock'@'localhost';

USE stock;

CREATE TABLE announcement_2017(
publish_time    CHAR(10),
code            CHAR(6),
content         TEXT,
pdf_url         VARCHAR(500)
);

CREATE TABLE interpretation_2017(
publish_time    CHAR(10),
code            CHAR(6),
content         TEXT,
pdf_url         VARCHAR(500)
);

CREATE TABLE useful_trade(
datetime        CHAR(10),
code            CHAR(6),
open            FLOAT(8,4),
close           FLOAT(8,4),
high            FLOAT(8,4),
low             FLOAT(8,4),
volume          FLOAT(12,6)
);

CREATE TABLE news_everyday_2017(
date            CHAR(10),    
collect_time    CHAR(6),     
title           VARCHAR(200),
content         VARCHAR(5000)
);

CREATE TABLE east_money_ann_201708(
securitycode          VARCHAR(6)    COMMENT '证券代码',
securityfullname      VARCHAR(30)   COMMENT '证券的全名称',
noticetitle           VARCHAR(200)  COMMENT '公告的标题',
noticedate            VARCHAR(10)   COMMENT '公告发布时间',
securitytype          VARCHAR(10)   COMMENT '证券类型',
columnname            VARCHAR(50)   COMMENT '公告类型',
url                   VARCHAR(400)  COMMENT '公告的url地址'
) COMMENT='表注释';

-- trade_cal()
