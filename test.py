import pandas as pd
from main import constants
from datetime import datetime
import os
from sendToDB import sendImagesToStorage, sendDataToDB

img_df = pd.read_csv(f"result/crawl/jgcrc.csv", parse_dates=['date'])
summary_df = pd.read_csv(f"result/summary/jgcrc.csv", parse_dates=['date'])
summary_df.drop(['Unnamed: 0'], axis = 1, inplace = True)
img_df['image'] = [img_df .loc[i]['image'].replace('\'', '')[1:-1].split(', ') for i in img_df.index]

images = img_df['image']
print(images)
summary_df['image'] = sendImagesToStorage('jgcrc', images)
summary_df["post_date"] = datetime.utcnow()

for i in summary_df.index:
    data = summary_df.loc[i].to_dict()
    print(data)
    sendDataToDB(data)

try:
    summary_df = summary_df.astype({"category" : "string"})
    summary_df.to_csv(f'result/summary/jgcrc.csv', mode='w')
except Exception as e:
    print(e, ": Make summary result csv file")
