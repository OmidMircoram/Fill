import streamlit as st

def bot():
    prompt = st.chat_input("Ask something about your portfolio")
    if prompt:
        st.write(f"{prompt}")