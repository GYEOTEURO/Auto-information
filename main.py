# -*- coding: utf-8 -*-

import subprocess
import yaml
import os
from datetime import datetime
import pathlib

os.chdir(pathlib.Path(__file__).parent.absolute())

# Constants load
with open('constants.yaml', encoding='UTF-8') as f:
  constants = yaml.load(f, Loader=yaml.FullLoader)

def setWorkingDirectoryToFileDirectory():
  os.chdir(pathlib.Path(__file__).parent.absolute())

def updateLastCrawlDate():
  constants['crawl']['latest_date'] = datetime.now().strftime("%Y-%m-%d")
  with open('constants.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(constants, f, allow_unicode=True)

def runCrawling():
  crawlFiles = os.listdir("sites")
  crawlFiles = os.listdir("sites")
  crawlFiles = [file for file in crawlFiles if file.endswith('.py')]
  crawlFiles.remove('crawl.py')
  crawlFiles.remove('save_csv.py')
  crawlFiles.remove('__init__.py')
  print(crawlFiles)

  for crawlFile in crawlFiles:
    crawlFile = 'sites/' + crawlFile
    print("-------------------")
    print(crawlFile, "실행 시작")
    try:
      subprocess.run(["python3", crawlFile])
      print(crawlFile, "실행 완료")

    except Exception as e:
      print(e, crawlFile, "실행 실패")

def runSendingSummariesToDB():
  try:
    subprocess.run(["python3", 'sendToDB.py'])
    print("summaries DB 전송 완료")

  except Exception as e:
    print(e, ": summaries DB 전송 완료")

if __name__ == "__main__":
  print("====================================================")
  print(f"{constants['crawl']['latest_date']} 일자 main.py 실행")
  print("====================================================\n")
  setWorkingDirectoryToFileDirectory()
  runCrawling()
  runSendingSummariesToDB()
  updateLastCrawlDate()