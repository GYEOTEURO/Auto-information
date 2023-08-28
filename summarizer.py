# -*- coding: utf-8 -*-

from bardapi import Bard, BardCookies
from bardapi.constants import SESSION_HEADERS
import openai
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import json
import yaml

# Summarize에 쓸 constants load
with open('constants.yaml', encoding='UTF-8') as f:
    constants = yaml.load(f, Loader=yaml.FullLoader)

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
    disabilityTypes = []
    regions = []

    def __init__(self, gptName) -> None:
        load_dotenv()
        self.gptName = gptName
        if self.gptName == "Bard":
            self.token = os.getenv("BARD_COOKIE_KEY")
        
        elif gptName == "chatGPT":
            openai.organization = os.getenv('OPENAI_ORGANIZAION_ID')
            openai.api_key = os.getenv('OPENAI_API_KEY') 

        self.makeInstanceOfGPT()

    def setFileName(self, fileName):
        self.fileName = fileName
        self.summaries = []
        self.categories = []
        self.disabilityTypes = []
        self.regions = []

    def makeInstanceOfGPT(self):
        if self.gptName == "Bard":
            session = requests.Session()
            session.headers = SESSION_HEADERS
            session.cookies.set("__Secure-1PSID", self.token)
            session.cookies.set("__Secure-1PSIDTS", os.getenv("BARD_COOKIE_1PSIDTS"))
            session.cookies.set("__Secure-1PSIDCC", os.getenv("BARD_COOKIE_1PSIDCC"))
            self.gpt = Bard(token=self.token, timeout=30, session=session)

        elif self.gptName == "chatGPT":
            self.gpt = openai.Completion

    def loadDataframe(self):
        try:
            self.df = pd.read_csv(f"result/crawl/{self.fileName}.csv", parse_dates=['date'])

        except Exception as e:
            print(e, ": Load result csv file")
        
    def saveDataframeToCSV(self):
            try:
                self.df.to_csv(f'result/summary/{self.fileName}.csv', mode='a')
            except Exception as e:
                print(e, ": Make summary result csv file")

    def organizeSummary(self, summary):
        summary  = summary.replace("*", "")
        summary = summary.replace("{", "$").replace("}", "$")
        summary = '{' + summary.split("$")[1] + '}'

        try:
            summary = json.loads(summary)
        except json.decoder.JSONDecodeError as e:
            print("JSON Decode Error : retry generate summarize")
        summary = summary['summary'] 

        return summary
    

    def organizeDetection(self, detection):
        detection = detection.replace("{", "$").replace("}", "$")
        detection = "{" + detection.split("$")[1] + "}"
        try:
            detection = json.loads(detection)
        except json.decoder.JSONDecodeError as e:
            print("JSON Decode Error : retry generate detection")

        return detection
    
    def organizeRegion(self, region):
        if region == "전국":
            region = "전체"
        elif region == "서울" or region == "서울특별시":
            region = "서울시"
        return [region]
        
    def organizeCategory(self, category):
        defaultCategory = "교육/활동"
        if category in ["교육/활동", "보조기기", "지원금", "돌봄 서비스"]:
             return category
        else:
            return defaultCategory
    
    def getSummaryAndCategoryAndDisabilityTypeAndRegion(self, content):
        summaryPrompt = content + constants['prompt']['summary']

        if self.gptName == "Bard":
            summary = self.gpt.get_answer(summaryPrompt)['content']
            print("-------------")
            print("summary 결과: \n")
            print(summary)
            summary = self.organizeSummary(summary)

            
            prompt = summary + constants['prompt']['detect']
            detection = self.gpt.get_answer(prompt)['content']
            print("-----------")
            print("json 전처리 결과:")
            print(detection)
            detection = self.organizeDetection(detection)
            print("-------------")
            print("json 후처리 결과: \n")
            print(detection)
            disabilityType = detection['disability_type']
            category = self.organizeCategory(detection['category'])
            region = self.organizeRegion(detection['region'])

        elif self.gptName == "chatGPT":
            summaryResponse = self.gpt.create(
                engine='text-davinci-003',  # Determines the quality, speed, and cost.
                temperature=0.5,            # Level of creativity in the response
                prompt=summaryPrompt,           # What the user typed in
                max_tokens=2000,             # Maximum tokens in the prompt AND response
                # n=1,                        # The number of completions to generate
                stop=['BYOURSIDE_DONE'],                  # An optional setting to control response generation
            )
            print(summaryResponse.choices[0])


        return summary, category, disabilityType, region
    
    def makeSummaryResultToDataframe(self):
        self.df.rename(columns={'content':'summary'}, inplace=True)
        self.df["summary"] = self.summaries
        self.df["category"] = self.categories
        self.df["disability_type"] = self.disabilityTypes
        self.df["region"] = self.regions

    def summarizeContents(self):
        self.loadDataframe()
        contents = self.df['content'].values
        for content in contents:
            summary, category, disabilityType, region = self.getSummaryAndCategoryAndDisabilityTypeAndRegion(content)
            self.summaries.append(summary)
            self.categories.append(category)
            self.disabilityTypes.append(disabilityType)
            self.regions.append(region)

        self.makeSummaryResultToDataframe()


class chatGPT(Summarizer):

    def __init__(self, gptName) -> None:
        super().__init__("chatGPT")

    def makeInstanceOfGPT(self, gptName):
        openai.organization = os.getenv('OPENAI_ORGANIZAION_ID')
        openai.api_key = os.getenv('OPENAI_API_KEY') 



if __name__ == "__main__":
    c = Summarizer("chatGPT")
    c.setFileName("seoul_edu")
    c.summarizeContents()