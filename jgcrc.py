from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from dateutil.relativedelta import relativedelta

now_date = datetime.datetime.now()
before_one_month = now_date + relativedelta(months=-1)

print(str(before_one_month))

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = "https://www.jgcrc.or.kr/notice"
driver.get(url)
# Find all the rows within the tbody element
rows = driver.find_elements(By.XPATH, '//tbody/tr')

# Get the current date
current_date = datetime.date.today()

# Collect the post links
post_links = []
for row in rows:
    link_element = row.find_element(By.TAG_NAME, 'a')
    link = link_element.get_attribute('href')
    post_links.append(link)

# Iterate over the post links and extract the data for the posts within the last month
for link in post_links:
    try:
        # Navigate to the link
        driver.get(link)

        # Extract the post date from the internal page
        date_string = driver.find_element(By.CLASS_NAME, 'view_info').text
        post_date = datetime.datetime.strptime(date_string.split('작성일')[1].strip(), '%Y.%m.%d').date()

        # Calculate the date difference in days
        date_diff = (current_date - post_date).days

        # Check if the post is within the last month
        if date_diff <= 30:
            # Extract the content and other optional elements from the internal page
            title = driver.find_element(By.CLASS_NAME, 'title_view').text
            author_date = driver.find_element(By.CLASS_NAME, 'view_info').text
            content = driver.find_element(By.CLASS_NAME, 'view_detail').text

            # Extract the image URL if it exists
            try:
                image_element = driver.find_element(By.CLASS_NAME, 'view_image')
                image_url = image_element.get_attribute('href')
            except :
                image_url = None

            # Extract other optional elements if they exist
            try:
                attachment_element = driver.find_element(By.CSS_SELECTOR, 'ul.ul_view_01 li em')
                attachment_name = attachment_element.text
                attachment_link = attachment_element.find_element(By.XPATH, './following-sibling::span/a').get_attribute('href')
            except :
                attachment_name = None
                attachment_link = None

            # Print the extracted data
            print(f"제목: {title}")
            print(f"작성자 및 날짜: {author_date}")
            print(f"내용: {content}")
            print(f"이미지 URL: {image_url}")
            print(f"첨부 파일: {attachment_name}")
            print(f"첨부 파일 링크: {attachment_link}")
            print("--------------------")

    except Exception as e:
        print(f"링크 처리 중 오류 발생: {e}")

    # Wait for a moment before processing the next link
    time.sleep(1)
