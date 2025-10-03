#%%
import pickle
import pandas as pd
from engine import calculate_portfolio
# from data_import_quarterly import calc_fund_holdings_looped

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
#%%
# REMOVE THIS CELL WHEN THIS IS DONE QUARTERLY
def calc_fund_holdings_looped(all_funds, mapping_after_scrape)-> dict:
    """
    Function that will add a df for the looped holdings for each fund.
    This makes comparing funds that has overlapping holdings possible.
    """
    for fund_isin in all_funds:
        fund_name = all_funds[fund_isin]['översikt']['fond_namn'] # Fetch fund name
        input_dict={0:{fund_name:1}} # Prepare the input dict and set value=1 in order to keep the result as share of the fund holding in %
        # input the fund name to retur
        fund_holdings_looped = calculate_portfolio(input_dict, all_funds, mapping_after_scrape)
        all_funds[fund_isin]['funds_holdings_looped'] = fund_holdings_looped
    return all_funds

# all_funds = calc_fund_holdings_looped(all_funds, mapping_after_scrape)
# #%%
# input_dict={0:{"Länsförsäkringar Global Index":100, "Handelsbanken Aktiv 100": 200, "Axfood":50}}
# # "Handelsbanken Aktiv 100":1000000, , "Axfood":50000

# my_portfolio = (calculate_portfolio(input_dict, all_funds.copy(), mapping_after_scrape)).reset_index()
# # current_portfolio=current_portfolio.sort_values(by="andel_av_fond",ascending=False)
# my_portfolio


# %%
##################### OVERLAPPING #####################
# my_portfolio.sort_values(by="andel_av_fond")
# my_portfolio["portfolio_weight"] = my_portfolio['andel_av_fond'] / my_portfolio['andel_av_fond'].sum()

def compute_overlap(my_portfolio, fund_w):
    """
    Returnerar:
      overlap: sum(min(w_p, w_f)) över gemensamma ISIN (0..1)
      port_coverage: andel av portf.vikt som täcks av fondens gemensamma innehav (0..1)
      fund_coverage: andel av fondvikt som täcks av portföljens gemensamma innehav (0..1)
      details_df: tabell med gemensamma innehav och deras bidrag
    """
    merged = my_portfolio.merge(fund_w, on="instrument_isin", suffixes=("_p", "_f"))
    if merged.empty:
        return 0.0, 0.0, 0.0, merged.assign(contribution=[])
    merged["contribution"] = merged[["portfolio_weight", "andel_av_fond_f"]].min(axis=1)
    overlap = merged["contribution"].sum()
    port_coverage = merged["portfolio_weight"].sum()            # andel av portföljen som finns i fonden
    fund_coverage = merged["andel_av_fond_f"].sum()            # andel av fonden som finns i portföljen
    # Sortera bidrag störst först
    details = merged[["instrument_isin", "instrument_namn_p", "instrument_namn_f", "portfolio_weight", "andel_av_fond_f", "contribution"]].copy()
    # Om namn skiljer sig mellan källor, välj ett "bäst tillgängligt" namn
    details["holding_name"] = details["instrument_namn_p"].fillna(details["instrument_namn_f"]).fillna("")
    details = details.drop(columns=["instrument_namn_p", "instrument_namn_f"]).sort_values("contribution", ascending=False)
    return float(overlap), float(port_coverage), float(fund_coverage), details

# %%

def rank_fund_overlaps(my_portfolio, all_funds, top_n=10):
    """
    my_portfolio: DataFrame med kolumner [isin, name, amount]
    all_funds: {fund_isin: {översikt:{}}, {avgifter:{}}, {innehav: Dataframe}, {funds_holdings_looped: Dataframe}}
    """
    results = []
    details_map = {}

    for fund_isin in all_funds:
        fund_w = all_funds[fund_isin]['funds_holdings_looped']
        overlap, port_cov, fund_cov, details = compute_overlap(my_portfolio, fund_w)
        results.append({
            "fund": all_funds[fund_isin]['översikt']['fond_namn'],
            "fund_isin": fund_isin,
            "overlap_score": overlap,          # 0..1, högre = mer lika viktmässigt
            "portfolio_coverage": port_cov,    # hur mycket av portföljen som finns i fonden
            "fund_coverage": fund_cov,         # hur mycket av fonden som finns i portföljen
        })
        details_map[all_funds[fund_isin]['översikt']['fond_namn']] = details

    results_df = pd.DataFrame(results).sort_values("overlap_score", ascending=False).reset_index(drop=True)
    top = results_df.head(top_n).copy()

    return top, results_df, details_map
# top, results_df, details_map = rank_fund_overlaps(my_portfolio, all_funds)
# %%
