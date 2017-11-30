# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 11/30/17 2:18 PM

@auther: imyin

@File: car4s
"""
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import constants as cons
from Utils import east_money_utils as e_utils


def bs_obj(contents):
    bsObj = BeautifulSoup(contents.get_attribute('innerHTML'), 'lxml')
    return bsObj


def info(retry=10):
    information = {'store_name': [], 'main_brand': [], 'phone': [], 'address': [], 'field': []}
    driver = e_utils.simulate_web_with_display()
    driver.get(cons.cars_store_bj)
    page_num = 44
    for page in range(1, page_num + 1):
        bsObj = bs_obj(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "list-box"))))
        for item in bsObj.find_all('li', {'class': 'list-item'}):
            contents = item.find_all('li')
            information['store_name'].append(contents[0].find('a', {'class': 'link'}).text)
            information['main_brand'].append(contents[1].find('em').text)
            information['phone'].append(contents[2].find('span', {'class': 'tel'}).text)
            information['address'].append(contents[3].find('span', {'class': 'info-addr'}).text)
            information['field'].append(contents[2].find('span', {'class': 'floating'}).text)
        for i in range(retry):
            try:
                time.sleep(2)
                if page != page_num:
                    driver.find_element_by_xpath(cons.EAST_MONEY_NEXT_PAGE).click()
                    break
            except Exception as e:
                time.sleep(0.5)
                print(e)
                pass
    driver.close()
    df = pd.DataFrame(information, columns=['store_name', 'main_brand', 'phone', 'address', 'field'])
    df.drop_duplicates(inplace=True)
    df.to_csv('/home/imyin/Desktop/car4s.csv', encoding='utf-8', index=False)


if __name__ == '__main__':
    info()
