import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.trade_model import get_trade_partner_summaries, get_sankey_trade_flows

st.set_page_config(page_title="Malaysia Trade Partner & Concentration Analysis", layout="wide")
st.title("TRADE PARTNER SANKEY & CONCENTRATION ANALYSIS")
st.caption("External Trade, HHI Index, and Global Trade Resilience (Tables 3.7, 3.10, 3.12)")

summaries, metrics = get_trade_partner_summaries("2026_8m")
sankey_data = get_sankey_trade_flows()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Top 3 Partner Share (CN, SG, US)", f"{metrics['top_3_concentration_pct']:.1f}%")
k2.metric("Trade Concentration (HHI)", f"{metrics['hhi_total_trade']:.0f}")
k3.metric("GTRI 2026 Global Rank", f"#{int(metrics['gtri_2026_rank'])} (Score: {metrics['gtri_2026_score']})")
k4.metric("Strait of Hormuz Crude Exposure", f"{metrics['hormuz_crude_transit_pct']:.0f}%")

fig = go.Figure(data=[go.Sankey(
    node=dict(pad=15, thickness=18, label=sankey_data["nodes"], color="#1D4ED8"),
    link=dict(source=sankey_data["sources"], target=sankey_data["targets"], value=sankey_data["values"], label=sankey_data["labels"])
)])
fig.update_layout(title="Malaysia Trade Flows (Jan-Aug 2026, RM Million)", paper_bgcolor="#FFFFFF")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Partner Breakdown")
st.dataframe(pd.DataFrame([s.model_dump() for s in summaries]), use_container_width=True)
