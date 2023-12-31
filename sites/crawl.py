# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import requests
import pandas as pd
import os


class Crawl:
    sites = []
    regions = []
    categories = []
    disabilityTypes = []
    titles = []
    dates = []
    contents = []
    originalLinks = []
    images = []

 
    def __init__(self, fileName, url, latestCrawlDate = '2023-06-01') -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--incognito")
        self.options.add_argument("--headless")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("enable-automation")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--dns-prefetch-disable")
        self.options.add_argument("--disable-gpu")

        self.latestCrawlDate = datetime.strptime(latestCrawlDate, '%Y-%m-%d')

        self.currentPage = 1
        self.fileName = fileName
        self.url = url

    def openBrowser(self):
        self.driver= webdriver.Chrome(options=self.options)
        self.driver.get(self.url)
        time.sleep(10)

    def makeCSVwithFormat(self):
        # Get data format
        try:
            self.df = pd.read_csv('result/format.csv')
        except Exception as e:
            print(e, ': Load format.csv') 

        # Make result csv file to apply column format
        # 참고 : lastCrawlDate를 지금 입력값으로 가져오는데 나중에 알아서 돌아가게 하려면 이부분의 코드 수정 필요할 듯
        # try:
        #     self.df.to_csv(f'result/crawl/{self.fileName}.csv', mode='w')
        # except Exception as e:
        #     print(e, f': Apply format to {self.fileName}.csv')

    def getContentsLengthPerPage(self):
        try:
            threads = self.getContentThreads()
        except Exception as e:
            print(e, ": 페이지 별 게시글 개수 가져오기 실패")
            return 10
        
        return len(threads)
    
    def getContentThreads(self, selector = "#container > section.cinner > div > div.bd-list > table > tbody > tr"):
        try:
            threads = self.driver.find_elements(By.CSS_SELECTOR, selector)
        except Exception as e:
            print(e, ": 게시글 목록에서 게시글 thread 가져오기 실패")

        return threads

    def getTotalContentsLength(self):
        try:
            contentsLengthPerPage = self.getContentsLengthPerPage()
            self.contentsLength = int(self.driver.find_element(By.CSS_SELECTOR, "#dataForm > div > div.bd-info > div.total > strong").text)
            self.pageLength = self.contentsLength // contentsLengthPerPage
            if self.contentsLength % contentsLengthPerPage:
                self.pageLength += 1

        except Exception as e:
            print(e, ": 전체 게시글 수 가져오기 실패")
            

    def isRemaiedPaegs(self):
        if self.currentPage <= self.pageLength:
            return True
        else:
            False

    def movetoNextPage(self):
        self.currentPage += 1
        nextPageUrl = f"https://www.sen.go.kr/user/bbs/BD_selectBbsList.do?q_rowPerPage=10&q_currPage={self.currentPage}&q_sortName=&q_sortOrder=&q_searchKeyTy2=1005&q_searchStartDt=&q_searchEndDt=&q_bbsSn=1100&q_bbsDocNo=&q_clsfNo=26&q_searchKeyTy=ttl___1002&q_searchVal=&"
        self.driver.get(nextPageUrl)
        # time.sleep(2)

    def moveToEachContent(self, url):
        self.driver.get(url)
        # time.sleep(0.5)

    def getSite(self):
        return "서울시교육청 특수교육과"

    def getContentLink(self, thread):
        href = thread.find_element(By.TAG_NAME, "a").get_attribute('href')
        return href

    def getOutsideDate(self, thread):
        date = thread.find_element(By.CLASS_NAME, "bbs_date").text
        date = datetime.strptime(date, '%Y-%m-%d')
        return date

    def makeContentLinkGroup(self) -> None:
        self.getTotalContentsLength()
        self.contentLinks = []

        while self.isRemaiedPaegs():
            try:
                threads = self.getContentThreads("#container > section.cinner > div > div.bd-list > table > tbody > tr")
            except Exception as e:
                print(e, ": 게시글 리스트 크롤링 실패")
                threads = []

            isContentLeftAfterLastCrawlDate = self.appendContentLinkOf(threads)
            if isContentLeftAfterLastCrawlDate:
                self.movetoNextPage()
            else:
                break

        return None
    
    def appendContentLinkOf(self, threads):
        for thread in threads:
            date = self.getOutsideDate(thread)
            if date <= self.latestCrawlDate:
                return False
            else:
                contentLink = self.getContentLink(thread)
                self.contentLinks.append(contentLink)
        return True

    def getRegion(self):
        return ["서울시"]

    def getCategory(self):
        return None

    def GetDisabilityType(self):
        return "전체"

    def getTitle(self):
        try:
            title = self.driver.find_element(By.CLASS_NAME, "vtitle").find_element(By.CLASS_NAME, "tit").text
        except Exception as e:
            print(e, ": title 크롤링 실패")
            title = ""

        return title
        
    def getInsideDate(self):
        try:
            date = self.driver.find_element(By.CLASS_NAME, "vinfo").find_elements(By.TAG_NAME, "li")[1].text.split("\n")[1]
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(e, "insideDate 크롤링 실패")
            date = self.latestCrawlDate

        return date

    def getContent(self):
        try:
            content = self.driver.find_element(By.CLASS_NAME, "bd-view__vcontent").find_element(By.CLASS_NAME, "txt").text
        except Exception as e:
            print(e, ": content 크롤링 실패")
            content = ""

        return content

    def getOriginalLink(self):
        pass

    def getImage(self):
        return []
    
    def makeCrawlingResultToDataframe(self):
        self.makeContentLinkGroup()

        for link in self.contentLinks:
            self.moveToEachContent(link)
            self.sites.append(self.getSite())
            self.regions.append(self.getRegion())
            self.categories.append(self.getCategory())
            self.disabilityTypes.append(self.GetDisabilityType())
            self.titles.append(self.getTitle())
            self.dates.append(self.getInsideDate())
            self.contents.append(self.getContent())
            # self.originalLinks.append(self.getOriginalLink())
            self.images.append(self.getImage())

        self.df['site'] = self.sites
        self.df['region'] = self.regions
        self.df['category'] = self.categories
        self.df['disability_type'] = self.disabilityTypes
        self.df['title'] = self.titles
        self.df['date'] = self.dates
        self.df['content'] = self.contents
        self.df['original_link'] = self.contentLinks
        self.df['content_link'] = self.contentLinks
        self.df['image'] = self.images

    def saveDataframeToCSV(self):
        try:
            self.df.to_csv(f'result/crawl/{self.fileName}.csv', mode='a', header=False)
        except Exception as e:
            print(e, ": Make crawling result csv file")

    def startCrawl(self):
        self.makeCSVwithFormat()
        self.openBrowser()
        self.makeCrawlingResultToDataframe()
        self.saveDataframeToCSV()