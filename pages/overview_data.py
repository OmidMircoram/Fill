#%%
from main import load_data
import streamlit as st
import pandas as pd 
def create_overview(alla_fonder):
    """
    Create an overview DataFrame from the provided fund data.

    Parameters:
    alla_fonder (dict): A dictionary containing fund data.

    Returns:
    pd.DataFrame: A DataFrame containing an overview of the funds.
    """
    rows = []
    for fund_id in alla_fonder:
        fond_namn = alla_fonder[fund_id]["översikt"]["fond_namn"]
        fond_ticker= alla_fonder[fund_id]["översikt"]["ticker"]
        len_fonder= len(alla_fonder[fund_id]["innehav"])
        std= alla_fonder[fund_id]["översikt"]["standardavvikelse"]
        return_6m = alla_fonder[fund_id]["översikt"]["returns"]["6m"]
        return_12m= alla_fonder[fund_id]["översikt"]["returns"]["12m"]
        return_24m=alla_fonder[fund_id]["översikt"]["returns"]["24m"]
        variance=alla_fonder[fund_id]["översikt"]["variance"]
        förmögenhet_mnkr = alla_fonder[fund_id]["översikt"]["fondformogenhet"] / 1_000_000
        if förmögenhet_mnkr is None:
            förmögenhet_mnkr = 0.0
        if len_fonder > 0:
            rows.append({"fond_isin": fund_id,"ticker": fond_ticker, "fond_namn": fond_namn, "antal_innehav": len_fonder, "standardavvikelse": std, "fondformogenhet_mnkr": förmögenhet_mnkr, "return_6m (%)": return_6m, "return_12m (%)": return_12m, "return_24m (%)": return_24m, "variance": variance})
        else:
                rows.append({"fond_isin": fund_id,"ticker": fond_ticker, "fond_namn": fond_namn, "antal_innehav": 0, "standardavvikelse": std, "fondformogenhet_mnkr": förmögenhet_mnkr, "return_6m (%)": return_6m, "return_12m (%)": return_12m, "return_24m (%)": return_24m, "variance": variance})


    df = pd.DataFrame(rows)

    # for col in ["return_6m", "return_12m", "return_24m"]:
    #     df[col] = df[col].apply(lambda x: f"{x:.1f}%" if x is not None else "")
    return df


st.title("📋 Fund Overview")

# Load data and create overview
alla_fonder, _ = load_data() 
overview_data = create_overview(alla_fonder)

overview_data[["return_6m (%)", "return_12m (%)", "return_24m (%)"]] = overview_data[["return_6m (%)", "return_12m (%)", "return_24m (%)"]].round(1)

# Display in Streamlit
def color_returns(val):
    if val > 0: return 'color: green'
    elif val < 0: return 'color: red'
    else: return ''

styled = overview_data.style.applymap(color_returns, subset=["return_6m (%)", "return_12m (%)", "return_24m (%)"]).format({"return_6m (%)": "{:.1f}", "return_12m (%)": "{:.1f}", "return_24m (%)": "{:.1f}"})
st.dataframe(styled, width=1000, height=600)
st.set_page_config(layout="wide") 
