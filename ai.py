#%%
import pandas as pd
import pandasai as pai
from pandasai_litellm.litellm import LiteLLM

def call_ai(user_prompt, df: pd.DataFrame):
    client = LiteLLM(model="gpt-5-nano", api_key="")
    pai.config.set({
        "llm":client
    })
    dfai = pai.DataFrame(df) 
    # pandasai.DataFrame({
    #     "Holdings": ["Nvidia"],
    #     "Amount": [600000]
    # })
    # response = client.responses.create(
    #     model="gpt-5-nano",
    #     input="Write a short bedtime story about a unicorn."
    # )
    return dfai.chat(user_prompt)
# %%
