from crawl import Crawl

class SeoulEdu(Crawl):
    url = "https://www.sen.go.kr/user/bbs/BD_selectBbsList.do?q_rowPerPage=10&q_currPage=1&q_sortName=&q_sortOrder=&q_searchKeyTy2=1005&q_searchStartDt=&q_searchEndDt=&q_bbsSn=1100&q_bbsDocNo=&q_clsfNo=26&q_searchKeyTy=ttl___1002&q_searchVal=&"

seoulEdu = SeoulEdu('seoul_edu', SeoulEdu.url)
seoulEdu.startCrawl()