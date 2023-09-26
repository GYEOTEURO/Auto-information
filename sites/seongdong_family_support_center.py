# 성동장애인가족지원센터

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
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

driver = webdriver.Chrome(options=options)

targetPages = ['http://m.seongdongdfsc.or.kr/bbs/board2', 'http://m.seongdongdfsc.or.kr/bbs/board3'] 

for page in targetPages:
    driver.get(page)
    time.sleep(2)

    i = 0
    while(i<15):
        post = driver.find_element(By.ID, 'list_board').find_elements(By.CLASS_NAME, 'clr')[i]
        uploadDate = post.find_element(By.CLASS_NAME, 'col_date').text
        uploadDate = strToDate(uploadDate)

        if uploadDate > lastCrawlDate:
            link = post.find_element(By.TAG_NAME, 'a')
            title = link.text
            linkText = link.get_attribute('href')

            if ('모집' in title) or ('홍보' in title) or ('안내' in title):
                link.click()
                time.sleep(2)
            else:
                i = i+1
                continue
            
            postBody = driver.find_element(By.ID, 'conbody')
            content = postBody.text
            
            imgs = []

            try:
                imgList = postBody.find_elements(By.TAG_NAME, 'img')
                for img in imgList:
                    imgLink = img.get_attribute('src')
                    imgs.append(imgLink)
            except:
                print('이미지 없음')

            sites.append('성동장애인가족지원센터')
            regions.append(['서울시', '성동구'])
            categories.append(None)
            disabilityTypes.append(None)
            titles.append(title)
            dates.append(uploadDate)
            contents.append(content)
            contentLinks.append(linkText)
            images.append(imgs)
            
            driver.back()
            i = i+1
            time.sleep(2)
        else:
            break

saveCsv('seongdong_family_support_center', sites, regions, categories, disabilityTypes, titles, dates, contents, contentLinks, images)