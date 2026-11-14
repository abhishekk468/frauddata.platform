from pathlib import Path

import pandas as pd
import streamlit as st


DATA = Path(__file__).resolve().parent.parent / "dashboard_data"

st.set_page_config(page_title="Fraud Analytics", layout="wide")
st.title("Fraud Analytics Dashboard")

daily = pd.read_parquet(DATA / "fct_daily_fraud.parquet")
hourly = pd.read_parquet(DATA / "fct_hourly_fraud.parquet")
tradeoff = pd.read_parquet(DATA / "fct_threshold_tradeoff.parquet")

fraud_only = daily[daily["txn_type"].isin(["TRANSFER", "CASH_OUT"])]

c1, c2, c3 = st.columns(3)

c1.metric("Total transactions", f"{int(daily['txn_count'].sum()):,}")
c2.metric("Fraud transactions", f"{int(daily['fraud_count'].sum()):,}")
c3.metric("Fraud value", f"{daily['fraud_amount'].sum():,.0f}")

st.subheader("Fraud value by transaction type")
by_type = fraud_only.groupby("txn_type", as_index=False)["fraud_amount"].sum()
st.bar_chart(by_type, x="txn_type", y="fraud_amount")

st.subheader("Fraud rate by hour of day (TRANSFER and CASH_OUT)")
st.bar_chart(hourly, x="hour_of_day", y="fraud_rate_pct")

st.subheader("Daily fraud count")
daily_total = daily.groupby("day_index", as_index=False)["fraud_count"].sum()
st.line_chart(daily_total, x="day_index", y="fraud_count")

st.subheader("Blocking by amount threshold")
st.dataframe(
    tradeoff[["amount_threshold", "fraud_value_blocked_pct", "legit_blocked_pct"]],
    width="stretch",
)

st.caption("Each row: block every TRANSFER or CASH_OUT above the amount threshold.")
