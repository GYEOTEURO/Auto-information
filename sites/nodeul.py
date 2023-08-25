from crawl import Crawl
from selenium.webdriver.common.by import By
from selenium .webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

class Nodeul(Crawl):


    def __init__(self, url, latestCrawlDate='2023-01-01') -> None:
        super().__init__("nodeul", url, latestCrawlDate)

    def movetoNextPage(self) -> None:
        self.currentPage += 1
        nextPageUrl = f"http://ncil.or.kr/index.php?mid=events_news&page={self.currentPage}"
        self.driver.get(nextPageUrl)

    def getOutsideDate(self, thread) -> datetime:
        try:
            date = thread.find_element(By.CSS_SELECTOR, "div > div.info > span:nth-child(1) > b").text
            date = datetime.strptime(date, '%Y.%m.%d')
        except Exception as e:
            print(e, ": 리스트뷰에서 게시글 바깥의 날짜 가져오기 실패")
            date = datetime.now()
        return date

    def isRemaiedPaegs(self) -> bool:
        try:
            firstThreadOfPage = self.driver.find_elements(By.CSS_SELECTOR, "#bd_224_0 > div.bd_lst_wrp > ol > li")[0]
            dateOfFirstContent = self.getOutsideDate(firstThreadOfPage)
            if dateOfFirstContent > self.latestCrawlDate:
                return True
            
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
    
    def isSecretContent(self, thread):
        try:
            content = thread.find_element(By.CLASS_NAME, "cnt").text
            if content == "비밀글입니다.":
                return True
        
        except Exception as e:
            print(e, ": 해당 게시글이 비밀 글인지에 대한 판단 실패")
        
        return False
    
    def appendContentLinkOf(self, threads):
        for thread in threads:
            date = self.getOutsideDate(thread)
            if date <= self.latestCrawlDate:
                return False
            else:
                contentLink = self.getContentLink(thread)
                print(f"{date} : {contentLink}")

                if not self.isSecretContent(thread):
                    self.contentLinks.append(contentLink)
        return True

    def getSite(self):
        return "노들장애인자립센터"
        
    def getTitle(self):
        try:
            title = self.driver.find_element(By.CLASS_NAME, "np_18px").find_element(By.TAG_NAME, 'a').text
        except Exception as e:
            print(e, ": title 가져오기 실패")
            title = ''

        return title
    
    def getContent(self):
        content = ''
        try:
            content  = self.driver.find_element(By.TAG_NAME,"article").text

        except Exception as e:
            print(e, ": content 가져오기 실패")
            print('content:', content)
            content = ''

        content = self.removeEmailAddress(content)
        return content
    
    def removeEmailAddress(self, content):
        content = content.replace('nodl@hanmail.net', '노들장애인자립생활센터 이메일 주소')
        return content
        
    def getImage(self):
        images = []
        try:
            threadsOfImage = self.driver.find_element(By.TAG_NAME,"article").find_elements(By.TAG_NAME, 'img')
            for thread in threadsOfImage:
                imageLink = thread.get_attribute('src')
                images.append(imageLink)
        except Exception as e:
            print(e, ": image 가져오기 실패")
        
        return images
    
    def getInsideDate(self):
        try:
            date = self.driver.find_element(By.CLASS_NAME, "top_area ngeb").find_element(By.CLASS_NAME, "fr")
            print(date)
            date = date.find_element(By.TAG_NAME, 'span').text
            date = datetime.strptime(date, '%Y.%m.%d %H:%M')
        except Exception as e:
            print(e, ": 게시글 안의 날짜 가져오기 실패")
            date = datetime.now()
        return date
    
    def getRegion(self):
        return super().getRegion()
    
    def getDisabilityType(self):
        return "전체"


if __name__ == "__main__":
    nodeul = Nodeul("http://ncil.or.kr/events_news")
    nodeul.startCrawl()