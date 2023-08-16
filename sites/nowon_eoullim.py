from crawl import Crawl

class NowonEoullim(Crawl):
    urlDict = {'free': 41, 'notice' : 51, 'eoullimNews':55, 'houseNeWs':56}

    def __init__(self, url, latestCrawlDate='2023-06-01') -> None:
        super().__init__("nowon_center", url, latestCrawlDate)


    def setUrlByBoard(self, boardName):
        self.url = "http://www.nowonilc.or.kr/bbs/board.php?bo_table=" + self.urlDict[boardName]

    def makeContentLinkGroup(self) -> None:
        return super().makeContentLinkGroup()

    def getContentsLengthPerPage(self):
        return 5
    

nowonNotices = NowonEoullim("http://www.nowonilc.or.kr")
print(nowonNotices.makeCSVwithFormat())

