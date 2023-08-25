from crawl import Crawl
from selenium.webdriver.common.by import By
from selenium .webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

class Nodeul(Crawl):


    def __init__(self, url, latestCrawlDate='2023-06-01') -> None:
        super().__init__("nodeul", url, latestCrawlDate)

    def movetoNextPage(self) -> None:
        self.currentPage += 1
        nextPageUrl = f"http://ncil.or.kr/index.php?mid=events_news&page={self.currentPage}"
        self.driver.get(nextPageUrl)

    def getOutsideDate(self, thread) -> datetime:
        date = thread.find_element(By.CLASS_NAME, "div > div.info > span:nth-child(1) > b").text
        date = datetime.strptime(date, '%Y.%m.%d')
        return date
    

    def isRemaiedPaegs(self) -> bool:
        try:
            firstThreadOfPage = self.driver.find_elements(By.CSS_SELECTOR, "#bd_224_0 > div.bd_lst_wrp > ol > li")[0]
            dateOfFirstContent = self.getOutsideDate(firstThreadOfPage)
            if dateOfFirstContent <= self.latestCrawlDate:
                return True
            else:
                return False
            
        except Exception as e:
            print(e, ": 크롤링할 페이지가 남았는 지 확인하는 코드 실행 실패")
        
        return False

    
    def makeContentLinkGroup(self) -> None:
        self.contentLinks = []

        while self.isRemaiedPaegs():
            try:
                threads = self.driver.find_elements(By.CSS_SELECTOR, "#bd_224_0 > div.bd_lst_wrp > ol > li")
            except Exception as e:
                print(e, ": 게시글 리스트 크롤링 실패")
                threads = []

            isContentLeftAfterLastCrawlDate = self.appendContentLinkOf(threads)
            if isContentLeftAfterLastCrawlDate:
                self.movetoNextPage()
            else:
                break

        return None



if __name__ == "__main__":
    nodeul = Nodeul("http://ncil.or.kr/events_news")