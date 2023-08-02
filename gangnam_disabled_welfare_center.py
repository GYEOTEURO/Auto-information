# 강남장애인복지관

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import date, timedelta, datetime
import os
from urllib.request import urlretrieve
import csv

#path_folder = '/home/shinmg/2022barrier-free/image/'


today = date.today()
one_week = timedelta(weeks=1)
last_week = today - one_week*20

def strToDate(strDate):
    dateTime = datetime.strptime(uploadDate, '%Y-%m-%d')
    return datetime.date(dateTime)


# 크롬드라이버 실행
driver = webdriver.Chrome() 

#크롬 드라이버에 url 주소 넣고 실행
driver.get('https://www.gangnam.go.kr/office/activeart/board/activeart3/list.do?mid=activeart_data03&pgno=2&keyfield=BDM_MAIN_TITLE&keyword=')

# 페이지가 완전히 로딩되도록 3초동안 기다림
time.sleep(3)

table = driver.find_element(By.TAG_NAME, 'table')
postList = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')[:18]

for post in postList:
    uploadDate = post.find_elements(By.TAG_NAME, 'td')[-1].text

    if strToDate(uploadDate) > last_week:
        link = post.find_element(By.TAG_NAME, 'a')
        title = link.text

        if '[모집]' in title or '[참여]' in title:
            link.click()
            time.sleep(2)
        else:
            continue
        
        content = driver.find_element(By.CLASS_NAME, 'post-content')
        
        images = []

        try:
            imgList = content.find_elements(By.TAG_NAME, 'img')
            for idx, img in enumerate(imgList):
                imgLink = img.get_attribute('src')
                extensionType = imgLink.split('.')[-1]
                #urlretrieve(imgLink, f'{path_folder}{title}_{idx}.{extensionType}')
                images.append(imgLink)
        except:
            print('이미지 없음')
        
        data = [
            {'title':title},
            {'content':content},
            {'content_link':link.get_attribute('href')},
            {'image':images},
            {'region':'서울시 강남구'},
            {'date':uploadDate},
            {'site':'강남장애인복지관'},
        ]

        f = open("gangnam_disabled_welfare_center.csv", "w")
        writer = csv.writer(f)
        writer.writerows(data)
        f.close()
        
        driver.back()


