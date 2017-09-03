#!/usr/bin/env python
# encoding: utf-8
"""
@version: ??
@author: 哎哟卧槽
@license: Apache Licence 
@file: login.py
@time: 2017/9/3 2:42
"""
import os
import time
import json
from selenium import webdriver
from selenium.webdriver import ActionChains
import requests
from lxml import etree


from bcy.config import *

session = requests.Session()

login_url = 'https://bcy.net/public/dologin'
post_url = 'https://bcy.net/coser/reply/publish'

login_data = {
    "email": login_user,
    "password":	login_password,
    "remember":	"1"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Referer": "https://bcy.net/login"
    }


def web_driver_login():
    cookies = {}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    if headers:
        driver = webdriver.Chrome(executable_path=browser_path, chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome(executable_path=browser_path)
    driver.get('https://bcy.net/login')
    time.sleep(2)
    driver.find_element_by_xpath("./*//input[@name='email']").clear()
    driver.find_element_by_xpath("./*//input[@name='email']").send_keys(login_user)
    driver.find_element_by_xpath("./*//input[@name='password']").clear()
    driver.find_element_by_xpath("./*//input[@name='password']").send_keys(login_password)
    driver.find_element_by_xpath("./*//input[@value='登 录']").click()
    time.sleep(5)
    tree = etree.HTML(driver.page_source)
    title = ''.join(tree.xpath('./*//title/text()'))
    if '我的首页' in title:
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            for item in driver.get_cookies():
               cookies[item.get('name')] = item.get('value')
            f.write(json.dumps(cookies))
            print('获取cookie成功：{}'.format(cookies))
            driver.close()
            return True
    else:
        print('没有正确的获取到cookie')
        driver.close()


def post(cp_id, rp_id):
    with open('cookies.txt', 'r', encoding='utf-8') as f:
        cookies = json.loads(f.read())
    post_data = {
        "publish_type": "1",
        "content": post_content,
        "cp_id": cp_id,
        "rp_id": rp_id
    }
    response = session.post(post_url, data=post_data, headers=headers, cookies=cookies)
    if response.json().get('status') == 1:
        print('评论发布成功')

    pass

if __name__ == '__main__':
    web_driver_login()
    # login()