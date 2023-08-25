from crawl import Crawl
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import pandas as pd

class NowonEoullim(Crawl):
    urlDict = {'free': '41', 'notice' : '51', 'eoullimNews': '55', 'houseNeWs': '56'}

    def __init__(self, url, latestCrawlDate='2023-01-01') -> None:
        super().__init__("nowon_eoullim", url, latestCrawlDate)


    def setAndMoveUrlByBoardOf(self, boardName="notice"):
        self.url = "http://www.nowonilc.or.kr/bbs/board.php?bo_table=" + self.urlDict[boardName]
        self.driver.get(self.url)
        # time.sleep(5)

    def movetoNextPage(self):
        self.currentPage += 1
        nextPageUrl = f"http://www.nowonilc.or.kr/bbs/board.php?bo_table=51&page={self.currentPage}"
        self.driver.get(nextPageUrl)

    def makeContentLinkGroup(self) -> None:
        self.setAndMoveUrlByBoardOf("notice")

        self.getTotalContentsLength()
        self.contentLinks = []
        # 일단 공지사항만 했는데 나중에는 urlDict.keys()로 여러 게시판 콘텐츠 다 가져올 예정 (기사 가져온 게시판도 있어서 일단 공지사항만 함)

        while self.isRemaiedPaegs():
            try:
                threads = self.driver.find_elements(By.CSS_SELECTOR, "#fboardlist > div > table > tbody > tr")
            except Exception as e:
                print(e, ": 게시글 리스트 크롤링 실패")
                threads = []

            if self.currentPage == 1:
                try:
                    pinnedContentTreads = self.driver.find_elements(By.CLASS_NAME, "bo_notice")
                    self.appendPinnedContentLinkOf(threads)
                    threads = threads[len(pinnedContentTreads):]

                except Exception as e:
                    print(e, ": 첫 페이지 상단 고정된 공지 게시글들 가져오기 실패")
                    threads = threads[13:]

            isContentLeftAfterLastCrawlDate = self.appendNormalContentLinkOf(threads)
            if isContentLeftAfterLastCrawlDate:
                self.movetoNextPage()
            else:
                break

        return None
    
    def appendNormalContentLinkOf(self, threads):
        return super().appendContentLinkOf(threads)
    
    def appendPinnedContentLinkOf(self, threads):
        for thread in threads:
            date = self.getOutsideDate(thread)
            if date <= self.latestCrawlDate:
                return False
            else:
                contentLink = self.getContentLink(thread)
                self.contentLinks.append(contentLink)
        return True
    
    def getOutsideDate(self, thread):
        try:
            date = thread.find_element(By.CLASS_NAME, "td_date").text
            date = datetime.strptime(date, '%Y-%m-%d')
        except Exception as e:
            print(e, ": 바깥에 있는 게시글 날짜 가져오기 실패")
        
        return date

    def getContentsLengthPerPage(self):
        try:
            threads = self.driver.find_elements(By.CSS_SELECTOR, "#fboardlist > div > table > tbody > tr")
        except Exception as e:
            print(e)
            return 30
        return len(threads)

    def getTotalContentsLength(self):
        contentsLengthPerPage = self.getContentsLengthPerPage()
        try:
            threadOfContentsLength = self.driver.find_element(By.CSS_SELECTOR, "#bo_list_total")
            self.contentsLength = int(threadOfContentsLength.find_element(By.TAG_NAME, "span").text.split(' ')[-1][:-1])
            self.pageLength = self.contentsLength // contentsLengthPerPage
            if self.contentsLength % contentsLengthPerPage:
                self.pageLength += 1
        
        except Exception as e:
            print(e, ": 게시글 총 개수 가져오기 실패")
            self.pageLength = 12
            self.contentsLength = 350

    def getSite(self):
        return "노원장애인자립생활센터어울림"
    
    def getRegion(self):
        return ["서울시", "노원구"]
    
    def getCategory(self):
        return super().getCategory()
    
    def getContent(self):
        try:
            content = self.driver.find_element(By.ID, "bo_v_con").text
        except Exception as e:
            print(e, ": content 크롤링 실패")
            content = ""

        print(f"content : \n{content}")

        return content
    
    def getImage(self):
        images = []
        try:
            threadsOfImage = self.driver.find_element(By.ID, "bo_v_img").find_elements(By.TAG_NAME, 'img')
            print(threadsOfImage)
            for image in threadsOfImage:
                imgLink = image.get_attribute('src')
                images.append(imgLink)
        except Exception as e:
            print(e, ": 이미지 가져오기 실패 혹은 없음")

        return images
    
    def getInsideDate(self):
        try:
            date = self.driver.find_element(By.CSS_SELECTOR, "#bo_v_info > strong:nth-child(4)").text
            date = datetime.strptime(date, '%y-%m-%d %H:%M')

        except Exception as e:
            print(e, ": 게시글 내 날짜 가져오기 실패")
            date = datetime.now()

        return date
    
    def getTitle(self):
        try:
            title = self.driver.find_element(By.CSS_SELECTOR, "#bo_v_title").text

        except Exception as e:
            print(e, ": title 가져오기 실패")
            title = ""

        return title
    

nowonNotices = NowonEoullim("http://www.nowonilc.or.kr")
print(nowonNotices.startCrawl())
print("크롤링 완료")