from pathlib import Path

import pandas as pd
import streamlit as st


DATA = Path(__file__).resolve().parent.parent / "dashboard_data"

st.set_page_config(page_title="Fraud Analytics", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    .stApp {
        background: #f5f5f3;
        color: #171717;
    }

    [data-testid="stHeader"] {
        background: #f5f5f3;
    }

    .block-container {
        max-width: 1440px;
        padding: 3.25rem 3.5rem 4rem;
    }

    h1, h2, h3, [data-testid="stMetricLabel"] {
        font-family: "Space Grotesk", sans-serif;
    }

    h1 {
        letter-spacing: -0.04em;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #b8b8b5;
        border-top: 4px solid #171717;
        border-radius: 0;
        box-shadow: none;
        padding: 1.1rem 1.25rem;
        animation: rise-in 0.65s ease-out both;
        transition: border-color 180ms ease, background 180ms ease;
    }

    [data-testid="stMetric"]:hover {
        background: #eeeeec;
        border-color: #171717;
    }

    [data-testid="stMetricValue"] {
        color: #171717;
        font-family: "Space Grotesk", sans-serif;
        font-size: 2rem;
    }

    [data-testid="stMetricLabel"] {
        color: #676767;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    [data-testid="stMetric"]:nth-child(2) {
        animation-delay: 90ms;
    }

    [data-testid="stMetric"]:nth-child(3) {
        animation-delay: 180ms;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #b8b8b5;
        border-radius: 0;
        overflow: hidden;
    }

    .hero {
        animation: rise-in 0.55s ease-out both;
        margin-bottom: 2rem;
    }

    .eyebrow {
        color: #676767;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #171717;
        font-size: clamp(2.2rem, 5vw, 4.25rem);
        margin: 0.35rem 0 0.5rem;
    }

    .hero p {
        color: #676767;
        font-size: 1.05rem;
        margin: 0;
        max-width: 42rem;
    }

    .status-pill {
        align-items: center;
        background: #ffffff;
        border: 1px solid #b8b8b5;
        border-radius: 0;
        color: #4a4a4a;
        display: inline-flex;
        font-size: 0.78rem;
        font-weight: 600;
        gap: 0.45rem;
        margin-top: 1.1rem;
        padding: 0.45rem 0.75rem;
    }

    .status-dot {
        animation: pulse 1.8s ease-in-out infinite;
        background: #171717;
        border-radius: 50%;
        height: 0.48rem;
        width: 0.48rem;
    }

    .section-label {
        color: #767676;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        margin: 2.2rem 0 0.35rem;
        text-transform: uppercase;
    }

    .section-title {
        color: #171717;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.35rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    @keyframes rise-in {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.35; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Risk intelligence · PaySim</div>
        <h1>Fraud Analytics</h1>
        <p>A focused view of fraud exposure, timing patterns, and the cost of intervention.</p>
        <div class="status-pill"><span class="status-dot"></span>Warehouse synced · 6.36M transactions analyzed</div>
    </div>
    """,
    unsafe_allow_html=True,
)

daily = pd.read_parquet(DATA / "fct_daily_fraud.parquet")
hourly = pd.read_parquet(DATA / "fct_hourly_fraud.parquet")
tradeoff = pd.read_parquet(DATA / "fct_threshold_tradeoff.parquet")

fraud_only = daily[daily["txn_type"].isin(["TRANSFER", "CASH_OUT"])]

c1, c2, c3 = st.columns(3)

c1.metric("Total transactions", f"{int(daily['txn_count'].sum()):,}")
c2.metric("Fraud transactions", f"{int(daily['fraud_count'].sum()):,}")
c3.metric("Fraud value", f"{daily['fraud_amount'].sum():,.0f}")

st.markdown('<div class="section-label">Exposure profile</div><div class="section-title">Where fraud value concentrates</div>', unsafe_allow_html=True)
by_type = fraud_only.groupby("txn_type", as_index=False)["fraud_amount"].sum()
st.bar_chart(by_type, x="txn_type", y="fraud_amount")

st.markdown('<div class="section-label">Temporal signal</div><div class="section-title">When risk peaks</div>', unsafe_allow_html=True)
st.bar_chart(hourly, x="hour_of_day", y="fraud_rate_pct")

st.markdown('<div class="section-label">Trend watch</div><div class="section-title">Daily fraud count</div>', unsafe_allow_html=True)
daily_total = daily.groupby("day_index", as_index=False)["fraud_count"].sum()
st.line_chart(daily_total, x="day_index", y="fraud_count")

st.markdown('<div class="section-label">Decision support</div><div class="section-title">Blocking by amount threshold</div>', unsafe_allow_html=True)
st.dataframe(
    tradeoff[["amount_threshold", "fraud_value_blocked_pct", "legit_blocked_pct"]],
    width="stretch",
    hide_index=True,
    column_config={
        "amount_threshold": st.column_config.NumberColumn("Threshold", format="$%,.0f"),
        "fraud_value_blocked_pct": st.column_config.NumberColumn(
            "Fraud value blocked", format="%.2f%%"
        ),
        "legit_blocked_pct": st.column_config.NumberColumn(
            "Legitimate blocked", format="%.2f%%"
        ),
    },
)

st.caption("Each row blocks every TRANSFER or CASH_OUT above the selected threshold.")
