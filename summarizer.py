from bardapi import Bard
import openai
import os
from dotenv import load_dotenv
import requests
import pandas as pd

'''
# session 을 유지하고 싶을 경우
session = requests.Session()
session.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
session.cookies.set("__Secure-1PSID", os.getenv("BARD_COOKIE_KEY"))
'''


class Summarizer:
    fileName = ''
    summaries = []
    categories = []
    disablityTypes = []

    def __init__(self, gptName) -> None:
        load_dotenv()
        if gptName == "Bard":
            self.token = os.getenv("BARD_COOKIE_KEY")
        
        elif gptName == "chatGPT":
            openai.organization = os.getenv('OPENAI_ORGANIZAION_ID')
            openai.api_key = os.getenv('OPENAI_API_KEY') 

        self.makeInstanceOfGPT(gptName)

    def setFileName(self, fileName):
        self.fileName = fileName

    def makeInstanceOfGPT(self, gptName):
        if gptName == "Bard":
            self.gpt = Bard(token=self.token, timeout=30)

    def loadDataframe(self):
        try:
            self.df = pd.read_csv(f"result/crawl/{self.fileName}.csv")

        except Exception as e:
            print(e, ": Load result csv file")
        
    def saveDataframeToCSV(self):
            try:
                self.df.to_csv(f'result/summary/{self.fileName}.csv', mode='a')
            except Exception as e:
                print(e, ": Make summary result csv file")

    def detectDisablityType(self, sentences):
        sentence = sentences.split('.')[0]
        types = []
        if sentence.find("발달"):
            types.append("발달")
        if sentence.find("뇌병변"):
            types.append("뇌병변")

        if len(types) > 1:
            return "전체"
        else:
            return types[0]
        
    def detectCategory(self, sentences):
        sentence = sentences.split('.')[0]
        defaultCategory = "지원금"
        for category in ["교육", "보조기기", "지원금", "돌봄 서비스"]:
            if category in sentence:
                return category
        return defaultCategory
                
    def getSummaryAndCategoryAndDisabilityType(self, content):
        prompt = content + "\n" + "위 내용을 5줄로 요약해줘. 그리고 주제가 (교육, 보조기기, 지원금, 돌봄 서비스) 중 어디에 가장 적합한 지 알려줘. \
            또한 장애 유형은 (발달 장애, 뇌병변 장애) 중 어디에 가장 적합한 지 알려줘"
        response = self.gpt.get_answer(prompt)['content']
        print(response)
        print("---------------------------")

        summary, category, disablityType = map(str, response.split(sep = "\n\n", maxsplit=2))
        disablityType = self.detectDisablityType(disablityType)
        category = self.detectCategory(category)

        print(f"장애 유형: {disablityType}, 카테고리: {category}\n 요약문:\n{summary}")
        print("============================")

        return summary, category, disablityType
    
    def makeSummaryResultToDataframe(self):
        self.df.rename(columns={'content':'summary'}, inplace=True)
        self.df["summary"] = self.summaries
        self.df["category"] = self.categories
        self.df["disablity_type"] = self.disablityTypes

    def summarizeContents(self):
        self.loadDataframe()
        contents = self.df['content'].values
        for content in contents:
            summary, category, disablityType = self.getSummaryAndCategoryAndDisabilityType(content)
            self.summaries.append(summary)
            self.categories.append(category)
            self.disablityTypes.append(disablityType)

        self.makeSummaryResultToDataframe()