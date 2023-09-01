# -*- coding: utf-8 -*-

# 강북장애인종합복지관

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import date, timedelta, datetime
from save_csv import saveCsv
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
    dateTime = datetime.strptime(strDate, '%y-%m-%d')
    return datetime.date(dateTime)

options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options) 

#크롬 드라이버에 url 주소 넣고 실행
driver.get('http://www.gangbukrc.or.kr/menu/?menu_str=3010&list_count=&sca=%EB%AA%A8%EC%A7%91')

# 페이지가 완전히 로딩되도록 3초동안 기다림
time.sleep(3)

postList = driver.find_element(By.CLASS_NAME, 'gallery_list').find_elements(By.CLASS_NAME, 'thumb_one')[:18]

for post in postList:
    uploadDate = post.find_element(By.CLASS_NAME, 'g_day').text
    uploadDate = strToDate(uploadDate.split('\n')[0])

    if uploadDate > lastCrawlDate:
        link = post.find_element(By.TAG_NAME, 'a')
        title = post.find_element(By.CLASS_NAME, 'g_title').text
        linkText = link.get_attribute('href')

        link.click()
        time.sleep(2)
        
        content = driver.find_element(By.ID, 'bo_v_con').text
        
        imgs = []

        try:
            imgList = driver.find_element(By.CLASS_NAME, 'detail_data').find_elements(By.TAG_NAME, 'img')
            for idx, img in enumerate(imgList):
                imgLink = img.get_attribute('src')
                imgs.append(imgLink)
        except:
            print('이미지 없음')

        sites.append('강북장애인종합복지관')
        regions.append(['서울시', '강북구'])
        categories.append(None)
        disabilityTypes.append(None)
        titles.append(title)
        dates.append(uploadDate)
        contents.append(content)
        #originalLinks.append(link)-
        contentLinks.append(linkText)
        images.append(imgs)
        
        driver.back()

saveCsv('gangbuk_disabled_welfare_center', sites, regions, categories, disabilityTypes, titles, dates, contents, contentLinks, images)