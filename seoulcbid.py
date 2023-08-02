from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import datetime
import re

def find_post_links():
    s = Service('./chromedriver')
    driver = webdriver.Chrome(service=s)

    url = "https://seoulcbid.or.kr/bbs/board.php?bo_table=0702"
    driver.get(url)

    # Find all the rows within the tbody element
    rows = driver.find_elements(By.XPATH, '//tbody/tr')

    # Get the current date
    current_date = datetime.date.today()

    # Collect the post links with dates
    post_links = []

    # Collect the post data
    for row in rows:
        try:
            # Find the span element containing the date
            date_element = row.find_element(By.XPATH, './/td[@class="td_date hidden-xs text-left"]')
            date_string = date_element.text

            # Extract the date from the string
            post_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')

            # Calculate the date difference in days
            date_diff = (current_date - post_date.date()).days

            # Check if the post is within the last month
            if date_diff <= 30:
                # Find the link to the post within the row
                link_element = row.find_element(By.XPATH, './/a[contains(@href, "wr_id=")]')
                link = link_element.get_attribute('href')

                # Extract the wr_id from the link using regular expressions
                wr_id_match = re.search(r'wr_id=(\d+)', link)
                if wr_id_match:
                    wr_id = wr_id_match.group(1)
                    post_links.append((wr_id, link, post_date))

        except Exception as e:
            print(f"날짜 처리 중 오류 발생: {e}")

    driver.quit()

    return post_links

# Example usage
post_links = find_post_links()

# Set up the Chrome driver
s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

# Iterate over the post links and extract the data for the posts within the last month
for wr_id, link, post_date in post_links:
    try:
        # Navigate to the link
        driver.get(link)
        print(link)

        # Wait for the page to load
        time.sleep(3)

        # Extract the HTML content of the post
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract the title
        title_element = soup.select_one('h6.pull-left')
        title = title_element.text.strip() if title_element else None
        print(f"Title: {title}")

        # Extract the content
        content_element = soup.select_one('#bo_v_con')
        content = content_element.text.strip() if content_element else None
        print(f"Content: {content}")

        # Extract the images
        image_elements = soup.select('#bo_v_con img')
        image_urls = [img['src'] for img in image_elements]
        print("Images:")
        for img_url in image_urls:
            print(img_url)

        print(f"Date: {post_date}")

    except Exception as e:
        print(f"Error in post with wr_id {wr_id}: {e}")

# Quit the driver after processing all post links
driver.quit()
