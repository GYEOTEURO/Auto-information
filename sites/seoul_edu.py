from crawl import Crawl
from main import constants
from main import constants

# 마지막 크롤링 날짜
lastCrawlDate = constants['crawl']['latest_date']

class SeoulEdu(Crawl):
    def __init__(self, fileName, url, latestCrawlDate='2023-06-01') -> None:
        super().__init__(fileName, url, latestCrawlDate)
        
url = "https://www.sen.go.kr/user/bbs/BD_selectBbsList.do?q_rowPerPage=10&q_currPage=1&q_sortName=&q_sortOrder=&q_searchKeyTy2=1005&q_searchStartDt=&q_searchEndDt=&q_bbsSn=1100&q_bbsDocNo=&q_clsfNo=26&q_searchKeyTy=ttl___1002&q_searchVal=&"
seoulEdu = SeoulEdu('seoul_edu', url, lastCrawlDate)
seoulEdu.startCrawl()