import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://markets.ft.com"
SEARCH_URL = BASE_URL + "/data/search?query="
isins = ["SE0008103071"]
LEI_REGEX = r'\b[A-Z0-9]{20}\b'

def search_on_isin(isin):
    url = SEARCH_URL + isin
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None
    html = str(response._content)
    search_result = html.split("mod-ui-table__cell--text")[1].split("href=")[1].split(" ")[0][1:-1]
    # print(search_result)
    fund_name = find_isin_from_page(search_result)
    return fund_name

def find_isin_from_page(target_url):

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)

    url = BASE_URL + target_url
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[3]/section/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]"))
        )
        
        fund_name_element = driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/section/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]")
        fund_name = fund_name_element.text
        print(f"Fund name: {fund_name}")
        
    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        driver.quit()
        if fund_name:
            return fund_name
        return None


def main():
    for isin in isins:
        print(f"Fetching LEI for {isin}...")
        fund = search_on_isin(isin)
        if fund:
            print(f"Fund name for ISIN {isin}: {fund}")
        else:
            print(f"No LEI found for isin {isin}")

if __name__ == "__main__":
    main()
