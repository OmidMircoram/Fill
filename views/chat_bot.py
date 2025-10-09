import streamlit as st
from ai import call_ai

def bot(my_portfolio_df):
    prompt = st.chat_input("Ask something about your portfolio")
    if prompt:
        prompt = """
Your role is to be a private banker at a firm that offers financial advise to clients.
You are an expert in portfolio theory, investment strategies, fund investments, stock investments and macro economy. 
Summarize the users portfolio, the pros and cons with the portfolio composition.
Give your opinion on whether the clients portfolio and investment strategy could be improved somehow.
Make sure to explain all financial concepts in your answers.
The column "andel_av_fond" actually means the clients investments in swedish crowns.
The following is the clients prompt:
""" + prompt
        st.write(call_ai(prompt, my_portfolio_df))

# Vi vill kunna skicka med input_dict, fondernas direkt och ev totala innehav samt avgifter så att det går att fråga om fonderna i sig också.
# Även overlap-tabellen så att vi kan få svar på vilka fonder som kunden skulle kunna köpa istället för lägra avgift med samma exponering.