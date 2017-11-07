# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 11/6/17 4:12 PM

@auther: imyin

@File: jd_auto_buy
"""

import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def simulate_web_with_display(chrome_path):
    driver = webdriver.Chrome(chrome_path)
    return driver


if __name__ == '__main__':
    jd_qualification = 'https://yushou.jd.com/member/qualificationList.action'  # 预约列表
    time_for_buy = '2017-11-07 10:08:20.05'  # 抢购时间
    products_num = 10  # 抢购数量
    chrome_path = '/usr/local/bin/chromedriver' # chrome driver 安装路径
    retry = 5

    driver = simulate_web_with_display(chrome_path)
    driver.get(jd_qualification)

    start_time = datetime.now()
    end_time = datetime.strptime(time_for_buy, '%Y-%m-%d %H:%M:%S.%f')
    sleep_time = (end_time - start_time).total_seconds()
    print("{} 秒后将自动购买。".format(sleep_time))
    time.sleep(sleep_time)

    for i in range(retry):
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btn-buy")))[0].click()
            for j in range(1, products_num + 1):
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "btn-reservation"))).click()
                    pay_it = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "GotoShoppingCart")))
                    print("已添加至购物车 {} 台".format(j))
                    if j != products_num:
                        driver.back()
                    else:
                        pay_it.click()
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "submit-btn"))).click()
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "checkout-submit"))).click()
                except Exception as e:
                    print("购买失败：{}".format(e))
            break
        except Exception as e:
            print("请在页面上登录京东")

    # driver.close() # 为保证完成订单提交动作，就不要关闭driver了，付款完成后可自行关闭
