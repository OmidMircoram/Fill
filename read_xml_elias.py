#%%
import os
import re
import time
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd


def normalize_name(name):
    # Remove any parentheses and content within
    return re.sub(r'\s*\(.*?\)\s*', ' ', name).strip()

def check_none(element,exception):
    fixed_element = element.text if element is not None and element.text is not None else exception
    return fixed_element

def check_aktiv(element):
     if element is not None and element.text == "Ej aktiv fond":
          return False
     else:
          return True

def find_element(level,elements):
    namespace= {'ns': 'http://schemas.fi.se/publika/vardepappersfonder/20200331'}
    string="./"
    for sub_element in elements:
        string=string + "/ns:"+sub_element  
    return level.find(string,namespace)

def find_all_elements(level,elements):
    namespace= {'ns': 'http://schemas.fi.se/publika/vardepappersfonder/20200331'}
    string="./"
    for sub_element in elements:
        string=string + "/ns:"+sub_element  
    return level.findall(string,namespace)


def get_fund_overview(root):
    fond_namn = find_element(root,['Fondinformation','Fond_namn']).text
    fond_isin = find_element(root,["Fondinformation","Fond_ISIN-kod"]) 
    fond_isin = check_none(fond_isin, "Unknown")
    likvida_medel=find_element(root,['Likvida_medel'])   
    likvida_medel= float(check_none(likvida_medel,0))
    ovriga_tillgangar = find_element(root,['Övriga_tillgångar_och_skulder'])
    ovriga_tillgangar = float(check_none(ovriga_tillgangar,0))
    fondformogenhet = find_element(root,['Fondförmögenhet'])            
    fondformogenhet=float(check_none(fondformogenhet,0))
    aktiv_risk= find_element(root,['Aktiv_risk'])
    aktiv_risk=check_none(aktiv_risk,None)
    standardavvikelse= find_element(root,['Standardavvikelse_24_månader'])
    standardavvikelse=check_none(standardavvikelse,None)
    jamforelseindex= find_element(root,['Jämförelseindex', "Jämförelseindex"])
    jamforelseindex=check_none(jamforelseindex,"Unknown Index")                                             

    overview_dict={"fond_namn":fond_namn,
              "fond_isin":fond_isin,
              "likvida_medel":likvida_medel,
              "ovriga_tillgangar":ovriga_tillgangar,
              "fondformogenhet":fondformogenhet,
              "aktiv_risk":aktiv_risk,
              "standardavvikelse":standardavvikelse,
              "jamforelseindex":jamforelseindex
              }


    return overview_dict

def unikt_instrument(instrument):
    instrument_isin = find_element(instrument,['ISIN-kod_instrument'])
    instrument_isin=check_none(instrument_isin,"Unknown")
    instrument_namn = find_element(instrument,['Instrumentnamn'])
    instrument_namn=check_none(instrument_namn,"Unknown")
    landkod_emittent= find_element(instrument,['Landkod_Emittent'])
    landkod_emittent=check_none(landkod_emittent,"Unknown")
    andel_av_fond= find_element(instrument,['Andel_av_fondförmögenhet_instrument'])
    andel_av_fond=float(check_none(andel_av_fond,0))
    marknadsvarde_instrument= find_element(instrument,['Marknadsvärde_instrument'])
    marknadsvarde_instrument=float(check_none(marknadsvarde_instrument,0))
    bransch = find_element(instrument,['Bransch','Bransch_namn_instrument'])
    bransch=check_none(bransch,"Unknown")

    instrument_dict={
        "instrument_isin":instrument_isin,
        "instrument_namn":instrument_namn,
        "landkod_emittent":landkod_emittent,
        "andel_av_fond":andel_av_fond/100,
        "marknadsvarde_instrument":marknadsvarde_instrument,
        "bransch":bransch
    }

    return instrument_dict


def get_all_instruments(root):
    alla_instrument=find_all_elements(root,['FinansielltInstrument'])
    df_instrument=pd.DataFrame()
    for instrument in alla_instrument:
        temp_df=pd.DataFrame([unikt_instrument(instrument)])
        df_instrument=pd.concat([df_instrument,temp_df],axis=0)
    return df_instrument

def get_fast_avgift(root):
    #Lägg till så alla andelsklasser sparas, inte bara den senaste.
    alla_andelsklasser=find_all_elements(root,["Förvaltningsavgift","MedAndelsklasser","Förvaltningsavgift"])
    alla_utan=find_all_elements(root,["Förvaltningsavgift","UtanAndelsklasser"])
    if alla_andelsklasser: 
        avgift_dict={}
        for andelsklass in alla_andelsklasser:
            andelsklass_namn = find_element(andelsklass,["Andelsklass_namn"]).text or "Unknown Class"
            avgift_fast=float(find_element(andelsklass,["Förvaltningsavgift_Typ","Förvaltningsavgift_fast"]).text or 0)
            avgift=max(0,avgift_fast)
            avgift_dict[andelsklass_namn]=avgift
    elif alla_utan: 
        avgift=float(find_element(alla_utan[0],["Förvaltningsavgift_fast"]).text or 0)
        avgift_dict={"utan_andelsklass" : avgift}
    return avgift_dict

def main():
    """Returns -> tuple[dict, DataFrame]"""
    root_folder_path = "xml"
    
    tid=0
    all_funds={}
    mapping_df=pd.DataFrame({"instrument_namn":[],"instrument_isin":[], "top_key":[]})
    all_holdings=pd.DataFrame({"instrument_namn":[],"instrument_isin":[], "top_key":[]})

    for dirpath, dirnames, filenames in os.walk(root_folder_path):
        for filename in filenames:
            fund_dict={}
            if filename.endswith('.xml'):  # Process only XML files
                file_path = os.path.join(dirpath, filename)
                tree = ET.parse(file_path)
                root = tree.getroot()
                overview_dict=get_fund_overview(root)
                fond_status_element =find_element(root,['Fondinformation','Fond_status'])    
                aktiv=check_aktiv(fond_status_element)
                if not aktiv:
                    print(f"Skipping {overview_dict['fond_namn']}: Fund is inactive (Ej aktiv fond).")
                    continue
                
                fees_dict=get_fast_avgift(root)    
                df_innehav=get_all_instruments(root) 
                if len(list(df_innehav.columns)) == 0:
                    print(f"Skipping {overview_dict['fond_namn']}: Fund has no holdings.")
                    continue
                # df_innehav["top_key"] = df_innehav["instrument_isin"].copy()

                all_holdings=pd.concat([all_holdings,df_innehav[["instrument_namn","instrument_isin", "landkod_emittent", "bransch"]]],axis=0)
                fund_dict["overview_dict"]=overview_dict
                fund_dict["fees_dict"]=fees_dict
                fund_dict["funds_holdings"]=df_innehav
                # add to mappning all funds by setting the instrument_isin/fond_isin to their top_key
                mapping_df=pd.concat([mapping_df,pd.DataFrame({"instrument_namn":[overview_dict["fond_namn"]],"instrument_isin":[overview_dict["fond_isin"]], "top_key":[overview_dict["fond_isin"]]})]).reset_index(drop=True)
                # set the key for the fund_dict to the ISIN code for that fund.
                all_funds[fund_dict["overview_dict"]["fond_isin"]]=fund_dict
    # keep all instruments that is not actually a fund in all_funds.
    all_holdings=all_holdings.loc[~all_holdings["instrument_isin"].isin(list(all_funds.keys()))]
    all_holdings.drop_duplicates(subset="instrument_isin",inplace=True)
    # Add up all instruments and funds to the mapping df
    mapping_df=pd.concat([mapping_df,all_holdings],axis=0).reset_index(drop=True)
    return all_funds, mapping_df.drop_duplicates()
    

def old_main(): 
    root_folder_path = "xml"
    
    tid=0
    all_funds={}
    mapping_df=pd.DataFrame({"instrument_namn":[],"instrument_isin":[]})
    for dirpath, dirnames, filenames in os.walk(root_folder_path):
        for filename in filenames:
            fund_dict={}
            if filename.endswith('.xml'):  # Process only XML files
                file_path = os.path.join(dirpath, filename)
                tree = ET.parse(file_path)
                root = tree.getroot()
                overview_dict=get_fund_overview(root)
                fond_status_element =find_element(root,['Fondinformation','Fond_status'])    
                aktiv=check_aktiv(fond_status_element)
                if not aktiv:
                    print(f"Skipping {overview_dict['fond_namn']}: Fund is inactive (Ej aktiv fond).")
                    continue
                
                fees_dict=get_fast_avgift(root)    
                df_innehav=get_all_instruments(root) 
                fund_dict["overview_dict"]=overview_dict
                fund_dict["fees_dict"]=fees_dict
                fund_dict["innehav"]=df_innehav
                mapping_df=pd.concat([mapping_df,pd.DataFrame({"instrument_namn":[overview_dict["fond_namn"]],"instrument_isin":[overview_dict["fond_isin"]]})]).reset_index(drop=True)
                mapping_df=pd.concat([mapping_df,df_innehav[["instrument_namn","instrument_isin"]]])
                all_funds[fund_dict["overview_dict"]["fond_isin"]]=fund_dict
    return all_funds, mapping_df.drop_duplicates()