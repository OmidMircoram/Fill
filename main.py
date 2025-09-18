#%%
import pickle
import pandas as pd
from engine_elias import calculate_portfolio


def load_existing_data(filename):
    """Ladda all_funds, mapping, andelsklasser"""
    file = open(f"{filename}.pkl", "rb") 
    obj = pickle.load(file)
    return obj


def load_data(): 
    """
    Load stored data from pickled files.
    """
    all_funds=load_existing_data("all_funds")
    mapping_after_scrape = load_existing_data("mapping_after_scrape")
    return all_funds, mapping_after_scrape



#%%
all_funds,mapping_after_scrape=load_data()
input_dict={0:{"Handelsbanken Aktiv 100":100, "qweqwe":100, "Axfood":100}}


current_portfolio = (calculate_portfolio(input_dict, all_funds.copy(), mapping_after_scrape)).reset_index()
# current_portfolio=current_portfolio.sort_values(by="andel_av_fond",ascending=False)
current_portfolio

# %%
current_portfolio.sort_values(by="andel_av_fond")