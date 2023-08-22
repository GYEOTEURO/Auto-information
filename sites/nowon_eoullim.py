from crawl import Crawl
from selenium.webdriver.common.by import By
import time


class NowonEoullim(Crawl):
    urlDict = {'free': '41', 'notice' : '51', 'eoullimNews': '55', 'houseNeWs': '56'}

    def __init__(self, url, latestCrawlDate='2023-01-01') -> None:
        super().__init__("nowon_eoullim", url, latestCrawlDate)


    def setAndMoveUrlByBoardOf(self, boardName="notice"):
        self.url = "http://www.nowonilc.or.kr/bbs/board.php?bo_table=" + self.urlDict[boardName]
        self.driver.get(self.url)
        time.sleep(5)

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
                print(f"{date} : {contentLink}")
                self.contentLinks.append(contentLink)
        return True
    
    def getOutsideDate(self, thread):
        return super().getOutsideDate(thread)

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
        return super().getRegion()
    
    def getCategory(self):
        return super().getCategory()
    
    def getContent(self):
        return super().getContent()
    
    def getContentLink(self, thread):
        return super().getContentLink(thread)
    
    def getImage(self):
        return super().getImage()
    
    def getInsideDate(self):
        return super().getInsideDate()
    
    def getOriginalLink(self):
        return super().getOriginalLink()
    
    def getTitle(self):
        pass
    
    
    def startCrawl(self):
        return super().startCrawl()
    

nowonNotices = NowonEoullim("http://www.nowonilc.or.kr")
print(nowonNotices.startCrawl())

