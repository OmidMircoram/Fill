#%%
import streamlit as st
import pandas as pd
import plotly.express as px
from main import load_data
from engine_elias import calculate_portfolio
# Dummy data for mapping (replace with your real one)
all_funds, mapping=load_data()

# Dummy calculate_porfolio function (replace with real one)


# --- UI Starts ---
st.title("📈 Portfolio Builder")

st.subheader("Select Stocks and Investment Amounts")

# Step 1: Multi-select stock names
stock_options = mapping['instrument_namn'].unique()
selected_stocks = st.multiselect("Choose Instruments", stock_options, accept_new_options = True)

# Step 2: Input invested amount per selected stock
portfolio_dict = {0: {}}
for stock in selected_stocks:
    invested = st.number_input(f"Amount invested in {stock}", min_value=0, value=0, step=100)
    if invested > 0:
        portfolio_dict[0][stock] = invested

# Step 3: Run portfolio calculation if we have valid input
if portfolio_dict[0]:
    result_df = calculate_portfolio(portfolio_dict,all_funds, mapping).reset_index()
    st.subheader("📊 Portfolio Breakdown") 
    result_df = result_df.groupby(by="instrument_isin").agg({"andel_av_fond": "sum",
                                                             "instrument_isin": "count",
                                                             "instrument_namn": "first",
                                                             "landkod_emittent": "first",
                                                             "bransch": "first",
                                                             })
    st.dataframe(result_df)
    st.subheader(f"📦 Number of holdings in portfolio: {len(result_df)}")
    st.write("-"*4)
    # Optional plots
    st.subheader(f"📦 Portfolio per country:")
    fig_country = px.pie(result_df, values='andel_av_fond', names='landkod_emittent', title='By Country',)
    st.plotly_chart(fig_country, use_container_width=True)
    st.write("-"*4)
    st.subheader("Portfolio per industry:")
    fig_industry = px.bar(result_df.groupby('bransch')['andel_av_fond'].sum().reset_index(),
                          x='bransch', y='andel_av_fond', title='By Industry', color='bransch')
    
    st.plotly_chart(fig_industry, use_container_width=True)
    st.subheader("Top 10 Holdings (Pie Chart)")

# Sort by "andel_av_fond"
    sorted_df = result_df.sort_values("andel_av_fond", ascending=False)

    # Top 10 and Others
    top_10 = sorted_df.head(10)
    others = sorted_df.iloc[10:]

    # Add "Other" if needed
    if not others.empty:
        other_row = pd.DataFrame([{
            'instrument_namn': 'Other',
            'andel_av_fond': others['andel_av_fond'].sum(),
            'Landkod': 'Mixed',
            'bransch': 'Mixed'
        }])
        pie_data = pd.concat([top_10, other_row], ignore_index=True)
    else:
        pie_data = top_10

    # Plot it
    fig_top_holdings = px.pie(
        pie_data,
        values='andel_av_fond',
        names='instrument_namn',
        title='Top 10 Holdings + Other'
    )
    st.plotly_chart(fig_top_holdings, use_container_width=True)

 

else:
    st.info("Please select stocks and enter invested amounts to see your portfolio.")
