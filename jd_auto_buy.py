# !/home/imyin/python_env/newspaper_python3/bin/python
# -*- coding: utf-8 -*-

"""
Create on 11/6/17 4:12 PM

@auther: imyin

@File: jd_auto_buy
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
        buy = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "choose-btn-ko")))
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
        submit = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "checkout-submit")))
    except Exception as error:
        print('抢购不成功\n{}'.format(error))
        driver.back()
        return False
    else:
        submit.click()
        return True


def wait_for_pay(driver):
    retry_times = 0
    try:
        # 抢购界面
        while wait_for_submit(driver) is False and retry_times < 20:
            time.sleep(0.01)
            retry_times += 1
        # 提交订单
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "saveConsigneeTitleDiv")))
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.LINK_TEXT, "保存支付及配送方式"))).click()
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "order-submit"))).click()
        # 进入付款界面
        WebDriverWait(driver, 2, 0.1).until(EC.presence_of_element_located((By.LINK_TEXT, "立即支付")))
    except Exception as error:
        print("抢单无效，重新抢购\n{}".format(error))
        driver.back()
        driver.back()
        return False
    else:
        return True


if __name__ == '__main__':
    time_for_buy = '2017-11-09 22:00:00.07'  # 抢购时间
    retry = 0  # 尝试次数

    driver = e_utils.simulate_web_with_display()
    driver.get(cons.jd_qualification)
    # 登录账号
    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.LINK_TEXT, "账户登录"))).click()
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
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "btn-buy"))).click()
        while wait_for_pay(driver) is False and retry < 20:
            time.sleep(0.01)
            retry += 1
    except Exception as e:
        print("请在页面上登录京东")
        raise
    print('下单完成，请付款...')
    # 付款
    # password = WebDriverWait(driver, 6).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-shortPwd-input")))
    # password[0].send_keys(cons.jd_password[0])
    # password[1].send_keys(cons.jd_password[1])
    # password[2].send_keys(cons.jd_password[2])
    # password[3].send_keys(cons.jd_password[3])
    # password[4].send_keys(cons.jd_password[4])
    # password[5].send_keys(cons.jd_password[5])
    # driver.find_elements_by_link_text('立即支付').click()
    # driver.close() # 为保证完成订单提交动作，就不要关闭driver了，付款完成后可自行关闭
