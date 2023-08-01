from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup

# Create a WebDriver instance
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Define the target URL
url = "https://seoulcbid.or.kr/bbs/board.php?bo_table=0702"
driver.get(url)

# Find all the rows within the tbody element
rows = driver.find_elements(By.XPATH, '//tbody/tr')

# Get the current date
current_date = datetime.date.today()

# Collect the post data
for row in rows:
    try:
        # Extract the post date from the internal page
        date_element = row.find_element(By.CSS_SELECTOR, 'span[title="작성일"]')
        date_string = date_element.text
        post_date = datetime.datetime.strptime(date_string.split()[1].strip(), '%y-%m-%d').date()

        # Calculate the date difference in days
        date_diff = (current_date - post_date).days

        # Check if the post is within the last month
        if date_diff <= 30:
            # Extract the link to the post
            link_element = row.find_element(By.TAG_NAME, 'a')
            post_link = link_element.get_attribute('href')

            # Navigate to the post page
            driver.get(post_link)

            # Extract the content of the post
            content_element = driver.find_element(By.ID, 'bo_v_con')
            content_html = content_element.get_attribute('outerHTML')
            content_soup = BeautifulSoup(content_html, 'html.parser')
            content = content_soup.get_text(strip=True)

            # Extract the title of the post
            title_element = content_soup.find('strong')
            title = title_element.get_text(strip=True)

            # Extract the image URL if it exists
            image_element = content_soup.find('figure', class_='image')
            image_url = image_element.find('img')['src'] if image_element else None

            # Print the extracted data
            print(f"제목: {title}")
            print(f"내용: {content}")
            print(f"이미지 URL: {image_url}")
            print("--------------------")

    except Exception as e:
        print(f"링크 처리 중 오류 발생: {e}")

    # Wait for a moment before processing the next link
    time.sleep(1)

# Close the WebDriver
driver.quit()
