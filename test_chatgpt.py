import pandas as pd
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Setting
openai.organization = os.getenv('OPENAI_ORGANIZAION_ID')
openai.api_key = os.getenv('OPENAI_API_KEY') 


def get_openai_response(prompt, print_output=False):

    completions = openai.Completion.create(
        engine='text-davinci-003',  # Determines the quality, speed, and cost.
        temperature=0.5,            # Level of creativity in the response
        prompt=prompt,           # What the user typed in
        max_tokens=1100,             # Maximum tokens in the prompt AND response
        # n=1,                        # The number of completions to generate
        stop=['BYOURSIDE_DONE'],                  # An optional setting to control response generation
    )
    # Displaying the output can be helpful if things go wrong
    if print_output:
        print(completions)

    # Return the first choice's text
    return completions.choices[0].text


## 1.Get data
df = pd.read_csv('./data.csv')

result_list = []

## 2. Make prompt
prompt = 'Rewrite this script professionally and add subheadings No Titles No Introduction No Conclusion.'

## Organize data
for ind, row in df.iterrows():
    eng_result = ''
    title = row['title']
    script = row['script']

    # script가 길 경우
    '''
        for s in script:
        request = prompt + s
        response = get_openai_response(request)
        eng_result += response
    '''

    # scipt가 짧을 경우
    request = "뒤에 오는 문장을 5줄로 요약해줘./n" + script + "BYOURSIDE_DONE"
    response = get_openai_response(request)
    summary_result = response


    result_list.append({'title': title, 'summary': summary_result})

df_result = pd.DataFrame(result_list)

df_result.to_csv('result/summary.csv', mode='a', index=False, encoding='utf-8-sig')