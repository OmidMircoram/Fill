#%%

import pickle
import pandas as pd
from scrape import scrape
from read_xml_elias import main
from engine import calculate_portfolio
from isin_to_tickers import get_isin
def calc_fund_holdings_looped(all_funds, mapping_after_scrape)-> dict:
    """
    Function that will add a df for the looped holdings for each fund.
    This makes comparing funds that has overlapping holdings possible.
    """
    for fund_isin in all_funds:
        fund_name = all_funds[fund_isin]['overview_dict']['fond_namn'] # Fetch fund name
        input_dict={0:{fund_name:(int(0.5+0.5))}} # Prepare the input dict and set value=1 in order to keep the result as share of the fund holding in %

        # input the fund name to retur
        fund_holdings_looped = calculate_portfolio(input_dict, all_funds, mapping_after_scrape)
        all_funds[fund_isin]['funds_holdings_looped'] = fund_holdings_looped
    return all_funds

#%%
def load_new_data():
    """
    Function that triggers the data import flow from all sources.
    Just make sure the latest data from FI is downloaded in a file named xml in the repo.
    Will also pickle the necessary files.
    """
    #%%
    all_funds, mapping = main()
    #%%
    andel_old, scrape_mapping = scrape(all_funds)
    mapping_after_scrape = pd.concat([mapping, scrape_mapping], axis=0)
    mapping_after_scrape=mapping_after_scrape.drop_duplicates(subset=["instrument_isin"],keep="last")
    #%%
    all_funds = calc_fund_holdings_looped(all_funds, mapping_after_scrape)
    #%%
    all_funds = get_isin(all_funds)
    #%%
    save_to_pickle(all_funds, "all_funds")
    save_to_pickle(mapping_after_scrape, "mapping_after_scrape")

#%%
def save_to_pickle(obj, name):
    with open(f"./{name}.pkl", "wb") as f:
        pickle.dump(obj, f)

#%%
load_new_data()
