# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import re
from main import constants

# 마지막 크롤링 날짜
lastCrawlDate = constants['crawl']['latest_date']
lastCrawlDate = datetime.datetime.strptime(lastCrawlDate, '%Y-%m-%d')

fileName = 'jgcrc'
siteName = '서울특별시중구장애인복지관'
region = ['서울시','중구']
category = None
disabilityType = '전체'

sites = []
regions = []
categories = []
disabilityTypes = []
titles = []
dates = []
contents = []
originalLinks = []
images = []


try:
    df = pd.read_csv('result/format.csv')
except Exception as e:
    print(e, ': Load format.csv') 

# Make result csv file to apply column format
try:
    df.to_csv(f'result/crawl/{fileName}.csv', mode='w')
except Exception as e:
    print(e, f': Apply format to {fileName}.csv')


options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options) 

url = "https://www.jgcrc.or.kr/notice"
driver.get(url)
# Find all the rows within the tbody element
rows = driver.find_elements(By.XPATH, '//tbody/tr')

# Collect the post links
post_links = []
for row in rows:
    try:
        # 포스트의 날짜 정보 추출
        date_string = row.find_element(By.CLASS_NAME, 'date').text
        post_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

        if post_date > lastCrawlDate:
            link_element = row.find_element(By.TAG_NAME, 'a')
            link = link_element.get_attribute('href')
            post_links.append(link)

    except Exception as e:
        print(f"날짜 처리 중 오류 발생: {e}")

# Iterate over the post links and extract the data for the posts within the last month
for link in post_links:
    try:
        # Navigate to the link
        driver.get(link)

        # Extract the content and other optional elements from the internal page
        try:
            title = driver.find_element(By.CLASS_NAME, 'title_view').text
        except Exception as e:
            print(e, ": title 크롤링 실패")
            title = ""
        try:
            author_date_element = driver.find_element(By.CLASS_NAME, 'view_info').text
            date_pattern = r"\d{4}\.\d{2}\.\d{2}"  # YYYY.MM.DD format pattern
            extracted_date = re.search(date_pattern, author_date_element).group()
            extracted_date_obj = datetime.datetime.strptime(extracted_date, '%Y.%m.%d')
        except Exception as e:
            print(e, "authorDate 크롤링 실패")
            extracted_date_obj = None

        
        try:
            content = driver.find_element(By.CLASS_NAME, 'view_detail').text
        except Exception as e:
            print(e, "content 크롤링 실패")
            content = ""

        # Extract the image URL if it exists
        try:
            image_element = driver.find_element(By.CLASS_NAME, 'view_image')
            image_url = [image_element.get_attribute('href')]
        except Exception as e:
            print("image 크롤링 실패")
            image_url = []


        sites.append(siteName)
        regions.append(region)
        categories.append(category)
        disabilityTypes.append(disabilityType)
        titles.append(title)
        dates.append(extracted_date_obj)
        contents.append(content)
        images.append(image_url)


    except Exception as e:
        print(f"링크 처리 중 오류 발생: {e}")

    # Wait for a moment before processing the next link
    time.sleep(1)

df['site'] = sites
df['region'] = regions
df['category'] = categories
df['disability_type'] = disabilityTypes
df['title'] = titles
df['date'] = dates
df['content'] = contents
df['original_link'] = post_links
df['content_link'] = post_links
df['image'] = images

try:
    df.to_csv(f'result/crawl/{fileName}.csv', mode='a', header=False)
except Exception as e:
    print(e, ": Make crawling result csv file")