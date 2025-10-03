import streamlit as st
import plotly.express as px
import pandas as pd

def portfolio_breakdown(my_portfolio_df: pd.DataFrame):
    my_portfolio_df = my_portfolio_df.groupby(by="instrument_isin").agg({"andel_av_fond": "sum",
                                                             "instrument_isin": "count",
                                                             "instrument_namn": "first",
                                                             "landkod_emittent": "first",
                                                             "bransch": "first",
                                                             })

    st.write("-"*4)
    # Optional plots
    st.subheader(f"📦 Portfolio per country:")
    fig_country = px.pie(my_portfolio_df, values='andel_av_fond', names='landkod_emittent', title='By Country',)
    st.plotly_chart(fig_country, use_container_width=True)
    st.write("-"*4)
    st.subheader("Portfolio per industry:")
    fig_industry = px.bar(my_portfolio_df.groupby('bransch')['andel_av_fond'].sum().reset_index(),
                          x='bransch', y='andel_av_fond', title='By Industry', color='bransch')
    
    st.plotly_chart(fig_industry, use_container_width=True)
    st.subheader("Top 10 Holdings (Pie Chart)")

# Sort by "andel_av_fond"
    sorted_df = my_portfolio_df.sort_values("andel_av_fond", ascending=False)

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
    st.dataframe(my_portfolio_df)

 

