CREATE DATABASE stock CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

GRANT ALL ON stock.* TO 'stock'@'localhost';

USE stock;

CREATE TABLE announcement_201612(
publish_time    CHAR(10),
code            CHAR(6),
content         TEXT,
pdf_url         VARCHAR(500)
);

CREATE TABLE interpretation201612(
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
high            FLOAT(8,5),
low             FLOAT(8,4),
volume          FLOAT(8,4)
);


-- trade_cal()
