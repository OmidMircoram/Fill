#%% 
import pandas as pd
import numpy as np

def find_first_isin(holdings,mappning):
    for fond in list(holdings[0]): 
        isin=mappning.loc[mappning["instrument_namn"]==fond]["top_key"]

        if not isin.empty:  
            isin=isin.values[0]
            holdings[0][isin] = holdings[0].pop(fond)
        else:
            continue
        return holdings

def calculate_portfolio(holdings, alla_fonder, mappning: pd.DataFrame):
    portfolio=pd.DataFrame()
    mappning=mappning.drop_duplicates(subset=["instrument_isin"],keep="last")
    nivåer=100

    for i in range (nivåer):
        fonder=holdings[i]
        innehav_per_nivå=pd.DataFrame({'instrument_isin':[""], 'instrument_namn':[""], 'landkod_emittent':[""],
       'andel_av_fond':[""], 'marknadsvarde_instrument':[""], 'bransch':[""], 'nivå':[""]})
        for fond in fonder:
            if i==0:
                isin=mappning.loc[mappning["instrument_namn"] == fond]["top_key"]
            else:
                isin=mappning[mappning["instrument_isin"] == fond]["top_key"]
            # if pd.isna(isin.iloc[0]):
                # isin=mappning.loc[mappning["instrument_namn"]==fond]["instrument_isin"]
  
            if isin.empty or pd.isna(isin.iloc[0]) :
                if isin.empty:
                    isin=fond
                elif pd.isna(isin.iloc[0]): 
                    isin=mappning.loc[mappning["instrument_namn"]==fond]["instrument_isin"]
                    isin=isin.values[0]
                temp_df=pd.DataFrame({"instrument_isin":[isin],"instrument_namn":[fond],"landkod_emittent":np.nan,"andel_av_fond":holdings[i][fond],"markandsvarde_instrument":holdings[i][fond],"bransch":np.nan,"nivå":0})
                portfolio=pd.concat([portfolio, temp_df],axis=0)
                if len(holdings[0])==1:
                    return portfolio
                continue
            else:
                isin=isin.values[0] 
                # else: 
                #     temp_df=pd.DataFrame({"instument_isin":[fond],"instrument_namn":[fond],"landkod_emittent":"-","andel_av_fond":holdings[i][fond],"markandsvarde_instrument":holdings[i][fond],"bransch":"-","nivå":0})
                #     portfolio=pd.concat([portfolio, temp_df],axis=0)
                #     continue

            # print(isin)
            innehav_per_fond=alla_fonder[isin]["innehav"].copy()
            innehav_per_fond["nivå"]=i+1
            innehav_per_fond["andel_av_fond"]*=holdings[i][fond]
            innehav_per_nivå=pd.concat([innehav_per_nivå,innehav_per_fond],axis=0).reset_index(drop=True)
        # print(mappning.columns)
        innehav_per_nivå=pd.merge(left=innehav_per_nivå,right=mappning[["instrument_isin","top_key"]],how="left",on="instrument_isin")
        aktier=innehav_per_nivå.loc[innehav_per_nivå["top_key"].isna()]
        
        portfolio=pd.concat([portfolio,aktier],axis=0).reset_index(drop=True)
        nästa_nivå=innehav_per_nivå.loc[innehav_per_nivå["top_key"].notna()]
        nästa_nivå=nästa_nivå.set_index('instrument_isin')['andel_av_fond'].to_dict()
        holdings[i+1]=nästa_nivå
        if not nästa_nivå: 
            break
    portfolio=portfolio.loc[portfolio["instrument_namn"]!=""]
    portfolio=portfolio.loc[portfolio["andel_av_fond"]!=""]
    return portfolio
    # return portfolio.groupby(["instrument_isin","instrument_namn","landkod_emittent","bransch"])["andel_av_fond"].sum()
