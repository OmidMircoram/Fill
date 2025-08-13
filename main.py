#%%
import pickle
import pandas as pd
from engine_elias import calculate_portfolio
from read_xml_elias import main, old_main
from scrape import scrape


def entrypoint():
    fund_info, all_available_funds = load_new_data()
    holdings={0:{'Handelsbanken Aktiv 100':1000,},
              }
    current_portfolio = calculate_portfolio(holdings, fund_info, all_available_funds)
    return fund_info, all_available_funds, current_portfolio

def get_data():
    return load_existing_data()
    

def load_new_data():
    """Runs once every Q."""
    alla_fonder, mappning = main()
    andel_old, andel_new = scrape(alla_fonder)
    mappning = pd.concat([mappning, andel_new], axis=0)
    return alla_fonder, mappning


def load_existing_data(filename):
    """Ladda alla_fonder, mappning, andelsklasser"""
    file = open(f"{filename}.pkl", "rb") 
    obj = pickle.load(file)
    return obj

def save_to_pickle(obj, name):
    with open(f"./{name}.pkl", "wb") as f:
        pickle.dump(obj, f)
def load_data(): 
    alla_fonder=load_existing_data("alla_fonder")

    mappning=load_existing_data("mappning")
    andel_new=load_existing_data("andel_new")
    andel_old = load_existing_data("andel_old")
    mappning_after_scrape = load_existing_data("mappning_after_scrape")
    return alla_fonder,mappning_after_scrape
#%%
# alla_fonder, mappning = main()

# andel_old, andel_new = scrape(alla_fonder)
# mappning_after_scrape = pd.concat([mappning, andel_new], axis=0)

#%%
# save_to_pickle(alla_fonder, "alla_fonder")
# save_to_pickle(mappning, "mappning")
# save_to_pickle(mappning_after_scrape, "mappning_after_scrape")
# save_to_pickle(andel_new,"andel_new")
# save_to_pickle(andel_old,"andel_old")

#%%
# from engine_elias import calculate_portfolio
alla_fonder,mappning_after_scrape=load_data()
holdings={0:{"Handelsbanken Aktiv 100":100}}


current_portfolio = (calculate_portfolio(holdings, alla_fonder.copy(), mappning_after_scrape)).reset_index()
current_portfolio=current_portfolio.loc[current_portfolio["instrument_isin"]!=""]
current_portfolio=current_portfolio.sort_values(by="andel_av_fond",ascending=False)
current_portfolio

# %%
