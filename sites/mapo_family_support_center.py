# -*- coding: utf-8 -*-

# 마포장애인가족지원센터

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
driver.get('http://mp.dfsc.or.kr/41')

# 페이지가 완전히 로딩되도록 3초동안 기다림
time.sleep(3)

index = 0

while index < 10: 
    post = driver.find_element(By.CLASS_NAME, 'li_board').find_elements(By.CLASS_NAME, 'li_body')[index]
    uploadDate = post.find_element(By.CLASS_NAME, 'time').get_attribute('title').split(' ')[0]
    uploadDate = strToDate(uploadDate)

    if uploadDate > lastCrawlDate:
        link = post.find_element(By.CLASS_NAME, 'list_text_title')
        title = link.text
        linkText = link.get_attribute('href')
        
        link.send_keys(Keys.ENTER)
        time.sleep(2)
  
        content = driver.find_element(By.CLASS_NAME, 'board_txt_area').find_element(By.CLASS_NAME, 'margin-top-xxl')

        # content 내용 없을 경우애 대한 예외처리
        if not content:
            content = ''

        imgs = []

        try:
            imgList = content.find_elements(By.TAG_NAME, 'img')
            for idx, img in enumerate(imgList):
                imgLink = img.get_attribute('src')
                imgs.append(imgLink)
        except:
            print('이미지 없음')

        sites.append('마포장애인가족지원센터')
        regions.append(['서울시', '마포구'])
        categories.append(None)
        disabilityTypes.append(None)
        titles.append(title)
        dates.append(uploadDate)
        contents.append(content.text)
        #originalLinks.append(link)-
        contentLinks.append(linkText)
        images.append(imgs)

        driver.back()
        
        index += 1

saveCsv('mapo_family_support_center', sites, regions, categories, disabilityTypes, titles, dates, contents, contentLinks, images)