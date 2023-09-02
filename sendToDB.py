# -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials, storage, firestore
import pandas as pd
from summarizer import Summarizer
from dotenv import load_dotenv
import os
import asyncio
import requests
from datetime import datetime

load_dotenv()

# Use the application default credentials
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"storageBucket": os.getenv("FIRSTORE_PROJECT_ID") + ".appspot.com"})
db = firestore.client()

# Storage에 이미지 업로드할 버킷 생성
bucket = storage.bucket()

def sendDataToDB(data) -> None:
    try:
        # autoInformation(collection) - 카테고리명(doc) - posts(collection) - 개별 post(doc)
        doc_ref = db.collection('autoInformation').document(data['category']).collection('autoInformation_posts').document()

        # 유의미한 ID를 두지 않고 Cloud Firestore에서 자동으로 ID를 생성 : add() , document().set()
        doc_ref.set(data)

    except Exception as e:
        print(e, ": data Firestore 전송 실패")

def sendImagesToStorage(fileName, imageUrlsGroup):
    storageUrlsGroup = []
    for index, imageUrls in enumerate(imageUrlsGroup):
        storageUrls = []

        if imageUrls == [""]:
            storageUrlsGroup.append(storageUrls)
            continue

        for imageUrl in imageUrls:
            try:
                response = requests.get(imageUrl)
                imageData = response.content
                url = f"autoInformation_images/{fileName}_{index}" + datetime.now().strftime("_%Y-%m-%d_%H-%M") + ".jpg"
                blob = bucket.blob(url)  # 업로드할 경로 및 파일명 지정
                blob.upload_from_string(imageData, content_type="image/jpeg")  # 이미지 데이터 및 MIME 타입 지정
                storageUrls.append('https://storage.googleapis.com/'+os.getenv("FIRSTORE_PROJECT_ID")+'.appspot.com/'+url)
            except Exception as e:
                print(e, ": 이미지 storage 저장 실패")
                storageUrls.append(None)

            
        storageUrlsGroup.append(storageUrls)

    return storageUrlsGroup

# 파일들 이름 가져오기
def getCrawledFileNames():
    return os.listdir("result/crawl")


async def main():
    # Summarize 인스턴스 생성
    summarizer = Summarizer("chatGPT")

    # 반복문으로 result/summary에 있는 csv 파일 하나씩 가져오면서 summarize 진행
        # summarize 진행 후 df 가져와서 DB로 보내기
    files = getCrawledFileNames()
    print(files)
    for file in files:
        fileName = file[:-4]
        try:
            summarizer.setFileName(fileName)
            summarizer.loadDataframe()
            await summarizer.summarizeContents()

            summarizer.df.drop(['Unnamed: 0'], axis = 1, inplace = True)
            summarizer.df = summarizer.df.astype({"category" : "str", "region" : "str", "image" : "str"})
            summarizer.df["region"] = [summarizer.df.loc[i]['region'].replace('\'', '')[1:-1].split(', ') for i in summarizer.df.index]
            summarizer.df["image"] = [summarizer.df.loc[i]['image'].replace('\'', '')[1:-1].split(', ') for i in summarizer.df.index]
            summarizer.df["image"] = sendImagesToStorage(fileName, summarizer.df["image"].tolist())
            summarizer.df["post_date"] = datetime.utcnow()
            print(summarizer.df["image"].tolist())

            for i in summarizer.df.index:
                data = summarizer.df.loc[i].to_dict()
                print(data)
                sendDataToDB(data)

            summarizer.saveDataframeToCSV()
        except Exception as e:
            print(e, f"{fileName} 요약 실패")

if __name__ == "__main__":
    asyncio.run(main())