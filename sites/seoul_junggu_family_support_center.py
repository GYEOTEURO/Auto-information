# 서울중구장애인가족지원센터

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

driver.get('https://jgdfsc.modoo.at/?link=7ajqm71h')
time.sleep(2)

i = 0
while(i<8):
    post = driver.find_element(By.ID, 'innerWrap').find_element(By.TAG_NAME, 'table').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')[i]
    uploadDate = post.find_element(By.CLASS_NAME, 'date').text
    uploadDate = strToDate(uploadDate.replace('.', '-'))
    
    if uploadDate > lastCrawlDate:
        link = post.find_element(By.TAG_NAME, 'a')
        title = link.text

        link.click()
        time.sleep(2)
        linkText = driver.current_url

        postBody = driver.find_element(By.CLASS_NAME, 'inner').find_element(By.CLASS_NAME, 'txt')
        content = postBody.text
        imgs = []

        try:
            imgList = postBody.find_elements(By.TAG_NAME, 'img')
            for img in imgList:
                imgLink = img.get_attribute('src')
                imgs.append(imgLink)
        except:
            print('이미지 없음')

        sites.append('서울중구장애인가족지원센터')
        regions.append(['서울시', '중구'])
        categories.append(None)
        disabilityTypes.append(None)
        titles.append(title)
        dates.append(uploadDate)
        contents.append(content)
        contentLinks.append(linkText)
        images.append(imgs)
        
        driver.back()
        i = i+1
        time.sleep(1)
    else:
        break

saveCsv('seoul_junggu_family_support_center', sites, regions, categories, disabilityTypes, titles, dates, contents, contentLinks, images)