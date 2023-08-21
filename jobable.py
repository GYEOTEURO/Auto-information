from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import re

fileName = 'jobable'
siteName = '서울특별시 장애인일자리 통합지원센터'
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

url = "https://jobable.seoul.go.kr/jobable/custmr_cntr/ntce/WwwNotice.do?method=selectWwwNoticeList&chUseZe=D"
driver.get(url)
# Find all the rows within the tbody element
rows = driver.find_elements(By.TAG_NAME, 'tr')

# Get the current date
current_date = datetime.date.today()

# Collect the post links
post_links = []
for row in rows:
    try:
        # JavaScript 함수 호출하여 링크 얻기
        link = driver.execute_script("return arguments[0].querySelector('a')?.getAttribute('href');", row)
        
        # 링크가 있는 경우에만 처리
        if link:
            # 숫자 추출
            numbers = re.findall(r'\d+', link)
            if numbers:
                bbscttSn = numbers[0]
                # 링크 생성
                post_link = f"https://jobable.seoul.go.kr/jobable/custmr_cntr/ntce/WwwNotice.do?method=getWwwNotice&chUseZe=D&noticeCmmnSeNo=1&bbscttSn={bbscttSn}&fileyn=N"
                post_links.append(post_link)
        
    except Exception as e:
        print(f"Error processing row: {e}")


# Iterate over the post links and extract the data for the posts within the last month
for link in post_links:
    try:
        driver.get(link)

        # 제목 추출
        try:
            title_element = driver.find_element(By.XPATH, "//th[@class='title']")
            title = title_element.text
        except Exception as e:
            print(e, ": title crawling failed")
            title = ""

        # 날짜 추출
        try:
            date_elements = driver.find_elements(By.XPATH, "//tr/th[text()='등록일']/following-sibling::td")
            date_str = date_elements[0].text
            date = datetime.datetime.strptime(date_str, '%d.%m.%y').strftime('%d-%m-%y')
        except Exception as e:
            print(e, ": date crawling failed")
            date = ""


        # 이미지 URL 추출
        try:
            # 이미지가 보일 때까지 대기
            img_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='content']/form/div/div[1]/table/tbody/tr[3]/td/p[3]/img"))
            )
            # 이미지 URL 추출
            image_url = img_element.get_attribute("src")  
        except Exception as e:
            print(e, ": image URL crawling failed")
            image_url = ""


        # 글 내용 추출
        try:
            content_element = driver.find_element(By.XPATH, "//td[@class='view']")
            content = content_element.text
        except Exception as e:
            print(e, ": content crawling failed")
            content = ""

        # Append the extracted data to lists
        sites.append(siteName)
        regions.append(region)
        categories.append(category)
        disabilityTypes.append(disabilityType)
        titles.append(title)
        dates.append(date)
        contents.append(content)
        images.append(image_url) 
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
