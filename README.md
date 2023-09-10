# Auto-information

'Beeside'의 정보 데이터 크롤링을 위한 레포지토리<br/>
Repository for crawling information data in 'Beeside'<br/><br/>

**The app source code of the information service can be found in the 'Byourside' repository.*

<br/><br/>


## Technologies
Project is created with:  

|                |NAME                          |
|----------------|-------------------------------|
|Language         |`Python`            |
|Framework|`Firebase` `Chat GPT API` `Selenium` `Pandas` `asyncio & aiohttp` `Amazon EC2` `Crontab` `AWS Lambda` `Amazon Event Bridge`|
|IDE     |`VScode`|
|Source Code Management     |`Git` `Github`|
|Project Document Management     |`Jira` `Confluence` `Wakatime`|
|Collaboration Tools |`Zoom` `Google Meet`|

<br/><br/>

#### Chat GPT API
- GPT 선택 이유
  - 요약을 하기 위해 참고했던 GPT의 종류는 총 4가지로 chatGPT, koGPT, Bard, Llama2입니다.<br />다음 표는 생성 모델 각각에 대해서 직접 테스트를 진행해 파악한 특징입니다.
    ![image](https://github.com/GYEOTEURO/Auto-information/assets/66138381/c3e157a6-6b2d-4710-9716-6955fe1cc72f)
  - 위와 같은 장단점을 비교해 저희 프로젝트에 가장 알맞은 모델을 찾고자 노력했습니다. 결과적으로 사용자에게 높은 품질의 콘텐츠를 제공하기 위해, 요약의 성능이 우수한 chatGPT를 사용하여 정보 제공 기능을 구현하기로 결정했습니다. 이를 위해 추가 비용이 발생할 수 있더라도, 사용자 경험과 정보 품질을 우선 고려한 결정입니다.<br /><br/>
- GPT 모델
  - 초기에는 GPT 모델 중에서 Davinci 모델의 text-davinci-003을 사용하였으며, 이 모델은 텍스트의 의도를 이해하는 능력에서 우수하여 요약 및 콘텐츠 생성에 큰 장점을 가졌습니다. 그러나 API 호출당 비용이 높고 처리 속도가 다른 모델에 비해 느린 단점이 있었습니다. 이후에 gpt-3.5-turbo 모델로 변경하였는데, 이 모델은 채팅에 최적화되어 있으면서도 text-davinci-003와 비교했을 때 1/10배 정도의 비용 효율을 보여줍니다. OpenAI에서도 GPT-3.5 모델 중에서 가장 유능하고 비용 효율적인 모델로 소개하고 있습니다.
  - 또한, OpenAI에서 1세대 텍스트 임베딩 모델의 지원을 중단할 예정이며, 이로 인해 2024년 1월 4일에 서비스가 종료될 예정이기 때문에 지속가능한 개발을 위해 모델을 변경하였습니다.
  - GPT 모델을 사용하기 위한 명령문 및 다양한 파라미터 정보는 constants.yaml 파일에 정리하여 효율적으로 관리하였습니다.
<br/>

#### asyncio & aiohttp
- 요약문을 생성하기 위해 chatGPT를 이용한 작업을 병렬로 처리하고 성능을 향상시키기 위해 asyncio와 aiohttp를 함께 사용했습니다. Python의 request는 동기적으로 요청을 처리하기 때문에, 비동기로 HTTP 요청을 처리하기 위해 aiohttp도 함께 활용하였습니다.
  ```
  async def get_openai_response(self, prompt, print_output=False):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(
                constants['model_parameter']['url'],
                headers={'Authorization': f'Bearer {openai.api_key}',
                         "Content-Type": "application/json"},
                json={
                    'messages': [
                        constants['prompt']['system_message'],
                        {"role": "user", "content": prompt}
                    ],
                    'model': constants['model_parameter']['model']['large'],
                    'temperature': constants['model_parameter']['temperature']['low'],
                    'max_tokens': constants['model_parameter']['max_token']['1k']
                }
            ) as response:
                response_data = await response.json()
                if print_output:
                   print(response_data)

                return response_data["choices"][0]["message"]["content"]
  ```

- 원문의 길이가 일정 토큰 크기를 초과할 경우, 이를 chunk 단위로 분할한 후 개별 chunk들을 동시에 GPT에 요청하여 처리 시간을 단축시켰습니다. 이로써 단일 스레드로 많은 네트워크 연결을 처리하는 서버에서 발생할 수 있는 오류 가능성을 최소화할 수 있었습니다.
  ```
  async def generateSummary(self, content):

        text = content
        max_cycle = int(len(text) / constants['chunk_size']['small']) + 1
        summaryPrompt = constants['prompt']['summary']
        summary = ''

        for cycle in range(max_cycle):
            chunks = textwrap.wrap(text, constants['chunk_size']['small'])

            if len(chunks) == 1:
                summary = await self.get_openai_response(text + summaryPrompt)
                break

            tasks = [self.get_openai_response(chunk + summaryPrompt) for chunk in chunks]
            chunkSummaries = await asyncio.gather(*tasks)
            summary = ' '.join(chunkSummaries)

            text = summary

        return summary
  ```

#### AWS Lambda & Amazon Event Bridge
- AWS Lambda와 Amazon Event Bridge를 활용하여 원하는 시간대에 EC2 인스턴스를 시작하고 중지하여 서버 비용을 효과적으로 관리하고, 사용한 리소스만큼의 비용을 부과받아 비용 효율을 높였습니다. 이를 구체적으로 설명하면, AWS Lambda를 사용하여 EC2 인스턴스를 시작하고 중지하는 코드 함수를 작성하고, Amazon Event Bridge를 활용하여 특정 시간대(예: 매주 일요일 23시 55분)에 Lambda 함수를 실행하도록 예약하였습니다. 이렇게 함으로써 필요한 시간에 EC2 인스턴스를 활성화하고 필요 없는 시간에는 중지하여 리소스를 효율적으로 활용할 수 있게 되었습니다.

<br/><br/>

## Feature
  사용자의 정보에 기반한 맞춤 정보 제공 기능입니다. 정보 게시판을 통해 중앙부처,지자체,재단 등 각종 웹사이트에 분산되어 있는 정보를 한 곳에 모아 사용자에게 제공합니다.이를 통해 장애인 및 보호자가 웹사이트를 돌아다니며 흩어진 정보를 수집하는 어려움을 줄일 수 있습니다. 더불어 장애 유형이나 지역 등 사용자의 개별적 특성에 따라 정보를 맞춤 제공하며, 사용자는 쉽고 간편하게 받을 수 있는 지원을 확인하고 신청할 수 있습니다.<br/><br/>
![image](https://github.com/GYEOTEURO/Byourside/assets/66212424/30e668f5-1b63-4b5d-956c-ef5bf1436396)  

![image](https://github.com/GYEOTEURO/Byourside/assets/66212424/a817d10f-37e7-4f46-916c-cc25ce65e980)

![image](https://github.com/GYEOTEURO/Byourside/assets/66212424/21e26b70-53bb-4257-b709-c5a5e06f5186)  


<br/><br/>

## Architecture
![image](https://github.com/GYEOTEURO/Byourside/assets/66212424/c786e129-2ba9-4f24-b41f-225d9f8f5aae)

<br/><br/>


## Developers
<div align='center'>
<table>
    <thead>
        <tr>
            <th colspan="5">GYEOTEURO</th>
        </tr>
    </thead>
    <tbody>
        <tr>
          <tr>
            <td align='center'><a href="https://github.com/anjiwon319"><img src="https://avatars.githubusercontent.com/u/66212424?v=4" width="100" height="100"></td>
            <td align='center'><a href="https://github.com/Shin-MG"><img src="https://avatars.githubusercontent.com/u/66138381?v=4" width="100" height="100"></td>
            <td align='center'><a href="https://github.com/YunHaaaa"><img src="https://avatars.githubusercontent.com/u/63325450?v=4" width="100" height="100"></td>
          </tr>
          <tr>
            <td align='center'>안지원</td>
            <td align='center'>신민경</td>
            <td align='center'>윤하은</td>
          </tr>
        </tr>
    </tbody>
</table>
</div>

&nbsp; 
