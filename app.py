import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Risk Indicator Dashboard",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("data/transactions.csv")

# -----------------------------
# TITLE
# -----------------------------
st.title("🔍 Risk Indicator & Fraud Detection Dashboard")

st.markdown(
    "SQL and Python-based transaction auditing and fraud-risk analytics system."
)

# -----------------------------
# CREATE RISK LEVELS
# -----------------------------
def classify_risk(score):
    if score >= 90:
        return "Critical Risk"
    elif score >= 75:
        return "High Risk"
    elif score >= 50:
        return "Moderate Risk"
    else:
        return "Low Risk"

df["risk_level"] = df["risk_score"].apply(classify_risk)

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📊 Audit Risk Metrics")

col1, col2, col3 = st.columns(3)

total_transactions = len(df)
high_risk_transactions = len(df[df["risk_score"] >= 75])
avg_risk_score = round(df["risk_score"].mean(), 2)

col1.metric("Total Transactions", total_transactions)
col2.metric("High Risk Transactions", high_risk_transactions)
col3.metric("Average Risk Score", avg_risk_score)

st.divider()

# -----------------------------
# HIGH RISK TABLE
# -----------------------------
st.subheader("🚨 High Risk Transactions")

high_risk_df = df[df["risk_score"] >= 50]

st.dataframe(
    high_risk_df.sort_values(
        by="risk_score",
        ascending=False
    ),
    use_container_width=True
)

st.divider()

# -----------------------------
# SEARCH FEATURE
# -----------------------------
st.subheader("🔎 Search Transactions Above Amount")

minimum_amount = st.number_input(
    "Enter minimum transaction amount",
    min_value=0.0,
    value=1000.0
)

filtered_df = df[df["amount"] >= minimum_amount]

st.dataframe(
    filtered_df.sort_values(
        by="amount",
        ascending=False
    ),
    use_container_width=True
)

st.success(f"{len(filtered_df)} matching transactions found.")

st.divider()

# -----------------------------
# RISK DISTRIBUTION
# -----------------------------
st.subheader("📈 Risk Level Distribution")

risk_counts = df["risk_level"].value_counts()

st.bar_chart(risk_counts)