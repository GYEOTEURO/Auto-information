from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import re

global lastCrawlDate

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

            
now_date = datetime.datetime.now()
before_one_month = now_date + relativedelta(months=-1)


s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

url = "https://www.jgcrc.or.kr/notice"
driver.get(url)
# Find all the rows within the tbody element
rows = driver.find_elements(By.XPATH, '//tbody/tr')

# Get the current date
current_date = datetime.date.today()

# Collect the post links
post_links = []
for row in rows:
    try:
        # 포스트의 날짜 정보 추출
        date_string = row.find_element(By.CLASS_NAME, 'date').text
        post_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

        # 날짜 차이 계산 (오늘과 포스트 작성일과의 차이)
        date_diff = (current_date - post_date).days

        # 포스트가 30일 이내에 작성된 것인지 확인
        if date_diff <= 30:
        # TODO: if uploadDate > lastCrawlDate:
            # 30일 이내에 작성된 포스트의 경우 링크를 수집
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
            author_date = driver.find_element(By.CLASS_NAME, 'view_info').text
            date_pattern = r"\d{4}\.\d{2}\.\d{2}"  # YYYY.MM.DD format pattern
            author_date = re.search(date_pattern, author_date).group()
            # YYYY.MM.DD 형식의 날짜 문자열을 datetime 객체로 변환
            extracted_date_obj = datetime.strptime(author_date, '%Y.%m.%d')
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
            image_url = image_element.get_attribute('href')
        except Exception as e:
            print(e, "image 크롤링 실패")
            image_url = None


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