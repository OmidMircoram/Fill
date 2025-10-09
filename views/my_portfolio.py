import streamlit as st
from main import load_data, rank_fund_overlaps
from engine import calculate_portfolio
from views.portfolio_breakdown import portfolio_breakdown
from views.chat_bot import bot
from views.overlap import laps

@st.cache_data
def calc_fund_holdings_looped(all_funds, mapping_after_scrape)-> dict:
    """
    Function that will add a df for the looped holdings for each fund.
    This makes comparing funds that has overlapping holdings possible.
    """
    for fund_isin in all_funds:
        fund_name = all_funds[fund_isin]['översikt']['fond_namn'] # Fetch fund name
        input_dict={0:{fund_name:1}} # Prepare the input dict and set value=1 in order to keep the result as share of the fund holding in %
        # input the fund name to retur
        fund_holdings_looped = calculate_portfolio(input_dict, all_funds, mapping_after_scrape)
        all_funds[fund_isin]['funds_holdings_looped'] = fund_holdings_looped
    return all_funds

def my_portfolio_page():
    all_funds, mapping=load_data()
    # all_funds = calc_fund_holdings_looped(all_funds, mapping) #DELETE THIS LINE FROM HERE WHEN DATA IMPORT SCRIPT IS RAN
    st.session_state["all_funds"] = all_funds
    st.session_state["mapping"] = mapping
    st.subheader("Select holdings and Investment Amounts", anchor = False)

    # Step 1: Multi-select holding names
    holding_options = st.session_state["mapping"]['instrument_namn'].unique()
    selected_holdings = st.multiselect("Choose Instruments", holding_options, accept_new_options = True)

    # Step 2: Input invested amount per selected stock
    input_dict = {0: {}}
    for holding in selected_holdings:
        invested = st.number_input(f"Amount invested in {holding}", min_value=0, value=0, step=100)
        if invested > 0:
            input_dict[0][holding] = invested

    # Step 3: Run portfolio calculation if we have valid input
    if input_dict[0]:
        my_portfolio_df = calculate_portfolio(input_dict,all_funds, mapping).reset_index()
        my_portfolio_df.sort_values(by="andel_av_fond")
        my_portfolio_df["portfolio_weight"] = my_portfolio_df['andel_av_fond'] / my_portfolio_df['andel_av_fond'].sum()
        top, results_df, details_map = rank_fund_overlaps(my_portfolio_df, all_funds)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="**Number of holdings in portfolio:**", value=f"{len(my_portfolio_df)}".replace(",", " "), border=True)
        # with col2:
        #     biggest_holding = my_portfolio_df.loc[my_portfolio_df['andel_av_fond'] == max(my_portfolio_df['andel_av_fond']), "instrument_namn"].iloc[0]
        #     biggest_holding_value = my_portfolio_df.loc[my_portfolio_df['instrument_namn'] == biggest_holding, "andel_av_fond"].iloc[0]
        #     st.metric(label=f"**Your biggest holding is:**", value = biggest_holding, delta=f"{biggest_holding_value}".replace(",", " "), border = True)
        # with  col3:
        #     top_three = top["fund"]
        #     st.metric(label="Top three overlapping funds:", value=f"{top_three}", delta= None, border=True)
        
        (chat_bot_tab, 
        portfolio_breakdown_tab,
        overlap_tab) = st.tabs(["Chat bot",
                                "Portfolio breakdown",
                                "Fund overlap",])

        with chat_bot_tab:
            bot(my_portfolio_df)

        with portfolio_breakdown_tab:
            portfolio_breakdown(my_portfolio_df)
        with overlap_tab:
            laps(top)

    else:
        st.info("Please select holdings and enter invested amounts to see your portfolio.")
