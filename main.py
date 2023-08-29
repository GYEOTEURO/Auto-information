import subprocess
import yaml
import os
from datetime import datetime


# Constants load
with open('constants.yaml', encoding='UTF-8') as f:
    constants = yaml.load(f, Loader=yaml.FullLoader)

def updateLatestDate():
  constants['crawl']['latest_date'] = datetime.now().strftime("%Y-%m-%d")
  with open('constants.yaml', 'w') as f:
    yaml.dump(constants, f)

def runCrawling():
  crawlFiles = os.listdir("sites").remove('crawl.py')
  crawlFiles.remove('save_csv.py')
  print(crawlFiles)

  for crawlFile in crawlFiles:
    print("-------------------")
    print(crawlFile, "실행 시작")
    try:
      subprocess.run(["python", crawlFile])
      print(crawlFile, "실행 완료")

    except Exception as e:
      print(e, crawlFile, "실행 실패")
    
  updateLatestDate()

if __name__ == "__main__":
    runCrawling()