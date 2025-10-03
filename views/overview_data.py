#%%
import streamlit as st
import pandas as pd


def overview_data_page():
    # Load data and create overview
    overview_data = create_overview(st.session_state["all_funds"])

    overview_data[["return_6m (%)", "return_12m (%)", "return_24m (%)"]] = overview_data[["return_6m (%)", "return_12m (%)", "return_24m (%)"]].round(1)


    styled = overview_data.style.applymap(color_returns, subset=["return_6m (%)", "return_12m (%)", "return_24m (%)"]).format({"return_6m (%)": "{:.1f}", "return_12m (%)": "{:.1f}", "return_24m (%)": "{:.1f}"})
    st.title("📋 Fund Overview")
    st.dataframe(styled)
    #  width=1000, height=600

def create_overview(all_funds):
    """
    Create an overview DataFrame from the provided fund data.

    Parameters:
    all_funds (dict): A dictionary containing fund data.

    Returns:
    pd.DataFrame: A DataFrame containing an overview of the funds.
    """
    rows = []
    for fund_id in all_funds:
        fond_namn = all_funds[fund_id]["översikt"]["fond_namn"]
        fond_ticker= all_funds[fund_id]["översikt"]["ticker"]
        len_fonder= len(all_funds[fund_id]["innehav"])
        std= all_funds[fund_id]["översikt"]["standardavvikelse"]
        return_6m = all_funds[fund_id]["översikt"]["returns"]["6m"]
        return_12m= all_funds[fund_id]["översikt"]["returns"]["12m"]
        return_24m=all_funds[fund_id]["översikt"]["returns"]["24m"]
        variance=all_funds[fund_id]["översikt"]["variance"]
        förmögenhet_mnkr = all_funds[fund_id]["översikt"]["fondformogenhet"] / 1_000_000
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

# Display in Streamlit
def color_returns(val):
    if val > 0: return 'color: green'
    elif val < 0: return 'color: red'
    else: return ''
