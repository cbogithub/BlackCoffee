# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 8/26/17 2:01 PM

@auther: imyin

@File: east_money_utils
"""

import re
import constants as cons
from selenium import webdriver
from bs4 import BeautifulSoup


# 对json进行正则匹配
def re_lst(contents):
    contents = re.sub("\n+", "", contents)
    contents = re.sub(" +", "", contents)
    contents = re.search("defjson.*charset", contents).group()
    contents = contents[17:-8]
    contents = re.sub(cons.EAST_MONEY_ANN_BADWORD1, "", contents)
    contents = re.sub(cons.EAST_MONEY_ANN_BADWORD2, "", contents)
    contents = re.sub(cons.EAST_MONEY_ANN_BADWORD3, "", contents)
    find_lst = (re.findall("(\".*?\"):(\".*?\"|\d{1,30}|\w{1,10})", contents))[:-1]
    return find_lst


# 将list进行分组（没有用到）
def group_list(line):
    init_i = 0
    result = []
    for i, item in enumerate(line):
        if u"http://" in item:
            result.append(line[init_i:i + 1])
            init_i = i + 1
    return result


# 将list进行分组
def mk_dict(tuples):
    init_1 = 0
    result = []
    for i, item in enumerate(tuples):
        if u"http://" in item[1]:
            result.append(tuples[init_1:i + 1])
            init_1 = i + 1
    for line in result:
        yield line


def simulate_web():
    driver = webdriver.Chrome(cons.CHROME_PATH)
    return driver


def _get_bsObj(driver):
    contents = driver.find_element_by_class_name("framecontent").find_element_by_tag_name("tbody")
    bsObj = BeautifulSoup(contents.get_attribute('innerHTML'), 'lxml')
    return bsObj


def get_contents(driver):
    bsObj = _get_bsObj(driver=driver)
    contents = bsObj.find_all("tr")
    for line in contents:
        yield line


if __name__ == '__main__':
    words = "hello"
    result = re_lst(words)
    rr = mk_dict(result)
    # print(rr)
    for item in rr:
        print(item)
