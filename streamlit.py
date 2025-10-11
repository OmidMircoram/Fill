#%%
import streamlit as st

from views.my_portfolio import my_portfolio_page
from views.overview_data import overview_data_page
# from views.chat_bot import portfolio_breakdown
# from views.portfolio_breakdown import portfolio_breakdown

def main_script():
    st.set_page_config(layout="wide")
    with st.sidebar:
        st.write("tyoes")
        for qa in st.session_state["conversation"]:
            st.write(type(qa[0]))
            if len(qa)>1:
                st.write(type(qa[1]))
    st.title(":material/finance_mode: Portfolio Screener", anchor=False)
    if not st.session_state.get("conversation"):
        st.session_state["conversation"] = []
    pages = st.navigation(pages=[run_my_portfolio_page(), run_overview_data_page()])
    pages.run()

def run_my_portfolio_page():
    """Run the my_portfolio_page"""
    return st.Page(my_portfolio_page,
                   title= "My portfolio",
                   icon= ":material/tenancy:",
                   default = True
                   )

def run_overview_data_page():
    """Run the my_portfolio_page"""
    return st.Page(overview_data_page,
                   title= "Data overview",
                   icon= ":material/data_exploration:",
                   default = False
                   )

if __name__ == "__main__":
    main_script()
