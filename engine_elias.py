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
    mappning=mappning.drop_duplicates(subset=["instrument_namn","instrument_isin"],keep="last")
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
        aktier=innehav_per_nivå.loc[~innehav_per_nivå["instrument_isin"].isin(alla_fonder.keys())]
        alla_aktier=pd.concat([alla_aktier,aktier],axis=0).reset_index(drop=True)
        nivå2=innehav_per_nivå.loc[innehav_per_nivå["instrument_isin"].isin(alla_fonder.keys())][["instrument_isin","andel_av_fond"]]
        nivå2=nivå2.set_index('instrument_isin')['andel_av_fond'].to_dict()
        holdings[i+1]=nivå2
        if not nivå2: 
            break
    return alla_aktier
