# from calculations.read_xml_elias import main
import matplotlib.pyplot as plt
import pandas as pd
from engine_elias import calc
from read_xml_elias import main

import streamlit as st

st.set_page_config(layout="wide")


@st.cache_data
def get_information():
    return main()


col1, col2 = st.columns([2, 3])
dt1, dt2 = get_information()
with col1:
    fonds = st.multiselect("Välj en fond:", dt2["fond_namn"])
    fond_df = pd.DataFrame(fonds, columns=["fonder"])
    fond_df["innehav"] = [1] * len(fonds)
    edited_df = (
        st.data_editor(fond_df, hide_index=True)
        .set_index("fonder")["innehav"]
        .to_dict()
    )
    if len(edited_df.keys()) < 1:
        st.stop()
    innehav1 = (
        calc({0: edited_df}, dt2, dt1)
        .groupby("instrument_isin")
        .agg({"instrument_namn": "first", "andel_av_fond": "sum"})
    )
    # st.write(innehav)
    top_10 = innehav1.sort_values("andel_av_fond", ascending=False).head(10)
    st.write(top_10)
labels = top_10["instrument_namn"]
sizes = top_10["andel_av_fond"]

with col2:
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)
    # st.write(dt1)
    # st.write(dt2)
