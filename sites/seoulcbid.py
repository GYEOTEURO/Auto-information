# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import datetime
import re
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from main import constants
from save_csv import saveCsv

# 마지막 크롤링 날짜
lastCrawlDate = constants['crawl']['latest_date']
lastCrawlDate = datetime.datetime.strptime(lastCrawlDate, '%Y-%m-%d')

fileName = 'seoulcbid'
siteName = '서울장애인종합복지관'
region = ['서울시']
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

options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options)

def removeEmailAddress(content):
    emailPattern = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
    content = re.sub(pattern=emailPattern, repl='노들장애인자립생활센터 이메일 주소', string=content)
    return content
    

def find_post_links():

    url = "https://seoulcbid.or.kr/bbs/board.php?bo_table=0702"
    driver.get(url)

    # Find all the rows within the tbody element
    rows = driver.find_elements(By.XPATH, '//tbody/tr')

    # Collect the post links with dates
    post_links = []

    # Collect the post data
    for row in rows:
        try:
            # Find the span element containing the date
            date_element = row.find_element(By.XPATH, './/td[@class="td_date hidden-xs text-left"]')
            date_string = date_element.text

            # Extract the date from the string
            post_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')

            # Check if the post is within the last month
            if post_date > lastCrawlDate:
                # Find the link to the post within the row
                link_element = row.find_element(By.XPATH, './/a[contains(@href, "wr_id=")]')
                link = link_element.get_attribute('href')

                # Extract the wr_id from the link using regular expressions
                wr_id_match = re.search(r'wr_id=(\d+)', link)
                if wr_id_match:
                    wr_id = wr_id_match.group(1)
                    post_links.append((wr_id, link, post_date))

        except Exception as e:
            print(f"날짜 처리 중 오류 발생: {e}")

    driver.quit()

    return post_links

# Example usage
post_links = find_post_links() 

# Iterate over the post links and extract the data for the posts within the last month
for wr_id, link, post_date in post_links:
    try:
        # Navigate to the link
        driver.get(link)
        # Wait for the page to load
        time.sleep(3)

        # Extract the HTML content of the post
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract the title (Fix this part if title extraction is not working as expected)

        try:
            title_element = soup.select_one('div.panel-heading h6')
            title_text = title_element.text.strip() if title_element else None
            # Splitting title_text to get the actual title
            title = title_text[3:]
        except Exception as e:
            print(e, ": Title extraction failed")
            title = None

        # Extract the content
        content_element = soup.select_one('#bo_v_con')
        content = content_element.text.strip() if content_element else None
        content = removeEmailAddress(content)

        # Extract the images
        image_elements = soup.select('#bo_v_con img')
        image_urls = [img['src'] for img in image_elements]



        # Append data to lists
        sites.append(siteName)
        regions.append(region)
        categories.append(category)
        disabilityTypes.append(disabilityType)
        titles.append(title)
        dates.append(post_date)
        contents.append(content)
        originalLinks.append(link)
        images.append(image_urls)

    except Exception as e:
        print(f"Error in post with wr_id {wr_id}: {e}")

# Quit the driver after processing all post links
driver.quit()


saveCsv(fileName, sites, regions, categories, disabilityTypes, titles, dates, contents, originalLinks, images)
