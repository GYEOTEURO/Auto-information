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
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from main import constants

# 마지막 크롤링 날짜
lastCrawlDate = constants['crawl']['latest_date']
lastCrawlDate = datetime.datetime.strptime(lastCrawlDate, '%Y-%m-%d')

fileName = 'together-seoul'
siteName = '서울시장애인복지관협회'
region = ['서울시']
category = None
disabilityType = '뇌병변'

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
options.add_argument("enable-automation")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options) 

url = "http://www.together-seoul.org/menu/?menu_str=0406"
driver.get(url)
# Find all the rows within the tbody element
rows = driver.find_elements(By.TAG_NAME, 'tr')


# Collect the post links
post_links = []
for row in rows:
    try:
        columns = row.find_elements(By.TAG_NAME, 'td')

        if len(columns) >= 5:
            date_string = columns[3].text
            post_date = datetime.datetime.strptime(date_string, '%y-%m-%d')

            if post_date > lastCrawlDate:
                link_element = columns[1].find_element(By.TAG_NAME, 'a')
                link = link_element.get_attribute('href')
                post_links.append(link)

    except Exception as e:
        print(f"Error processing date: {e}")

# Iterate over the post links and extract the data for the posts within the last month
for link in post_links:
    try:
        # Navigate to the link
        driver.get(link)

        # Extract the title, author, date, and content from the internal page
        try:
            title_element = driver.find_element(By.XPATH, "//dl[@class='top_title']/dd")
            title = title_element.text
        except Exception as e:
            print(e, ": title crawling failed")
            title = ""

        try:
            author_date_element = driver.find_elements(By.XPATH, "//dl[contains(dt/span, '작성자') or contains(dt/span, '등록일')]/dd")
            author = author_date_element[0].text
            date_string = author_date_element[1].text
            date_pattern = r"\d{2}-\d{2}-\d{2}"  # YY-MM-DD format pattern
            extracted_date = re.search(date_pattern, date_string).group()
            
            # YY-MM-DD 형식의 날짜 문자열을 datetime 객체로 변환
            extracted_date_obj = datetime.datetime.strptime(extracted_date, '%y-%m-%d')
        except Exception as e:
            print(e, "author or date crawling failed")
            author = ""
            extracted_date_obj = None

        try:
            content_element = driver.find_element(By.CLASS_NAME, 'detail_data')
            content = content_element.text
        except Exception as e:
            print(e, "content crawling failed")
            content = ""

        # Extract the image URL if it exists
        try:
            image_element = driver.find_element(By.XPATH, "//a[@class='view_image']")
            image_url = [image_element.get_attribute('href')]
        except Exception as e:
            print("image crawling failed")
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