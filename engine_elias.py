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
    mapping_after_scrape=mapping_after_scrape.drop_duplicates(subset=["instrument_isin"],keep="last") # MOVED THIS LINE TO data_import_quarterly. Remove here when we import new data.
    max_loops=100

    for level in range(max_loops):
        input=input_dict[level]
        holdings_per_level=pd.DataFrame({'instrument_isin':[""], 'instrument_namn':[""], 'landkod_emittent':[""],
       'andel_av_fond':[""], 'marknadsvarde_instrument':[""], 'bransch':[""], 'nivå':[""]})
        for holding in input:
            if level==0: # Only performed on the input holdings ie. level=0
                # Fetches a series of the top_key-isins where the holdings name is equal to a cell in column instrument_namn
                isin=mapping_after_scrape.loc[mapping_after_scrape["instrument_namn"] == holding]["top_key"]
            else: # When level != 0
                  # Fetches a series of the top_key-isins where the holdings name is equal to a cell in column instrument_isin.
                isin=mapping_after_scrape[mapping_after_scrape["instrument_isin"] == holding]["top_key"]
            # if pd.isna(isin.iloc[0]):
                # isin=mapping_after_scrape.loc[mapping_after_scrape["instrument_namn"]==holding]["instrument_isin"]
  
            if isin.empty or pd.isna(isin.iloc[0]): # Check if isin is empty or the series isna.
                if isin.empty: # if empty
                    isin=holding # set isin as the name of the holding.
                elif pd.isna(isin.iloc[0]): # if the series first value is nan
                    # set the isin as the instruments isin as it doesnt have a top_key
                    isin=mapping_after_scrape.loc[mapping_after_scrape["instrument_namn"]==holding]["instrument_isin"] #This fetches a series of the instument_isin where instrument_namn == holding name
                    isin=isin.values[0] # fetch the first value in the series. Note, the series only has one value as duplicates should have been dropped in import.
                # Create a temporary df with a row for the holding that didnt have either a top_key nor an instrument_isin
                temp_df=pd.DataFrame({"instrument_isin":[isin],"instrument_namn":[holding],"landkod_emittent":np.nan,"andel_av_fond":input_dict[level][holding],"markandsvarde_instrument":input_dict[level][holding],"bransch":np.nan,"nivå":0})
                my_portfolio=pd.concat([my_portfolio, temp_df],axis=0) # Adds the new row to my_portfolio. Will lack attributes such as land code etc.
                if len(input_dict[0])==1: # Check if the dict has exactly one key, MEANING that if we couldn´t find an isin and this is the only holding: 
                    return my_portfolio
                continue
            else: # If the isin is not empty nor na.
                isin=isin.values[0] # Isin retrieved as a string from the isin-series
                # else: 
                #     temp_df=pd.DataFrame({"instument_isin":[holding],"instrument_namn":[holding],"landkod_emittent":"-","andel_av_fond":input_dict[i][holding],"markandsvarde_instrument":input_dict[i][holding],"bransch":"-","nivå":0})
                #     my_portfolio=pd.concat([my_portfolio, temp_df],axis=0)
                #     continue

            # print(isin)
            holdings_per_fund=all_funds[isin]["funds_holdings"].copy() # Using the isin as a key to fetches a copy of the funds holdings, a df.
            holdings_per_fund["nivå"]=level+1 # creates a new column in the df named nivå and adds 1 to the level at which the instrument was found in the input.
            holdings_per_fund["andel_av_fond"]*=input_dict[level][holding] # multiplies the andel_av_fond for each instrument by the value that i invested in the fund(holding) on top level.
            holdings_per_level=pd.concat([holdings_per_level, holdings_per_fund],axis=0).reset_index(drop=True) # populate the holdings_per_level df with all instruments from all funds. 
        # print(mapping_after_scrape.columns)
        holdings_per_level=pd.merge(left=holdings_per_level,right=mapping_after_scrape[["instrument_isin","top_key"]],how="left",on="instrument_isin") # Adding the top_key-column to holdings_per_level.
        all_my_holdings=holdings_per_level.loc[holdings_per_level["top_key"].isna()] # MAYBE WE SHOULD KEEP ALL top_keys to be able to track all funds that has overlapping holdings.
        
        my_portfolio=pd.concat([my_portfolio,all_my_holdings],axis=0).reset_index(drop=True) # Populate my_portfolio wit the holdings so far.
        next_level=holdings_per_level.loc[holdings_per_level["top_key"].notna()] # prepare the next level for the next loop by finding all funds on this level, meaning where there is a top_key.
        next_level=next_level.set_index('instrument_isin')['andel_av_fond'].to_dict() # Preparing the next level in the input_dict creating a dictionary that has the instrument_isin's as keys (holding in the loop) and the andel_av_fond which is now the actuall value in kronor, as the value.
        input_dict[level+1]=next_level # add the row for the next level of holdings to the input_dict.
        if not next_level: # If no next level then break.
            break
    my_portfolio=my_portfolio.loc[my_portfolio["instrument_namn"]!=""] # Filter my portfolio on rows that doesnt have an instrument_namn
    my_portfolio=my_portfolio.loc[my_portfolio["andel_av_fond"]!=""] # Filter my portfolio on rows that doesnt have an andel_av_fond
    return my_portfolio
    # return portfolio.groupby(["instrument_isin","instrument_namn","landkod_emittent","bransch"])["andel_av_fond"].sum()
