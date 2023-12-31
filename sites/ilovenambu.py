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

fileName = 'ilovenambu'
siteName = '서울특별시립 남부장애인종합복지관'
region = ['서울시', '남부']
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
options.add_argument("enable-automation")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options) 

url = "https://ilovenambu.or.kr/bbs/board.php?bo_table=0102"
driver.get(url)
# Find all the rows within the tbody element
rows = driver.find_elements(By.TAG_NAME, 'tr')

# Collect the post links
post_links = []
for row in rows:
    try:
        columns = row.find_elements(By.TAG_NAME, 'td')

        if len(columns) >= 5:
            date_string = columns[3].text.strip()  # Remove whitespace
            post_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')  # Fixed date format

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
            title_element = driver.find_element(By.XPATH, "//h2[@id='bo_v_title']")
            title = title_element.text
        except Exception as e:
            print(e, ": title crawling failed")
            title = ""

        try:
            date_element = driver.find_element(By.XPATH, "//section[@id='bo_v_info']//span[contains(@class, 'sound_only') and contains(text(), '작성일')]")
            date_string = date_element.find_element(By.XPATH, "./following-sibling::strong").text.split()[0]
            
            # 정규표현식을 사용하여 날짜 문자열에서 숫자 부분 추출
            date_numbers = re.findall(r'\d+', date_string)

            # 추출한 숫자를 이용하여 datetime 객체 생성
            year = int(date_numbers[0])
            month = int(date_numbers[1])
            day = int(date_numbers[2])

            crawled_date_obj = datetime.datetime(year, month, day)

        except Exception as e:
            print(e, "date crawling failed")
            crawled_date_obj = None


        try:
            content_element = driver.find_element(By.XPATH, "//div[@id='bo_v_con']")
            content = content_element.text
        except Exception as e:
            print(e, "content crawling failed")
            content = ""
            
        try:
            image_urls = []
            
            # If multiple images are inside <div id="bo_v_con">
            img_elements = driver.find_elements(By.CSS_SELECTOR, "#bo_v_con img")
            image_urls.extend([img.get_attribute("src") for img in img_elements if "newsletter" in img.get_attribute("src")])

            # Try to find images inside <div id="bo_v_con">
            img_elements = driver.find_elements(By.CSS_SELECTOR, "#bo_v_con img")
            image_urls.extend([img.get_attribute("src") for img in img_elements if "data/editor" in img.get_attribute("src")])

            # Try to find an image inside <div id="bo_v_img">
            try:
                image_element = driver.find_element(By.XPATH, "//div[@id='bo_v_img']//a[@class='view_image']")
                image_url = image_element.find_element(By.TAG_NAME, "img").get_attribute('src')
                image_urls.append(image_url)
            except:
                pass

        except Exception as e:
            print("Image crawling failed")
        

        # Append the extracted data to lists
        sites.append(siteName)
        regions.append(region)
        categories.append(category)
        disabilityTypes.append(disabilityType)
        titles.append(title)
        dates.append(crawled_date_obj)
        contents.append(content)
        images.append(image_urls)
        originalLinks.append(link)

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
