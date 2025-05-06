#%%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
def accept_cookies(driver):
    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, "iframe")))
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Found {len(iframes)} iframes")

    for iframe in iframes:
        driver.switch_to.frame(iframe)
        try:
            time.sleep(0.5)
            accept_btn = driver.find_element(By.XPATH, "//button[@title='Accept Cookies']")
            accept_btn.click()
            print("Cookies accepted inside iframe.")
            driver.switch_to.default_content()
            break
        except NoSuchElementException:
            driver.switch_to.default_content()
            continue
#%%
fondnamn="Handelsbanken Global Digital"
fondnamn_fixad=fondnamn.replace(" ","+")

driver = webdriver.Chrome()
url="https://markets.ft.com/data/search?query="+fondnamn_fixad
driver.get(url)
driver.maximize_window()
accept_cookies(driver)
time.sleep(1)
tabell = driver.find_element(By.CLASS_NAME, "mod-ui-table--freeze-pane")
rader = tabell.find_elements(By.CLASS_NAME, "mod-ui-table__cell--text")

alla_fonder = {}
alla_fonder[fondnamn] = {}
for i in range(0, len(rader), 2):
    andelsklass = rader[i].text
    isin = rader[i+1].text.split(":")[0] if i+1 < len(rader) else None
    alla_fonder[fondnamn][andelsklass]=isin
time.sleep(3)
driver.close()