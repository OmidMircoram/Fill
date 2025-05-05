#%% 
import pandas as pd 
from read_xml_elias import main
alla_fonder,mappning=main()
#%%
nivå_dict={0:{'Handelsbanken Pension 50':100,

# "SEB Active 20" :100
},        
}


alla_aktier=pd.DataFrame()
mappning=mappning.drop_duplicates()
nivåer=100
for i in range (nivåer):    
    fonder=nivå_dict[i]
    innehav_per_nivå=pd.DataFrame()
    for fond in fonder:
        if i==0:
            isin=mappning.loc[mappning["fond_namn"]==fond]["isin"]
            if not isin.empty:  
                isin=isin.values[0]
            else: 
                temp_df=pd.DataFrame({"instument_isin":[fond],"instrument_namn":[fond],"landkod_emittent":"-","andel_av_fond":nivå_dict[i][fond],"markandsvarde_instrument":nivå_dict[i][fond],"bransch":"-","nivå":0})
                alla_aktier=pd.concat([alla_aktier, pd.DataFrame({})])
                continue
        else:
            isin=fond
        innehav=alla_fonder[isin]["innehav"].copy()
        innehav["nivå"]=i+1
        innehav["andel_av_fond"]*=nivå_dict[i][fond]
        innehav_per_nivå=pd.concat([innehav_per_nivå,innehav],axis=0).reset_index(drop=True)
    aktier=innehav_per_nivå.loc[~innehav_per_nivå["instrument_isin"].isin(alla_fonder.keys())]
    alla_aktier=pd.concat([alla_aktier,aktier],axis=0).reset_index(drop=True)
    nivå2=innehav_per_nivå.loc[innehav_per_nivå["instrument_isin"].isin(alla_fonder.keys())][["instrument_isin","andel_av_fond"]]
    nivå2=nivå2.set_index('instrument_isin')['andel_av_fond'].to_dict()
    nivå_dict[i+1]=nivå2
    if not nivå2: 
        break

nivå_dict
#%%
alla_aktier
#%%
import financedatabase as fd
#%%
etf=fd.ETFs()
funds=fd.Funds()
eq=fd.Equities()
#%%

eq.options("country")
# eq.select(country="Sweden",exclude_exchanges=True)
# eq.select