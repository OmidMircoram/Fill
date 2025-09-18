#%% 
import pandas as pd
import numpy as np

def find_first_isin(input_dict,mapping_after_scrape):
    for holding in list(input_dict[0]): # Loops only over the first row in the dict. 0 is the key for returning the lisn
        # Returns a series/variable holding the top_key (ISIN) where instrument_namn is equal to the holdings name.
        isin=mapping_after_scrape.loc[mapping_after_scrape["instrument_namn"]==holding]["top_key"] 

        if not isin.empty:  # if isin holds an actual value:
            isin=isin.values[0] # extracts the actual isin as a string
            input_dict[0][isin] = input_dict[0].pop(holding) # deletes the holding and replaces it with the value of that holding. 
        else:
            continue
        return input_dict

def calculate_portfolio(input_dict, all_funds, mapping_after_scrape: pd.DataFrame):
    my_portfolio=pd.DataFrame()
    # Drop duplicates based on instrument_isin in the mapping and keep the last one added as that one must be fetched from the scrapeing
    # Hence, we make sure to keep the funds 
    mapping_after_scrape=mapping_after_scrape.drop_duplicates(subset=["instrument_isin"],keep="last") # MOVE THIS LINE TO data_import_quarterly?
    max_loops=100

    for i in range(max_loops):
        input=input_dict[i]
        innehav_per_nivå=pd.DataFrame({'instrument_isin':[""], 'instrument_namn':[""], 'landkod_emittent':[""],
       'andel_av_fond':[""], 'marknadsvarde_instrument':[""], 'bransch':[""], 'nivå':[""]})
        for holding in input:
            if i==0:
                isin=mapping_after_scrape.loc[mapping_after_scrape["instrument_namn"] == holding]["top_key"]
            else:
                isin=mapping_after_scrape[mapping_after_scrape["instrument_isin"] == holding]["top_key"]
            # if pd.isna(isin.iloc[0]):
                # isin=mapping_after_scrape.loc[mapping_after_scrape["instrument_namn"]==holding]["instrument_isin"]
  
            if isin.empty or pd.isna(isin.iloc[0]) :
                if isin.empty:
                    isin=holding
                elif pd.isna(isin.iloc[0]): 
                    isin=mapping_after_scrape.loc[mapping_after_scrape["instrument_namn"]==holding]["instrument_isin"]
                    isin=isin.values[0]
                temp_df=pd.DataFrame({"instrument_isin":[isin],"instrument_namn":[holding],"landkod_emittent":np.nan,"andel_av_fond":input_dict[i][holding],"markandsvarde_instrument":input_dict[i][holding],"bransch":np.nan,"nivå":0})
                my_portfolio=pd.concat([my_portfolio, temp_df],axis=0)
                if len(input_dict[0])==1:
                    return my_portfolio
                continue
            else:
                isin=isin.values[0] 
                # else: 
                #     temp_df=pd.DataFrame({"instument_isin":[holding],"instrument_namn":[holding],"landkod_emittent":"-","andel_av_fond":input_dict[i][holding],"markandsvarde_instrument":input_dict[i][holding],"bransch":"-","nivå":0})
                #     my_portfolio=pd.concat([my_portfolio, temp_df],axis=0)
                #     continue

            # print(isin)
            innehav_per_fond=all_funds[isin]["innehav"].copy()
            innehav_per_fond["nivå"]=i+1
            innehav_per_fond["andel_av_fond"]*=input_dict[i][holding]
            innehav_per_nivå=pd.concat([innehav_per_nivå, innehav_per_fond],axis=0).reset_index(drop=True)
        # print(mapping_after_scrape.columns)
        innehav_per_nivå=pd.merge(left=innehav_per_nivå,right=mapping_after_scrape[["instrument_isin","top_key"]],how="left",on="instrument_isin")
        aktier=innehav_per_nivå.loc[innehav_per_nivå["top_key"].isna()]
        
        my_portfolio=pd.concat([my_portfolio,aktier],axis=0).reset_index(drop=True)
        nästa_nivå=innehav_per_nivå.loc[innehav_per_nivå["top_key"].notna()]
        nästa_nivå=nästa_nivå.set_index('instrument_isin')['andel_av_fond'].to_dict()
        input_dict[i+1]=nästa_nivå
        if not nästa_nivå: 
            break
    my_portfolio=my_portfolio.loc[my_portfolio["instrument_namn"]!=""]
    my_portfolio=my_portfolio.loc[my_portfolio["andel_av_fond"]!=""]
    return my_portfolio
    # return portfolio.groupby(["instrument_isin","instrument_namn","landkod_emittent","bransch"])["andel_av_fond"].sum()
