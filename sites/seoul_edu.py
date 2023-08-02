from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import requests

# Get Latest realse version
realse = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"

# Get version name
version = requests.get(realse).text

driver= webdriver.Chrome(service=Service(ChromeDriverManager(version=version).install()))

page = 1
url = f"https://www.sen.go.kr/user/bbs/BD_selectBbsList.do?q_rowPerPage=10&q_currPage={page}&q_sortName=&q_sortOrder=&q_searchKeyTy2=1005&q_searchStartDt=&q_searchEndDt=&q_bbsSn=1100&q_bbsDocNo=&q_clsfNo=26&q_searchKeyTy=ttl___1002&q_searchVal=&"

driver.get(url)

start = time.time()

threadsLength = driver.find_element(By.CSS_SELECTOR, "#dataForm > div > div.bd-info > div.total > strong").text
print(threadsLength)

for p in range(1, int(threadsLength)//10 + 1 + 1):
    # url에 page 부분이 p로만 바뀐 상태로 이동
    pass


threads = driver.find_elements(By.CSS_SELECTOR, "#container > section.cinner > div > div.bd-list > table > tbody > tr")
print(len(threads))

print("=======Start Crawling======")
contentLinks = []
dates = []
for thread in threads:
    date = thread.find_element(By.CLASS_NAME, "bbs_date").text
    date = datetime.strptime(date, '%Y-%m-%d')
    dates.append(date)
    if date <= datetime.strptime('2023-01-01', '%Y-%m-%d'):
        break
    else:
        href = thread.find_element(By.TAG_NAME, "a").get_attribute('href')
        contentLinks.append(href)
    
print(contentLinks)
print(dates)

# 게시글 하나씩 돌면서 크롤링 진행
for link in contentLinks:
    driver.get(link)
    time.sleep(2)

print("=======End Crawling======")

end = time.time()

print("총 걸린 시간 : %.5f" %(end-start))
