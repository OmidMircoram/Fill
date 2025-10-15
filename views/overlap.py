import streamlit as st
import plotly.express as px

def laps(top):
    top = top[['fund', 'fund_isin', 'overlap_score']]
    st.subheader("Top 10 overlapping funds:")
    overlap_chart(top)

    # st.dataframe(top)

def overlap_chart(top):
    # top['overlap_score'] = top['overlap_score'].round()
    fig_top = px.bar(top,
                     x='overlap_score',
                     y='fund', title=None,
                     color='fund',
                     color_discrete_sequence=px.colors.sequential.Plasma_r,
                     orientation='h',
                     labels=False)
    fig_top.update_traces(
        texttemplate="%{x:.0%}",   # 25.0%, 15.0%, ...
        textposition="outside",
        hovertemplate="%{x:.2%}")
    
    fig_top.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,     # döljer legend
        )
    fig_top.update_xaxes(
    visible=False)
    
    st.plotly_chart(fig_top, use_container_width=True)
