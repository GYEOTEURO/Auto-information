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
    df.to_csv('result/seoul_edu.csv', mode='w')
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
        try:
            threads = driver.find_elements(By.CSS_SELECTOR, "#container > section.cinner > div > div.bd-list > table > tbody > tr")
        except Exception as e:
            print(e, ": 게시글 리스트 크롤링 실패")
            threads = []

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
    return "서울시"

def getCategory():
    return None

def GetDisabilityType():
    return "전체"

def getTitle():
    try:
        title = driver.find_element(By.CLASS_NAME, "vtitle").find_element(By.CLASS_NAME, "tit").text
    except Exception as e:
        print(e, ": title 크롤링 실패")
        title = ""

    return title
    
def getInsideDate():
    try:
        date = driver.find_element(By.CLASS_NAME, "vinfo").find_elements(By.TAG_NAME, "li")[1].text.split("\n")[1]
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(e, "insideDate 크롤링 실패")
        date = latestCrawlDate

    return date

def getContent():
    try:
        content = driver.find_element(By.CLASS_NAME, "bd-view__vcontent").find_element(By.CLASS_NAME, "txt").text
    except Exception as e:
        print(e, ": content 크롤링 실패")
        content = ""

    return content


def getOriginalLink():
    pass

def getImage():
    return None

# Get total contents length
contentsLength = int(driver.find_element(By.CSS_SELECTOR, "#dataForm > div > div.bd-info > div.total > strong").text)
print(contentsLength)
pageLength = contentsLength//10 + 1


print("=======Start Crawling======")
contentLinks = makeContentLinkGroup()
    
print(contentLinks)

# 게시글 하나씩 돌면서 크롤링 진행
sites = []
regions = []
categories = []
disabilityTypes = []
titles = []
dates = []
contents = []
originalLinks = []
images = []

for link in contentLinks:
    moveToEachContent(link)
    sites.append('서울시교육청 특수교육과')
    regions.append(getRegion())
    categories.append(getCategory())
    disabilityTypes.append(GetDisabilityType())
    titles.append(getTitle())
    dates.append(getInsideDate())
    contents.append(getContent())
    # originalLinks.append(getOriginalLink())
    images.append(getImage())

df['site'] = sites
df['region'] = regions
df['category'] = categories
df['disability_type'] = disabilityTypes
df['title'] = titles
df['date'] = dates
df['content'] = contents
df['original_link'] = contentLinks # 따로 외부 링크 없기에 본문 링크 동일
df['content_link'] = contentLinks
df['image'] = images # 따로 이미지가 안올라옴


# Save dataframe to csv file
try:
    df.to_csv('result/seoul_edu.csv', mode='a', header=False)
except Exception as e:
    print(e, ": Make crawling result csv file")

print("=======End Crawling======")

end = time.time()

print("총 걸린 시간 : %.5f" %(end-start))
