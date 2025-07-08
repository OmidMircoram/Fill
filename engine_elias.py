#%% 
import pandas as pd

# from read_xml_elias import main
# alla_fonder,mappning=main()
#%%
# holdings={0:{'Handelsbanken Aktiv 100':1000,

# # "SEB Active 20" :100
# },        
# }

def portfolio(holdings, alla_fonder, mappning: pd.DataFrame):
    alla_aktier=pd.DataFrame()
    mappning=mappning.drop_duplicates(subset=["instrument_isin"],keep="last")
    nivåer=100
    for i in range (nivåer):
        fonder=holdings[i]
        innehav_per_nivå=pd.DataFrame()
        for fond in fonder:
            if i==0:
                isin=mappning.loc[mappning["instrument_namn"]==fond]["top_key"]
                if not isin.empty:  
                    isin=isin.values[0]
                else: 
                    temp_df=pd.DataFrame({"instument_isin":[fond],"instrument_namn":[fond],"landkod_emittent":"-","andel_av_fond":holdings[i][fond],"markandsvarde_instrument":holdings[i][fond],"bransch":"-","nivå":0})
                    alla_aktier=pd.concat([alla_aktier, pd.DataFrame({})])
                    continue
            else:
                isin=mappning[mappning["instrument_isin"] == fond]["top_key"].values[0]
            innehav=alla_fonder[isin]["innehav"]
            innehav["nivå"]=i+1
            innehav["andel_av_fond"]*=holdings[i][fond]
            innehav_per_nivå=pd.concat([innehav_per_nivå,innehav],axis=0).reset_index(drop=True)
        #HÄR ÄR DET FEL
        innehav_per_nivå=pd.merge(left=innehav_per_nivå,right=mappning[["instrument_isin","top_key"]],on="instrument_isin")
        aktier=innehav_per_nivå.loc[innehav_per_nivå["top_key"].isna()]
        nästa_nivå=innehav_per_nivå.loc[innehav_per_nivå["top_key"].notna()]
        # aktier=innehav_per_nivå.loc[((~innehav_per_nivå["instrument_isin"].isin(mappning["instrument_isin"].unique())) & (mappning["top_key"].isna()))]
        # aktier=innehav_per_nivå.loc[~innehav_per_nivå["instrument_isin"].isin(mappning[mappning["instrument_isin"] == fond]["top_key"].unique())]
        print(aktier)
        alla_aktier=pd.concat([alla_aktier,aktier],axis=0).reset_index(drop=True)

        # nästa_nivå=innehav_per_nivå.loc[((innehav_per_nivå["instrument_isin"].isin(mappning["instrument_isin"].unique())) & (mappning[mappning["instrument_isin"]==innehav_per_nivå["instrument_isin"]]["top_key"].notna()))]
        # [["top_key","andel_av_fond"]]
        nästa_nivå=nästa_nivå.set_index('instrument_isin')['andel_av_fond'].to_dict()
        holdings[i+1]=nästa_nivå
        # print(holdings)
        if not nästa_nivå: 
            break
    return alla_aktier
