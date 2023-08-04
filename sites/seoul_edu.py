from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import requests
import pandas as pd
import os

latestCrawlDate = datetime.strptime('2023-06-01', '%Y-%m-%d')

# Get Latest realse version
realse = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
version = requests.get(realse).text

# Get data format
try:
    df = pd.read_csv('format.csv')
except Exception as e:
    print(e, ': Load format.csv') 

# Make result csv file to apply column format
try:
    df.to_csv('/result/seoul_edu.csv', mode='w')
except Exception as e:
    print(e, ': Apply format to seoul_edu.csv') 

# Open browser
driver= webdriver.Chrome(service=Service(ChromeDriverManager(version=version).install()))
currentPage = 1
url = f"https://www.sen.go.kr/user/bbs/BD_selectBbsList.do?q_rowPerPage=10&q_currPage={currentPage}&q_sortName=&q_sortOrder=&q_searchKeyTy2=1005&q_searchStartDt=&q_searchEndDt=&q_bbsSn=1100&q_bbsDocNo=&q_clsfNo=26&q_searchKeyTy=ttl___1002&q_searchVal=&"
driver.get(url)

start = time.time()

# 필요한 함수들 정의
def isRemaiedPaegs():
    if currentPage <= pageLength:
        return True
    else:
        False

def movetoNextPage():
    currentPage += 1
    driver.get(url)
    # time.sleep(2)

def moveToEachContent(url):
    driver.get(url)
    # time.sleep(0.5)

def getContentLink(thread):
    href = thread.find_element(By.TAG_NAME, "a").get_attribute('href')
    return href

def getOutsideDate(thread):
    date = thread.find_element(By.CLASS_NAME, "bbs_date").text
    date = datetime.strptime(date, '%Y-%m-%d')
    return date

def makeContentLinkGroup():
    while isRemaiedPaegs():
        threads = driver.find_elements(By.CSS_SELECTOR, "#container > section.cinner > div > div.bd-list > table > tbody > tr")

        contentLinks = []
        for thread in threads:
            date = getOutsideDate(thread)
            if date <= latestCrawlDate:
                return contentLinks
            else:
                contentLink = getContentLink(thread)
                print(f"{date} : {contentLink}")
                contentLinks.append(contentLink)
        movetoNextPage()
        return contentLinks

def getRegion():
    pass

def getCategory():
    pass

def GetDisabilityType():
    pass

def getTitle():
    pass

def getInsideDate():
    pass

def getContent():
    pass

def getOriginalLink():
    pass

def getImage():
    pass

# Get total contents length
contentsLength = int(driver.find_element(By.CSS_SELECTOR, "#dataForm > div > div.bd-info > div.total > strong").text)
print(contentsLength)
pageLength = contentsLength//10 + 1


print("=======Start Crawling======")
contentLinks = makeContentLinkGroup()
    
print(contentLinks)

# 게시글 하나씩 돌면서 크롤링 진행
regions = []
categories = []
disability_types = []
titles = []
dates = []
contents = []
original_links = []
images = []

for link in contentLinks:
    moveToEachContent(link)
    regions.append(getRegion())
    categories.append(getCategory())
    disability_types.append(GetDisabilityType())
    titles.append(getTitle())
    dates.append(getInsideDate())
    contents.append(getContent())
    original_links.append(getOriginalLink())
    images.append(getImage())

df['site'] = '서울시교육청 특수교육과'
df['region'] = regions
df['category'] = categories
df['disability_type'] = disability_types
df['title'] = titles
df['date'] = dates
df['content'] = contents
df['original_link'] = original_links
df['conten_links'] = contentLinks
df['image'] = images


# Save dataframe to csv file
try:
    df.to_csv('/result/seoul_edu.csv', mode='a', header=False)
except Exception as e:
    print(e, ": Make crawling result csv file")

print("=======End Crawling======")

end = time.time()

print("총 걸린 시간 : %.5f" %(end-start))
