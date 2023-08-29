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

            
now_date = datetime.datetime.now()
before_one_month = now_date + relativedelta(months=-1)

print(str(before_one_month))

s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

url = "http://www.together-seoul.org/menu/?menu_str=0406"
driver.get(url)
# Find all the rows within the tbody element
rows = driver.find_elements(By.TAG_NAME, 'tr')

# Get the current date
current_date = datetime.date.today()

# Collect the post links
post_links = []
for row in rows:
    try:
        columns = row.find_elements(By.TAG_NAME, 'td')

        if len(columns) >= 5:
            date_string = columns[3].text
            post_date = datetime.datetime.strptime(date_string, '%y-%m-%d').date()

            # Calculate date difference
            date_diff = (current_date - post_date).days

            if date_diff <= 30:
            # TODO: if uploadDate > lastCrawlDate:
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
            extracted_date_obj = datetime.strptime(extracted_date, '%y-%m-%d')
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
            image_url = image_element.get_attribute('href')
        except Exception as e:
            print(e, "image crawling failed")
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