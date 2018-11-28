#centos 版
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time
import random
from pymongo import MongoClient
import re

"""
用mongodb，分层次运行

会遇到加载失败，需要手动更新的时候：记录在一个collection里面，然后先跳过再回头看
"""

display = Display(visible=0, size=(800, 600))
display.start()
browser = webdriver.Firefox()

client = MongoClient()
db = client['TCGA']
collection = db["record"]
collection2 = db["monitor"]

start_url = "https://xenabrowser.net/datapages/?hub=https://tcga.xenahubs.net:443"

def start_crawl(start_url):
    crawl_flop(start_url)
    for item in collection.find():
        turn_url = item["href"]
        abbr = item["abbr"]
        crawl_turn(turn_url,abbr)
    #检查
    for item in collection2.find():
        river_url = item["href"]
        abbr = item["abbr"]
        crawl_river(river_url,abbr)
    #检查
    display.stop()

def crawl_flop(start_url):
    browser.get(start_url)
    wait = WebDriverWait(browser,5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#main .Datapages-module__list___sOowd")))
    for item in browser.find_elements_by_css_selector("#main .Datapages-module__list___sOowd li"):
        label = item.text.split("(")
        data_type = label[0].rstrip()
        abbr = label[1].replace(") ", "")
        datasets_num = label[2].replace(" datasets)", "")
        turn_url = item.find_element_by_tag_name('a').get_attribute("href")
        collection.update({"data_type":data_type,"abbr":abbr,"datasets_num":datasets_num},{"$set":{"href":turn_url}},upsert=True)
    print("主页面信息收集完毕")

def crawl_turn(turn_url,abbr):
    browser.get(turn_url)
    wait = WebDriverWait(browser, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main")))
    except:
        collection.update({"abbr":abbr},{"$set":{"finish":False}})
        print("%s抓取失败" %(turn_url))
        return
    for item in browser.find_elements_by_css_selector("#main .Datapages-module__datapages___177x8 li"):
        river_url = item.find_element_by_tag_name('a').get_attribute("href")
        print(river_url)
        collection2.update({"abbr":abbr},{"$set":{"href":river_url}},upsert=True)
    collection.update({"abbr": abbr}, {"$set": {"finish": True}},upsert=True)
    print("%s的二级信息收集完毕" %(abbr))
    time.sleep(random.random() + 2)

def crawl_river(river_url,abbr):
    browser.get(river_url)
    wait = WebDriverWait(browser, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
    except:
        collection2.update({"abbr":abbr,"href":river_url},{"$set":{"finish":False}})
        print("%s抓取失败" % (river_url))
        return
    source_page = browser.page_source
    download_url = re.findall("href=\"(https://tcga.xenahubs.net/download/\S+)\">", source_page)[0]
    collection2.update({"abbr": abbr, "href": river_url}, {"$set": {"finish": True}})
    print("%s抓取成功" %(river_url))
    time.sleep(random.random() + 2)

start_crawl(start_url)
