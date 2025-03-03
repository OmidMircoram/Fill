#%%
import pandas as pd
import xml.etree.ElementTree as ET
import os
import re
from rapidfuzz import process
import numpy as np

def normalize_name(name):
    # Remove any parentheses and content within
    return re.sub(r'\s*\(.*?\)\s*', ' ', name).strip()

def match_name(name, possible_names_list):
    matches = process.extract(name, possible_names_list, limit=1)
    if matches:
        match_tuple = matches[0]
        best_match = match_tuple[0]  # Matched string
        score = match_tuple[1]       # Similarity score
        # best_match, score, _ = matches[0] # Unpack the first two elements, ignore the rest
        if score > 90:  # Adjust the threshold as needed
            return best_match
    return None

def find_best_name_match(name, possible_names_list):
    normalized_input = normalize_name(name)
    
    # First attempt to find an exact match with normalized names
    if normalized_input in possible_names_list:
        return normalized_input
    
    # If no exact match, fall back to fuzzy matching
    best_match = match_name(name, possible_names_list)
    if best_match:
        return best_match
    
    # If no match at all, return None or handle accordingly
    return None

# Specify the folder containing the XML files
def read_funds_data(root_folder_path = "data"):  # Replace with the path to your folder containing XML files
    global test
    root_folder_path = "data"
    # Define the namespace
    namespace = {'ns': 'http://schemas.fi.se/publika/vardepappersfonder/20200331'}

    # List to hold DataFrames for each XML file
    dataframes = {}                 # Primary ISIN as keys and fund holdings df as attributes   
    funds_andelsklasser = {}        # Primary ISIN as keys and andelsklasser and fast avgift as attributes
    funds_data = {}     
    fund_name_primary_isin = {}     # Dictionary with und_name as keys and primary ISIN for mapping          
    andelsklass_to_fond_isin = {}   # create a mapping from ISIN codes to fund names for later reference
    # Initialize mappings
    name_to_isin = {}
    isin_to_name = {}


    # Walk through all subdirectories and files in the root folder
    test=pd.DataFrame()
    for dirpath, dirnames, filenames in os.walk(root_folder_path):
        for filename in filenames:
            if filename.endswith('.xml'):  # Process only XML files
                file_path = os.path.join(dirpath, filename)

                # Parse the XML file
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Extract the fund name
                fond_namn = root.find('.//ns:Fondinformation/ns:Fond_namn', namespace).text
                
                # fond_namn_element = root.find('.//ns:Fondinformation/ns:Fond_namn', namespace)
                # fond_namn = fond_namn_element.text if fond_namn_element is not None else "Unknown Fund"
                # normalized_fond_namn = normalize_name(fond_namn)

                # Extract the fund ISIN
                fond_isin_kod_element = root.find('.//ns:Fondinformation/ns:Fond_ISIN-kod', namespace)
                fond_isin_kod = fond_isin_kod_element.text if fond_isin_kod_element is not None else "Unknown"
                # Check the fund status
                fond_status_element = root.find('.//ns:Fondinformation/ns:Fond_status', namespace)
                if fond_status_element is not None and fond_status_element.text == "Ej aktiv fond":
                    print(f"Skipping {fond_namn}: Fund is inactive (Ej aktiv fond).")
                    continue  # Skip this file and move on to the next one

                # Extract relevant values for 'Likvida_medel', 'Övriga_tillgångar_och_skulder', and 'Fondförmögenhet'
                likvida_medel_element = root.find('.//ns:Likvida_medel', namespace)
                likvida_medel = float(likvida_medel_element.text) if likvida_medel_element is not None else 0
                

                ovriga_tillgangar_element = root.find('.//ns:Övriga_tillgångar_och_skulder', namespace)
                ovriga_tillgangar = float(ovriga_tillgangar_element.text) if ovriga_tillgangar_element is not None else 0

                fondformogenhet_element = root.find('.//ns:Fondförmögenhet', namespace)
                fondformogenhet = float(fondformogenhet_element.text) if fondformogenhet_element is not None else 1  # avoid division by zero

                normalized_fond_namn = normalize_name(fond_namn)
                fund_name_primary_isin[normalized_fond_namn] = fond_isin_kod

                # Populate isin_to_name with fund_name_primary_isin mappings
                for fund_name, primary_isin in fund_name_primary_isin.items():
                    # Normalize the fund name (if necessary)
                    normalized_fund_name = normalize_name(fund_name)
                    
                    # Add the mapping of ISIN to fund name
                    isin_to_name[primary_isin] = normalized_fund_name
                    
                # fund_name_primary_isin.append({ 
                #         'fond_namn': fond_namn,
                #         'Primary_ISIN': fond_isin_kod
                #         })


                # Extract relevant data for each FinansielltInstrument
                data = []
                for instrument in root.findall('.//ns:FinansielltInstrument', namespace):
                    instrument_isin_element = instrument.find('ns:ISIN-kod_instrument', namespace)
                    instrument_isin = instrument_isin_element.text if instrument_isin_element is not None else "Unknown"
                    
                    instrument_namn_element = instrument.find('ns:Instrumentnamn', namespace)
                    instrument_namn = instrument_namn_element.text if instrument_namn_element is not None else "Unknown"
                    normalized_instrument_namn = normalize_name(instrument_namn)

                    landkod_emittent_element = instrument.find('ns:Landkod_Emittent', namespace)
                    landkod_emittent = landkod_emittent_element.text if landkod_emittent_element is not None else "Unknown"

                    andel_av_fond_element = instrument.find('ns:Andel_av_fondförmögenhet_instrument', namespace)
                    andel_av_fond = andel_av_fond_element.text if andel_av_fond_element is not None else "0"

                    marknadsvarde_instrument_element = instrument.find('ns:Marknadsvärde_instrument', namespace)
                    marknadsvarde_instrument = marknadsvarde_instrument_element.text if marknadsvarde_instrument_element is not None else "0"
                    

                    # Check if 'Bransch_namn_instrument' exists, otherwise assign a default value
                    bransch_element = instrument.find('ns:Bransch/ns:Bransch_namn_instrument', namespace)
                    bransch_namn = bransch_element.text if (bransch_element is not None and bransch_element.text is not None) else 'Unknown'
                    # name_to_isin[instrument_namn] = instrument_isin
                    # isin_to_name[instrument_isin] = instrument_namn
                    
                    name_to_isin[normalized_instrument_namn] = instrument_isin
                    isin_to_name[instrument_isin] = normalized_instrument_namn
                    

                    # Convert 'Andel_av_fondförmögenhet_instrument' and 'Marknadsvärde_instrument' to float
                    try:
                        andel_av_fond = float(andel_av_fond)
                    except ValueError:
                        andel_av_fond = 0.0  # Handle cases where conversion might fail
                    
                    try:
                        marknadsvarde_instrument = float(marknadsvarde_instrument)
                    except ValueError:
                        marknadsvarde_instrument = 0.0  # Handle cases where conversion might fail

                    data.append({
                        'Instrument_ISIN': instrument_isin,
                        'Instrumentnamn': instrument_namn,
                        'Landkod_Emittent': landkod_emittent,
                        'Andel_av_fondförmögenhet_instrument': andel_av_fond,
                        'Marknadsvärde_instrument': marknadsvarde_instrument,
                        'Bransch_namn_instrument': bransch_namn
                    })
                if data: 
                    global df1
                    # Create the DataFrame for the current XML file
                    df = pd.DataFrame(data)
                    
                    test=pd.concat([test,df.copy()],axis=0)                    
                    # Debugging step: print the DataFrame's columns and data
                    # print(f"DataFrame for {fond_namn}:")
                    # print(df.head())  # Display first few rows to check the structure

                    # Group by 'Instrumentnamn' and sum 'Andel_av_fondförmögenhet_instrument' and 'Marknadsvärde_instrument'
                    df = df.groupby(['Instrument_ISIN','Instrumentnamn', 'Landkod_Emittent', 'Bransch_namn_instrument'], as_index=False).agg({
                        'Andel_av_fondförmögenhet_instrument': 'sum',
                        'Marknadsvärde_instrument': 'sum'
                    })
                    new_row1 = pd.DataFrame({
                        'Instrument_ISIN': "LM",
                        'Instrumentnamn': ['Likvida_medel'],
                        'Landkod_Emittent': ['XX'],
                        'Andel_av_fondförmögenhet_instrument': [likvida_medel / fondformogenhet * 100],
                        'Marknadsvärde_instrument': [likvida_medel],
                        'Bransch_namn_instrument': ['XX']
                    })
                    
                        # Add a row for Övriga tillgångar och skulder
                    new_row2 = pd.DataFrame({
                        'Instrument_ISIN': "Other",
                        'Instrumentnamn': ['Övriga_tillgångar_och_skulder'],
                        'Landkod_Emittent': ['XX'],
                        'Andel_av_fondförmögenhet_instrument': [ovriga_tillgangar / fondformogenhet * 100],
                        'Marknadsvärde_instrument': [ovriga_tillgangar],
                        'Bransch_namn_instrument': ['XX']
                    })
                    
                    # Concatenate the new rows to the DataFrame
                    df = pd.concat([df, new_row1, new_row2], ignore_index=True)
                    
                    # Check if the sum of 'Andel_av_fondförmögenhet_instrument' is greater than 0
                    if df['Andel_av_fondförmögenhet_instrument'].sum() > 0.1:
                        total_andel_sum = df['Andel_av_fondförmögenhet_instrument'].sum()
                        # print(f"Total Sum of 'Andel_av_fondförmögenhet_instrument' for {name}: {total_andel_sum:.2f}")
                        
                        # Calculate the sum of the 'Marknadsvärde_instrument' column
                        total_marknadsvarde_sum = df['Marknadsvärde_instrument'].sum()
                        # print(f"Total Sum of 'Marknadsvärde_instrument' for {name}: {total_marknadsvarde_sum:.2f}")
                        
                        # Check if the sum is close to 100
                        if abs(100 - total_andel_sum ) < 1e-3:
                            # print("The total adds up to 100.\n")
                            pass
                        else:
                            # print("The total does not add up to 100.")
                            pass
                            # Calculate missing value for Andel_av_fondförmögenhet_instrument
                            missing_andel = 100 - total_andel_sum
                            
                            # Calculate corresponding value for Marknadsvärde_instrument
                            missing_marknadsvarde = (total_marknadsvarde_sum / total_andel_sum) * missing_andel if total_andel_sum != 0 else 0
                            
                            # Create a new row as a DataFrame
                            new_row3 = pd.DataFrame({
                                'Instrument_ISIN': "Other",
                                'Instrumentnamn': ['Onoterat'],
                                'Landkod_Emittent': ['XX'],
                                'Andel_av_fondförmögenhet_instrument': [missing_andel],
                                'Marknadsvärde_instrument': [missing_marknadsvarde],
                                'Bransch_namn_instrument': ['XX']
                            })
                            
                            # Concatenate the new row to the DataFrame
                            df = pd.concat([df, new_row3], ignore_index=True)    
                        # Add the DataFrame to the dictionary using the fund_isin_kod as the key
                        dataframes[fond_isin_kod] = df
                    else:
                        print(f"Skipping {fond_namn}: Total 'Andel_av_fondförmögenhet_instrument' is 0.")
                else:
                    print(f"No data found in {filename}. Skipping.")


                # Extract Avgifter and Andelsklasser
                avgifter_data = []
                fund_risk_data = []
                # Track the maximum Förvaltningsavgift_fast for the current fund
                max_forvaltningsavgift = 0
                for avgift in root.findall(".//ns:Förvaltningsavgift/ns:MedAndelsklasser/ns:Förvaltningsavgift", namespace):
                    andelsklass_namn = avgift.find("ns:Andelsklass_namn", namespace).text or "Unknown Class"
                    # normalized_andelsklass_namn = normalize_name(andelsklass_namn)
                    # primary_isin = fund_name_primary_isin[fond_namn]

                    forvaltningsavgift_typ = float(avgift.find("ns:Förvaltningsavgift_Typ/ns:Förvaltningsavgift_fast", namespace).text or 0)
                    max_forvaltningsavgift = max(max_forvaltningsavgift, forvaltningsavgift_typ)  # Update the max fee
                    
                    avgifter_data.append({
                        "Fond_ISIN-kod": fond_isin_kod,
                        "Andelsklass_namn": andelsklass_namn,
                        "Förvaltningsavgift_fast": forvaltningsavgift_typ
                    })
    
                # Add an Andelsklass as a default option if no andelsklass is known.
                if avgifter_data:
                    avgifter_data.append({
                        "Fond_ISIN-kod": fond_isin_kod,
                        "Andelsklass_namn": fond_namn,  # Add the fund name as Andelsklass_namn
                        "Förvaltningsavgift_fast": max_forvaltningsavgift
                        })
                    funds_andelsklasser[fond_isin_kod] = pd.DataFrame(avgifter_data)
                # Create a DataFrame for avgifter and andelsklasser
                if avgifter_data:  # Only create a DataFrame if there is data
                    avgifter_df = pd.DataFrame(avgifter_data)
                else:
                    avgifter_df = pd.DataFrame(columns=['Fond_ISIN_kod','Andelsklass_namn', 'Förvaltningsavgift_fast'])
                # Store the DataFrame in the dictionary with the fund name as the key
                funds_andelsklasser[fond_isin_kod] = avgifter_df

                for std in root.findall('.//ns:Standardavvikelse_24_månader', namespace):        # Extract Aktiv risk, Standardavvikelse, Jämförelseindex
                    fond_isin_kod_element = root.find('.//ns:Fondinformation/ns:Fond_ISIN-kod', namespace)
                    fond_isin_kod = fond_isin_kod_element.text if fond_isin_kod_element is not None else "Unknown"

                    aktiv_risk_element = root.find('.//ns:Aktiv_risk', namespace)
                    aktiv_risk = float(aktiv_risk_element.text) if aktiv_risk_element is not None else None

                    standardavvikelse_element = root.find('.//ns:Standardavvikelse_24_månader', namespace)
                    standardavvikelse = float(standardavvikelse_element.text) if standardavvikelse_element is not None else None

                    jamforelseindex_element = root.find('.//ns:Jämförelseindex', namespace)
                    jamforelseindex = jamforelseindex_element.text if jamforelseindex_element is not None else "Unknown Index"

                    fund_risk_data.append({
                        'Fond_ISIN-kod': fond_isin_kod,
                        'Fondformogenhet': fondformogenhet,
                        'Standardavvikelse_24': standardavvikelse,
                        'Aktiv_risk': aktiv_risk,
                        'jmf_index': jamforelseindex
                    })

                # Create a DataFrame for fund risk data
                if fund_risk_data:  # Only create a DataFrame if there is data
                    fund_risk_data_df = pd.DataFrame(fund_risk_data)
                else:
                    fund_risk_data_df = pd.DataFrame(columns=['Fond_ISIN_kod','fondformogenhet', 'Standardavvikelse_24', 'Aktiv_risk', 'jmf_index'])
                # Store the DataFrame in the dictionary with the fund name as the key
                funds_data[fond_isin_kod] = fund_risk_data_df

    return dataframes, funds_andelsklasser, funds_data, andelsklass_to_fond_isin, name_to_isin, isin_to_name, fund_name_primary_isin

dataframes, funds_andelsklasser, funds_data, andelsklass_to_fond_isin, name_to_isin, isin_to_name, fund_name_primary_isin = read_funds_data()