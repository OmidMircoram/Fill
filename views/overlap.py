import streamlit as st

def laps(top):
    top = top[['fund', 'fund_isin', 'overlap_score']]
    st.dataframe(top)