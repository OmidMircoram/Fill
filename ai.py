#%%
import pandas as pd
import pandasai as pai
from pandasai_litellm.litellm import LiteLLM
import streamlit as st
def call_ai(user_prompt, df: pd.DataFrame):
    client = LiteLLM(model="gpt-5-nano", api_key="")
    pai.config.set({
        "llm":client
    })
    # Ta ett steg som hämptar ex returns, sharpkvot osv och syr på, på innehavsnivå i SAMMA dataframe.
    dfai = pai.DataFrame(df)
    # pandasai.DataFrame({
    #     "Holdings": ["Nvidia"],
    #     "Amount": [600000]
    # })
    # response = client.responses.create(
    #     model="gpt-5-nano",
    #     input="Write a short bedtime story about a unicorn."
    # )
    ai_answer =pai.chat(user_prompt, dfai, st.session_state["top_overlaps"])
    st.session_state["conversation"][-1].append(ai_answer)
    return ai_answer
# %%
