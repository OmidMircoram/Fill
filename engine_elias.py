#%% 
import pandas as pd 
from read_xml_elias import main
alla_fonder,mappning=main()
#%%
nivå_dict={0:{'Handelsbanken Aktiv 100':1000,
            #   'Handelsbanken Aktiv 70':1000,
# "SEB Active 20" :100
},        
}


alla_aktier=pd.DataFrame()
mappning=mappning.drop_duplicates()
nivåer=3
for i in range (nivåer):    
    fonder=nivå_dict[i]
    innehav_per_nivå=pd.DataFrame()
    for fond in fonder:
        if i==0:
            isin=mappning.loc[mappning["fond_namn"]==fond]["isin"]
            if not isin.empty:  
                isin=isin.values[0]
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