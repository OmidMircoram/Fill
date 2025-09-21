#%%

import pickle
import pandas as pd
from scrape import scrape
from read_xml_elias import main

def load_new_data():
    """
    Function that triggers the data import flow from all sources.
    Just make sure the latest data from FI is downloaded in a file named xml in the repo.
    Will also pickle the necessary files.
    """
    all_funds, mapping = main()
    andel_old, scrape_mapping = scrape(all_funds)
    mapping_after_scrape = pd.concat([mapping, scrape_mapping], axis=0)
    mapping_after_scrape=mapping_after_scrape.drop_duplicates(subset=["instrument_isin"],keep="last")
    save_to_pickle(all_funds, "all_funds")
    save_to_pickle(mapping_after_scrape, "mapping_after_scrape")

def save_to_pickle(obj, name):
    with open(f"./{name}.pkl", "wb") as f:
        pickle.dump(obj, f)

#%%
load_new_data()