from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time
import random
from pymongo import MongoClient
import re
from functools import wraps
import multiprocessing

"""
遇到个使用MP的问题：
如果使用MP，crawl_river里要纳入browser = webdriver.Firefox()和browser.close()，这一过程需要耗费额外时间
此外river_check()这一步也需要改写
----------------
需要VPN打开的网页加载速度慢，VPN速度是否支持4个网页同时正常加载
----------------
centos无法脚本启动的原因？
"""

browser = webdriver.Firefox()
client = MongoClient()
db = client['TCGA']
collection = db["record"]
collection2 = db["monitor"]

def conn_try_again(func, wait_time=3):
    __retries = 3
    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal __retries
        try:
            return func(*args, **kwargs)
        except:
            if __retries > 0:
                __retries -= 1
                time.sleep(wait_time)
                print("程序将在%s秒后重新运行" %(wait_time))
                return wrapper(*args, **kwargs)
            else:
                print("网络状况可能不佳")
                raise Exception
    return wrapper


def crawl_flop(start_url):
    browser.get(start_url)
    WebDriverWait(browser, 5)
    for item in browser.find_elements_by_css_selector("#main .Datapages-module__list___sOowd li"):
        label = item.text.split("(")
        data_type = label[0].rstrip()
        abbr = label[1].replace(") ", "")
        datasets_num = label[2].replace(" datasets)", "")
        turn_url = item.find_element_by_css_selector('a').get_attribute("href")
        collection.update_one({"data_type": data_type, "abbr": abbr, "datasets_num": datasets_num},{"$set": {"href": turn_url}}, upsert=True)
    print("主页面信息收集完毕")


@conn_try_again
def crawl_turn(turn_url, abbr):
    if not collection.find_one({"abbr": abbr, "finish": True}):
        browser.get(turn_url)
        wait = WebDriverWait(browser, 10)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main li")))
        except:
            collection.update_one({"abbr": abbr}, {"$set": {"finish": False}})
            print("%s抓取失败" % (turn_url))
            return
        for item in browser.find_elements_by_css_selector("#main .Datapages-module__datapages___177x8 li a"):
            river_url = item.get_attribute("href")
            collection2.update_one({"abbr": abbr, "href": river_url}, {"$set": {"finish": True}}, upsert=True)
        collection.update_one({"abbr": abbr}, {"$set": {"finish": True}}, upsert=True)
        print("%s的二级信息收集完毕" % (abbr))
        time.sleep(random.random() + 2)
    else:
        print("%s %s已纳入 collection" % (abbr, turn_url))
        return

def turn_check():
    while collection.find_one({"finish":False}):
        for item in collection.find({"finish": False}):
            turn_url = item["href"]
            abbr = item["abbr"]
            crawl_turn(turn_url, abbr)

@conn_try_again
def crawl_river(river_url, abbr):
    if not collection2.find_one({"abbr": abbr, "href": river_url, "finish": True,"download_url":{"$exists":True}}):
        browser.get(river_url)
        wait = WebDriverWait(browser, 10)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main span")))
            page_source = browser.page_source
            download_url = re.findall("href=\"(https://tcga.xenahubs.net/download/\S+)\">", page_source)[0]
        except:
            collection2.update_one({"abbr": abbr, "href": river_url}, {"$set": {"finish": False}})
            print("%s抓取失败" % (river_url))
            return
        collection2.update_one({"abbr": abbr, "href": river_url},{"$set": {"finish": True, "download_url": download_url}})
        print("%s抓取成功" % (download_url))
        time.sleep(random.random() + 2)
    else:
        print("%s %s已纳入 collection2" % (abbr, river_url))
        return

def river_check():
    while collection2.find_one({"finish":False}):
        for item in collection2.find({"finish": False}):
            river_url = item["href"]
            abbr = item["abbr"]
            crawl_river(river_url, abbr)

if __name__ == "__main__":
    start_url = "https://xenabrowser.net/datapages/?hub=https://tcga.xenahubs.net:443"
    crawl_flop(start_url)
    for item in collection.find():
        turn_url = item["href"]
        abbr = item["abbr"]
        crawl_turn(turn_url, abbr)
    turn_check()
    for item in collection2.find():
        river_url = item["href"]
        abbr = item["abbr"]
        crawl_river(river_url, abbr)
    river_check()
