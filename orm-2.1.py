#%%
import pandas as pd
import matplotlib.pyplot as plt
import functools
from read_xml_new import normalize_name, find_best_name_match, read_funds_data

# Cache the data loading function
@functools.lru_cache(maxsize=None)
def get_funds_data():
    return read_funds_data(root_folder_path="data")

# Use the cached data loading function
dataframes, funds_andelsklasser, funds_data, andelsklass_to_fond_isin, name_to_isin, isin_to_name, fund_name_primary_isin = get_funds_data()

#%%
# Build a mapping from Andelsklass_namn to Fond_namn
andelsklass_to_fond = {}
for fond_namn, df in funds_andelsklasser.items():
    if isinstance(df, pd.DataFrame):
        for index, row in df.iterrows():
            andelsklass_namn = row['Andelsklass_namn']

            andelsklass_to_fond[andelsklass_namn] = fond_namn

# Collect possible normalized names from fund names and instrument names
possible_names = set(name_to_isin.keys())

# Add normalized names to possible_names
# for name in name_to_isin.keys():
#     possible_names.add(normalize_name(name))

# Add instrument names from each fund's DataFrame
for df in dataframes.values():
    possible_names.update(df['Instrumentnamn'].tolist())

# Add fund ISIN codes (if necessary)
possible_names.update(dataframes.keys())

# Add Andelsklass_namn
possible_names.update(andelsklass_to_fond.keys())

# Convert the set of possible names to a sorted list
possible_names_list = sorted(possible_names)


def create_table_C(table_A, dataframes, fund_name_primary_isin, name_to_isin, isin_to_name, max_depth=10):
    global table_C    
    global cumulative_exposures
    cumulative_exposures = {}
    processed_funds = {}  # Map ISIN to depth
    expansion_cache = {}  # Cache to store expanded results for funds
    expansion_log = []  # Initialize as a list of dictionaries

    def expand_holding_iteratively(name, value, cumulative_exposures, max_depth, mother=None):
        # Use a stack for iterative expansion, now including "mother"
        stack = [(name, value, 1, mother)]  # Each entry is (name, value, depth, mother)
        global isin
        cumulative_fee = 0
        # isin = fund_name_primary_isin['Handelsbanken Aktiv 100']
        # df = funds_andelsklasser[isin]
        # avgift = df.loc[df['Andelsklass_namn'] == name]['Förvaltningsavgift_fast']
        # if avgift.values[0] > 0:
        #     cumulative_fee = value * avgift/100
        #     print(cumulative_fee)
        
        while stack:
            current_name, current_value, depth, mother_name = stack.pop()
            if depth > max_depth:
                if current_name in cumulative_exposures:
                    cumulative_exposures[current_name]['Exposure'] += current_value
                    cumulative_exposures[current_name]['Depth'] = max(cumulative_exposures[current_name]['Depth'], depth)
                else:
                    cumulative_exposures[current_name] = {'Exposure': current_value, 'Depth': depth}
                # continue

            # Normalize the name to remove parentheses and other unwanted text
            normalized_name = normalize_name(current_name)
            # print(f"Original Name: '{current_name}', Normalized Name: '{normalized_name}'")

            
            # Map normalized name to ISIN when instrument is a fund
            if normalized_name in fund_name_primary_isin:
                
                isin = fund_name_primary_isin.get(normalized_name)
                print(isin)
                df = funds_andelsklasser[isin]
                avgift = df.loc[df['Andelsklass_namn'] == current_name]['Förvaltningsavgift_fast']
                # print(current_value, current_name)
                print(avgift.values)
                if len(avgift) > 0 and avgift.values[0] > 0:
                    cumulative_fee += current_value * avgift.values[0]/100
                    print(cumulative_fee)
                else:
                    print("Avgift fel", isin)
                
                # print(f"ISIN from fund_name_primary_isin: {isin} found for {normalized_name}")
            # Map normalized name to ISIN when instrument is NOT a fund i.e. share or other holding
            else:
                isin = name_to_isin.get(normalized_name)
                # print(f"ISIN from name_to_isin: {isin} found for {normalized_name}")
            
            # if not isin:
            #     print(f"Could not find ISIN for '{normalized_name}'.")
            #     # Optionally, try to map using the original name
            #     isin = fund_name_primary_isin.get(current_name)
            #     if isin:
            #         print(f"Found ISIN using original name: {isin}")
            #     else:
            #         print(f"No ISIN found for '{current_name}'. Skipping expansion.")
            #         isin = current_name  # or handle appropriately



            # # Check if we already have expanded this fund in the cache
            ## TROR INTE DETTA BEHÖVS DÅ SAMMA FOND SKALL KUNNA ITERERS FLERA GÅNGER OM CROSS HOLDINGS FINNS.
            if normalized_name in expansion_cache:
                expansion_result = expansion_cache[normalized_name]
                for instrument in expansion_result:
                    stack.append((instrument['Instrument_ISIN'], current_value * instrument['Weight'], depth + 1, current_name))
                # continue
            

            expansion_log.append({
                'Type': 'Holding',
                'Mother': mother_name,  # Add mother name here                
                'Original Name': current_name,
                'Normalized Name': normalized_name,
                'Value': current_value,
                'Depth': depth,
                'ISIN': isin,
                'Mapped ISIN': None,
                'Message': None
                })

            # If ISIN is not found, check if we have the normalized name in the dataframes dictionary
            # if not isin:
            #     if normalized_name in dataframes:
            #         expansion_log.append({
            #             'Type': 'Info',
            #             'Mother': mother_name,                        
            #             'Original Name': current_name,
            #             'Normalized Name': normalized_name,
            #             'Value': current_value,
            #             'Depth': depth,
            #             'ISIN': None,
            #             'Mapped ISIN': None,
            #             'Message': f"Mapping by normalized name: '{normalized_name}' found in dataframes."
            #         })
            #         isin = normalized_name
            #     else:
            #         expansion_log.append({
            #             'Type': 'Info',
            #             'Mother': mother_name,
            #             'Original Name': current_name,
            #             'Normalized Name': normalized_name,
            #             'Value': current_value,
            #             'Depth': depth,
            #             'ISIN': None,
            #             'Mapped ISIN': None,
            #             'Message': f"Could not find a match for '{normalized_name}', skipping further expansion."
            #         })
            #         isin = current_name

            # Continue expanding if it's a fund
            if isin in dataframes:
                # Check if the current depth has reached the maximum allowed depth
                if depth > max_depth:
                    expansion_log.append({
                        'Type': 'Info',
                        'Mother': mother_name,
                        'Original Name': current_name,
                        'Normalized Name': normalized_name,
                        'Value': current_value,
                        'Depth': depth,
                        'ISIN': isin,
                        'Mapped ISIN': None,
                        'Message': f"Reached max depth for fund '{isin}' at depth {depth}. Skipping further processing."
                    })
                    # continue  # Skip processing if the depth exceeds max_depth

                # Always update the depth of the current fund and process it
                processed_funds[isin] = depth

                # Retrieve the DataFrame for the current fund
                try:
                    fund_df = dataframes[isin]
                except:
                    print(f"keyError: ISIN '{isin}' not found in dataframes")

                if isinstance(fund_df, pd.DataFrame) and not fund_df.empty :
                    # Store expansion result in cache
                    expansion_cache[normalized_name] = []

                    for _, instrument in fund_df.iterrows():
                        instrument_name = instrument["Instrumentnamn"]
                        normalized_instrument_name = normalize_name(instrument_name)
                        instrument_isin = instrument["Instrument_ISIN"]
                        # Map instrument ISIN if necessary

                        # Map normalized name to ISIN when instrument is a fund
                        if normalized_instrument_name in fund_name_primary_isin:
                            instrument_isin_mapped = fund_name_primary_isin.get(normalized_instrument_name)
                        # Map normalized name to ISIN when instrument is NOT a fund i.e. share or other holding
                        else:
                            instrument_isin_mapped = name_to_isin.get(normalized_instrument_name, instrument_isin)                       

                        # Log the expansion of the instrument
                        expansion_log.append({
                            'Type': 'Instrument',
                            'Mother': current_name,  # Set the current_name as the mother for each instrument
                            'Original Name': instrument_name,
                            'Normalized Name': normalized_instrument_name,
                            'Value': current_value * (instrument["Andel_av_fondförmögenhet_instrument"] / 100),
                            'Depth': depth + 1,
                            'ISIN': instrument_isin,
                            'Mapped ISIN': instrument_isin_mapped,
                            'Message': None
                        })

                        weight = instrument["Andel_av_fondförmögenhet_instrument"] / 100
                        expansion_cache[normalized_name].append({'Instrument_ISIN': instrument_isin_mapped, 'Weight': weight})
                        stack.append((normalized_instrument_name, current_value * weight, depth + 1, current_name))
                else:
                    expansion_log.append({
                        'Type': 'Error',
                        'Mother': mother_name,
                        'Original Name': current_name,
                        'Normalized Name': normalized_name,
                        'Value': current_value,
                        'Depth': depth,
                        'ISIN': isin,
                        'Mapped ISIN': None,
                        'Message': f"Expected a DataFrame for ISIN {isin}, but got {type(fund_df)}"
                    })
            else:
                # It's an individual instrument
                if isin in cumulative_exposures:
                    cumulative_exposures[isin]['Exposure'] += current_value
                    cumulative_exposures[isin]['Depth'] = max(cumulative_exposures[isin]['Depth'], depth)
                else:
                    cumulative_exposures[isin] = {'Exposure': current_value, 'Depth': depth}
        
    # Start expanding all holdings in table_A
    for idx, row_A in table_A.iterrows():
        name_A = row_A["Name"]
        value_A = row_A["Exposure"]
        expand_holding_iteratively(name_A, value_A, cumulative_exposures, max_depth)

    # Convert cumulative exposures to DataFrame
    data_cumulative = []
    for isin, info in cumulative_exposures.items():
        exposure = info['Exposure']
        depth = info['Depth']
        name = isin_to_name.get(isin, isin)
        data_cumulative.append({'Name': name, 'ISIN': isin, 'Exposure': exposure, 'Depth': depth})

    table_C = pd.DataFrame(data_cumulative)

    # Convert expansion_log to DataFrame
    global expansion_log_df
    expansion_log_df = pd.DataFrame(expansion_log)

    return table_C, expansion_log_df


# Function to generate portfolio analysis summary
def generate_portfolio_summary(table_C):
    total_exposure = table_C['Exposure'].sum()
    largest_holding = table_C.loc[table_C['Exposure'].idxmax()]

    summary = (
        f"Your portfolio has a total exposure of SEK {total_exposure:,.2f}. "
        f"The largest holding is {largest_holding['Name']} with an exposure of "
        f"SEK {largest_holding['Exposure']:,.2f}, accounting for "
        f"{(largest_holding['Exposure'] / total_exposure) * 100:.2f}% of your portfolio.\n\n"
        "General suggestions for improvement:\n"
        "- Consider diversifying your holdings to reduce concentration risk.\n"
        "- Review the performance and risk associated with the largest holdings.\n"
        "- Ensure that your portfolio aligns with your long-term investment goals."
    )

    return summary

# Function to create a pie chart with 'Other' category
def create_pie_chart_with_other(data1, labels, total_exposure):
    # Calculate the sum of the top holdings
    top_holdings_exposure = sum(data1)
    # Calculate 'Other' exposure
    other_exposure = total_exposure - top_holdings_exposure
    # Append 'Other' data
    data1.append(other_exposure)
    labels.append('Other')
    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(data1, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title('Portfolio Allocation')
    plt.show()

def main():
    print("Input Your Holdings")

    # Initialize table_A with predefined holdings
    table_A = pd.DataFrame({
        'Name': ['Länsförsäkringar Fastighetsfond'], 
        # Handelsbanken norden selektiv
        # Assa Abloy B

        'Exposure': [100000]
    }) # 'Handelsbanken Aktiv 100' 'Handelsbanken Amerika Tema'

    # Iterate over the existing table_A to match and modify holdings
    for index, row in table_A.iterrows():
        name = row['Name']
        # value = row['Exposure']

        # Find the best match for the name
        best_match_name = find_best_name_match(name, possible_names_list)
        
        if best_match_name:
            # Update the 'Name' in table_A with the best match name
            table_A.at[index, 'Name'] = best_match_name
        else:
            print(f"Could not match {name} to any fund or instrument.")

    # Proceed with the rest of your code using the updated table_A
    # Generate table_C using the collected data
    if not table_A.empty:
        global table_C,expansion_log
        table_C, expansion_log = create_table_C(
            table_A,
            dataframes,
            fund_name_primary_isin,
            name_to_isin,
            isin_to_name,
            max_depth=3
        )
        print("\nCalculated Holdings (Table C):")
        print(table_C.sort_values(by='Exposure', ascending=False))
        global holdings_top10
        holdings_top10 = table_C.sort_values(by='Exposure', ascending=False).head(10)

        if not holdings_top10.empty:
            labels = holdings_top10['Name'].tolist()
            data = holdings_top10['Exposure'].tolist()
            total_exposure = table_C['Exposure'].sum()

            print("\nPie Chart of Your Top 10 Holdings with Other Exposures")
            create_pie_chart_with_other(data, labels, total_exposure)

            print("\nPortfolio Analysis Summary")
            summary = generate_portfolio_summary(table_C)
            print(summary)

        # Print expansion log DataFrame
        print("\nExpansion Log:")
        # print(expansion_log.to_string(index=False))
    else:
        print("Please enter your holdings above.")

if __name__ == "__main__":
    main()

# %%
