#%%
import pickle
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
def scrape(all_funds):
    all_funds1 = {}
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    url="https://markets.ft.com/data/"
    driver.get(url)
    driver.maximize_window()
    accept_cookies(driver)
    scrape_mapping = pd.DataFrame()
    for key in all_funds:
        fondnamn=all_funds[key]["overview_dict"]["fond_namn"]
        fondnamn_fixad=fondnamn.replace(" ","+")
        # print(fondnamn_fixad)
        url="https://markets.ft.com/data/search?query="+fondnamn_fixad
        driver.get(url)        
        # time.sleep(1)
        try: 
            tabell = driver.find_element(By.CLASS_NAME, "mod-ui-table--freeze-pane")
            rader = tabell.find_elements(By.CLASS_NAME, "mod-ui-table__cell--text")
            
            if len(rader) >0:  
                all_funds1[fondnamn] = {} # creates new dict with fondnamn as key and empty dict as value.
                for i in range(0, len(rader), 2): # Should we really use step=2, will we lose half of andelsklasser?
                    andelsklass = rader[i].text # Andelsklass is the name of the fund.
                    isin = rader[i+1].text.split(":")[0] if i+1 < len(rader) else None # selects each isin code respectively.
                    print(isin)
                    if isin==key: # If true it is a top_key-fund and it is allready in the mapping with instrument_isin=top_key
                        continue
                    all_funds1[fondnamn][andelsklass]=isin #??????????????? blir som ett index av fondnamn och fondnamn och isin är värdet i intercept.
                    # If not a top_key-fund, the add it in the scrape_mapping
                    scrape_mapping=pd.concat([scrape_mapping,pd.DataFrame({"instrument_namn": [andelsklass], "instrument_isin": [isin], "top_key": [key]})],axis=0)    
                # time.sleep(0)
                # driver.close()
        except: 
            print(fondnamn_fixad, "skippad")
            continue
    return all_funds1, scrape_mapping
#%%


# a=scrape()