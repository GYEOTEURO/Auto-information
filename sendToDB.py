 # -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
from summarizer import Summarizer
import os


# Use the application default credentials
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 요약문 df 를 가지고 firestore DB로 보내는 함수
def sendToDB(df):
    pass

# 파일들 이름 가져오기
def getCrawledFileNames():
    return os.listdir("result/crawl")


# Summarize 인스턴스 생성
summarizer = Summarizer("chatGPT")

# 반복문으로 result/summary에 있는 csv 파일 하나씩 가져오면서 summarize 진행
    # summarize 진행 후 df 가져와서 DB로 보내기
files = getCrawledFileNames()
print(files)

for file in files[2:]:
    fileName = file[:-4]
    summarizer.setFileName(fileName)
    summarizer.loadDataframe()
    summarizer.summarizeContents()
    summarizer.saveDataframeToCSV()
    
    summarizer.df.drop(['Unnamed: 0'], axis = 1, inplace = True)
    summarizer.df = summarizer.df.astype({"category" : "str"})
    print("++++\n", summarizer.df.dtypes)

    for i in summarizer.df.index:
        data = summarizer.df.loc[i].to_dict()
        data['region'] = data['region'].split(',')
        print(data)

        # autoInformation(collection) - 카테고리명(doc) - posts(collection) - 개별 post(doc)
        doc_ref = db.collection('autoInformation').document(data['category']).collection('autoInformation_posts').document()

        # 유의미한 ID를 두지 않고 Cloud Firestore에서 자동으로 ID를 생성 : add() , document().set()
        doc_ref.set(data)