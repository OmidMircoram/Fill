#%%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
def scrape():
    global alla_fonder1
    alla_fonder1 = {}
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    url="https://markets.ft.com/data/"
    driver.get(url)
    driver.maximize_window()
    accept_cookies(driver)

    for key in alla_fonder:
        fondnamn=alla_fonder[key]["översikt"]["fond_namn"]
        fondnamn_fixad=fondnamn.replace(" ","+")
        print(fondnamn_fixad)
        url="https://markets.ft.com/data/search?query="+fondnamn_fixad
        driver.get(url)
        
        # time.sleep(1)
        try: 
            tabell = driver.find_element(By.CLASS_NAME, "mod-ui-table--freeze-pane")
            rader = tabell.find_elements(By.CLASS_NAME, "mod-ui-table__cell--text")
            
            if len(rader) >0:  
                alla_fonder1[fondnamn] = {}
                for i in range(0, len(rader), 2):
                    andelsklass = rader[i].text
                    isin = rader[i+1].text.split(":")[0] if i+1 < len(rader) else None
                    alla_fonder1[fondnamn][andelsklass]=isin
                # time.sleep(0)
                # driver.close()
        except: 
            print(fondnamn_fixad, "skippad")
            continue
    return alla_fonder1
#%%
import pickle
with open("./alla_andelsklasser.pkl", "wb") as f:
        pickle.dump(alla_fonder1, f)

# a=scrape()