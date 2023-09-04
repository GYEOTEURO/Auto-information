# -*- coding: utf-8 -*-

from crawl import Crawl
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from main import constants

# 마지막 크롤링 날짜
lastCrawlDate = constants['crawl']['latest_date']

class Hasang(Crawl):
    def __init__(self, url, latestCrawlDate='2023-06-01') -> None:
        super().__init__("hasang", url, latestCrawlDate)

    def getContentsLengthPerPage(self):
        try:
            threads = self.getContentThreads("#fboardlist > div > table > tbody > tr")
        except Exception as e:
            print(e)
            return 15
        
        return len(threads)

    def getTotalContentsLength(self):
        try:
            contentsLengthPerPage = self.getContentsLengthPerPage()
            self.contentsLength = int(self.driver.find_element(By.CSS_SELECTOR, "#subContent > div.contents > div.board_top > div.total > strong").text)
            self.pageLength = self.contentsLength // contentsLengthPerPage
            if self.contentsLength % contentsLengthPerPage:
                self.pageLength += 1

        except Exception as e:
            print(e, ": 전체 게시글 수 가져오기 실패")
    
    def movetoNextPage(self):
        self.currentPage += 1
        nextPageUrl = f"http://www.hasang.org/recruitment_act?page={self.currentPage}"
        self.driver.get(nextPageUrl)

    def getOutsideDate(self, thread):
        date = thread.find_element(By.CSS_SELECTOR, "#fboardlist > div > table > tbody > tr> td:nth-child(4)").text
        date = datetime.strptime(date, '%Y-%m-%d')
        return date

    def makeContentLinkGroup(self) -> None:
        self.getTotalContentsLength()
        self.contentLinks = []

        while self.isRemaiedPaegs():
            try:
                threads = self.getContentThreads("#fboardlist > div > table > tbody > tr")
            except Exception as e:
                print(e, ": 게시글 리스트 크롤링 실패")
                threads = []


            if self.currentPage == 1:
                try:
                    pinnedContentTreads = self.driver.find_elements(By.CLASS_NAME, "bo_notice")
                    self.appendContentLinkOf(pinnedContentTreads)
                    threads = threads[len(pinnedContentTreads):]

                except Exception as e:
                    print(e, ": 첫 페이지 상단 고정된 공지 게시글들 가져오기 실패")
                    threads = threads[4:]

            isContentLeftAfterLastCrawlDate = self.appendContentLinkOf(threads)
            if isContentLeftAfterLastCrawlDate:
                self.movetoNextPage()
            else:
                break

        return None
    
    def getSite(self):
        return "하상장애인복지관"
        
    def getTitle(self):
        try:
            title = self.driver.find_element(By.CLASS_NAME, "bo_v_tit").text
        except Exception as e:
            print(e, ": title 가져오기 실패")
            title = ''

        return title
    
    def removeEmailAddress(self, content):
        emailPattern = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
        content = re.sub(pattern=emailPattern, repl='복지관 이메일 주소', string=content)
        return content
    
    def getContent(self):
        content = ''
        try:
            content  = self.driver.find_element(By.ID, "bo_v_con").text

        except Exception as e:
            print(e, ": content 가져오기 실패")
            print('content:', content)
            content = ''

        content = self.removeEmailAddress(content)
        return content
    
    def getImage(self):
        images = []
        try:
            threadsOfImage = self.driver.find_element(By.ID,"bo_v_atc").find_elements(By.TAG_NAME, 'img')
            for thread in threadsOfImage:
                imageLink = thread.get_attribute('src')
                images.append(imageLink)
        except Exception as e:
            print(e, ": image 가져오기 실패")
        
        return images
    
    def getInsideDate(self):
        try:
            date = self.driver.find_element(By.CLASS_NAME, "if_date").text
            date = datetime.strptime(date, '%y-%m-%d %H:%M')
        except Exception as e:
            print(e, ": 게시글 안의 날짜 가져오기 실패")
            date = datetime.now()
        return date
    
    def getDisabilityType(self):
        return "전체"


if __name__ == "__main__":
    hasang = Hasang("http://www.hasang.org/recruitment_act", lastCrawlDate)
    hasang.startCrawl()