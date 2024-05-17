from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import requests
import pandas as pd
import re
import argparse
import random
waiting_seg = [4, 5, 6]

parser = argparse.ArgumentParser()
parser.add_argument('search_phrase', help='the search phrase to use')
parser.add_argument('--category', help='the news category/section/topic to use (optional)')
parser.add_argument('--months', type=int, default=1, help='the number of months for which to receive news')
args = parser.parse_args()

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

driver.get('https://gothamist.com/')
wait = WebDriverWait(driver, random.choice(waiting_seg))

search_field = driver.find_element(by=By.CSS_SELECTOR,value="div[class='search-button'] > button")
search_field.click()

searchBar = wait.until(EC.presence_of_element_located( (By.NAME,"q" ) ) ) 
searchBar.send_keys(args.search_phrase,Keys.ENTER)

search_results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='card-title'] > a")))

data = {'Title': [], 'Date': [], 'Description': [], 'Picture Filename': [], 'Count of Search Phrases': [], 'Contains Money': []}
df = pd.DataFrame(data)

for i in range(len(search_results)):
    search_results[i].click()

    wait.until(EC.presence_of_element_located((By.TAG_NAME,"h1")))

    title_element = driver.find_element(by=By.TAG_NAME,value="h1")
    title = title_element.get_property("innerText")

    description_element = driver.find_element(by=By.CSS_SELECTOR,value="meta[name='description']")
    description = description_element.get_attribute("content") if description_element else ''

    date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"div[class='date-published'] > p")))
    date = date_element.get_property("innerText")

    count = len(re.findall(r'\bsearch phrase\b', title.lower() + ' ' + description.lower()))

    contains_money = bool(re.search(r'\b\$[\d,]+(\.\d{1,2})?|\b\d+\s*dollars?\b', title.lower() + ' ' + description.lower()))

    picture_element = driver.find_element(By.CSS_SELECTOR,'div[class="simple-responsive-image-holder"] > img')
    picture_url = picture_element.get_attribute('src') if picture_element else ''
    print(picture_url)
    if picture_url:
        response = requests.get(picture_url)
        filename = f'picture_{title.replace(" ", "_")}.jpg'
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        filename = ''

    new_data = {'Title': [title], 'Date': [date], 'Description': [description], 'Picture Filename': [filename], 'Count of Search Phrases': [count], 'Contains Money': [contains_money]}
    new_df = pd.DataFrame(new_data)
    df = pd.concat([df, new_df], ignore_index=True)

    if args.search_phrase in title:
        driver.execute_script("window.history.go(-1)")
        search_results = driver.find_elements(by=By.CSS_SELECTOR,value="div[class='card-title'] > a")
    else:
        break
# Save the DataFrame to an Excel file
df.to_excel('news.xlsx', index=False)

# Close the WebDriver
driver.quit()