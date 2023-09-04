# -*- coding: utf-8 -*-

# 노원구장애인가족지원센터

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import date, timedelta, datetime
from save_csv import saveCsv
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from main import constants

# 마지막 크롤링 날짜
lastCrawlDate = constants['crawl']['latest_date']
lastCrawlDate = datetime.strptime(lastCrawlDate, '%Y-%m-%d')

sites = []
regions = []
categories = []
disabilityTypes = []
titles = []
dates = []
contents = []
contentLinks = []
images = []

def strToDate(strDate):
    strDate = strDate.replace('.', '-')
    dateTime = datetime.strptime(strDate, '%Y-%m-%d')
    return dateTime


options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("enable-automation")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options) 

#크롬 드라이버에 url 주소 넣고 실행
driver.get('http://www.xn--o39az0a12gluvn1ebncda65ksl71ekzf4w4a.kr/program')

# 페이지가 완전히 로딩되도록 3초동안 기다림
time.sleep(3)

postList = driver.find_element(By.CLASS_NAME, 'gall_list').find_elements(By.CLASS_NAME, 'gall_item')[:18]

for post in postList:
    link = post.find_element(By.TAG_NAME, 'a')
    title = post.find_element(By.CLASS_NAME, 'gall_txt').text
    linkText = link.get_attribute('href')
    
    link.click()
    time.sleep(2)

    uploadDate = driver.find_element(By.CLASS_NAME, 'bo_date').text
    uploadDate = strToDate(uploadDate)

    if uploadDate > lastCrawlDate:
        content = driver.find_element(By.CLASS_NAME, 'bo_info').text

        imgs = []

        try:
            imgList = driver.find_element(By.CLASS_NAME, 'bo_v_con').find_elements(By.TAG_NAME, 'a')
            for idx, img in enumerate(imgList):
                img.click()
                time.sleep(2)
                imgLink = img.find_element(By.TAG_NAME, 'img').get_attribute('src')
                imgs.append(imgLink)
        except:
            print('이미지 없음')

        sites.append('노원구장애인가족지원센터')
        regions.append(['서울시', '노원구'])
        categories.append(None)
        disabilityTypes.append(None)
        titles.append(title)
        dates.append(uploadDate)
        contents.append(content)
        #originalLinks.append(link)-
        contentLinks.append(linkText)
        images.append(imgs)
        
        driver.back()
    else:
        break

saveCsv('nowon_family_support_center', sites, regions, categories, disabilityTypes, titles, dates, contents, contentLinks, images)