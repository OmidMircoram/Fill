#%% 
import pandas as pd 
from read_xml_elias import main
alla_fonder,mappning=main()
#%%
nivå_dict={0:{'SEB Active 20':1000},
           1:{},
           2:{},
           3:{},
           4:{},
           5:{}}


alla_aktier=pd.DataFrame()
mappning=mappning.drop_duplicates()
nivåer=4
for i in range (nivåer):
    # print(nivå_dict)
    fonder=nivå_dict[i]
    # print(fonder)
    for fond in fonder:
        if i==0:
            isin=mappning.loc[mappning["fond_namn"]==fond]["isin"]
            if not isin.empty: 
                isin=isin.values[0]
        else:
            isin=fond
        innehav=alla_fonder[isin]["innehav"].copy()
        innehav["andel_av_fond"]*=nivå_dict[i][fond]
        aktier=innehav.loc[~innehav["instrument_isin"].isin(alla_fonder.keys())]
        nivå2=innehav.loc[innehav["instrument_isin"].isin(alla_fonder.keys())][["instrument_isin","andel_av_fond"]]
        nivå2=nivå2.set_index('instrument_isin')['andel_av_fond'].to_dict()
        nivå_dict[i+1]=nivå2
        alla_aktier=pd.concat([alla_aktier,aktier],axis=0)

    # for innehav in  
        # pass
        




nivå_dict
