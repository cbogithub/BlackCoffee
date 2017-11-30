# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 11/9/17 4:46 PM

@auther: imyin

@File: test_jd
"""

import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import constants as cons
from Utils import east_money_utils as e_utils


def wait_for_buy(driver):
    try:
        buy = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "btn-reservation")))
    except Exception as error:
        print("没有抢购键\n{}".format(error))
        driver.refresh()
        return False
    else:
        buy.click()
        return True


def wait_for_submit(driver):
    retry_times = 0
    try:
        while wait_for_buy(driver) is False and retry_times < 20:
            time.sleep(0.01)
            retry_times += 1
        submit = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "GotoShoppingCart")))
    except Exception as error:
        print('抢购不成功\n{}'.format(error))
        driver.back()
        return False
    else:
        submit.click()
        return True


if __name__ == '__main__':
    time_for_buy = '2017-11-09 16:00:00.07'  # 抢购时间
    retry = 0 # 尝试次数

    driver = e_utils.simulate_web_with_display()
    driver.get(cons.jd_qualification)

    # 登录账号
    WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.LINK_TEXT, "账户登录"))).click()
    driver.find_element_by_id('loginname').send_keys(cons.jd_user)
    driver.find_element_by_id('nloginpwd').send_keys(cons.jd_password)
    driver.find_element_by_id('loginsubmit').click()

    # 设置等待时间
    # start_time = datetime.now()
    # end_time = datetime.strptime(time_for_buy, '%Y-%m-%d %H:%M:%S.%f')
    # sleep_time = (end_time - start_time).total_seconds()
    # print("{} 秒后将自动购买。".format(sleep_time))
    # time.sleep(sleep_time)
    # driver.refresh()

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "btn-buy"))).click()
        while wait_for_submit(driver) is False and retry < 20:
            time.sleep(0.01)
            retry += 1
    except Exception as e:
        print("请在页面上登录京东")
        raise

    # 提交订单
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "submit-btn"))).click()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "checkout-submit"))).click()
    # WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "saveConsigneeTitleDiv")))
    # WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.LINK_TEXT, "保存支付及配送方式"))).click()
    # WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "order-submit"))).click()

    # 付款
    password = WebDriverWait(driver, 6).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-shortPwd-input")))
    password[0].send_keys(cons.jd_password[0])
    password[1].send_keys(cons.jd_password[1])
    password[2].send_keys(cons.jd_password[2])
    password[3].send_keys(cons.jd_password[3])
    password[4].send_keys(cons.jd_password[4])
    password[5].send_keys(cons.jd_password[5])
    driver.find_elements_by_link_text('立即支付').click()

    print('下单完成，请付款...')
    # driver.close() # 为保证完成订单提交动作，就不要关闭driver了，付款完成后可自行关闭