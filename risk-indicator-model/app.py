import streamlit as st
import mysql.connector
import pandas as pd

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
HOST = "127.0.0.1"
PORT = 3306
DB   = "riskindicator"
USER = "root"
PWD  = "2025"

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Risk Indicator Model",
    layout="wide"
)

st.title("🔍 Risk Indicator & Fraud Detection Dashboard")
st.markdown("SQL-Based Transaction Auditing and Fraud-Risk Analytics System")

# -----------------------------
# DATABASE FUNCTION
# -----------------------------
def run_query(query, params=None):
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PWD,
        database=DB
    )

    cursor = conn.cursor(dictionary=True)

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    rows = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return rows

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📊 Audit Risk Metrics")

col1, col2, col3 = st.columns(3)

total_transactions_query = """
SELECT COUNT(*) AS total_transactions
FROM transaction;
"""

high_risk_query = """
SELECT COUNT(*) AS high_risk_transactions
FROM transaction
WHERE risk_score >= 75;
"""

avg_risk_query = """
SELECT ROUND(AVG(risk_score),2) AS avg_risk_score
FROM transaction;
"""

total_transactions = run_query(total_transactions_query)[0]["total_transactions"]
high_risk_transactions = run_query(high_risk_query)[0]["high_risk_transactions"]
avg_risk_score = run_query(avg_risk_query)[0]["avg_risk_score"]

col1.metric("Total Transactions", total_transactions)
col2.metric("High Risk Transactions", high_risk_transactions)
col3.metric("Average Risk Score", avg_risk_score)

st.divider()

# -----------------------------
# HIGH RISK TRANSACTIONS
# -----------------------------
st.subheader("🚨 High Risk Transactions")

risk_query = """
SELECT 
    t.transaction_id,
    c.client_name,
    v.vendor_name,
    d.department_name,
    t.amount,
    t.transaction_date,
    t.risk_score,

    CASE
        WHEN t.risk_score >= 90 THEN 'Critical Risk'
        WHEN t.risk_score >= 75 THEN 'High Risk'
        WHEN t.risk_score >= 50 THEN 'Moderate Risk'
        ELSE 'Low Risk'
    END AS risk_level

FROM transaction t

LEFT JOIN client c
    ON t.client_id = c.client_id

LEFT JOIN vendor v
    ON t.vendor_id = v.vendor_id

LEFT JOIN department d
    ON t.department_id = d.department_id

WHERE t.risk_score >= 50

ORDER BY t.risk_score DESC, t.amount DESC;
"""

risk_data = run_query(risk_query)

if risk_data:
    df = pd.DataFrame(risk_data)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No high-risk transactions found.")

st.divider()

# -----------------------------
# SEARCH TRANSACTIONS
# -----------------------------
st.subheader("🔎 Search Transactions Above Amount")

minimum_amount = st.number_input(
    "Enter minimum transaction amount",
    min_value=0.0,
    value=1000.0
)

if st.button("Run Audit Query"):

    search_query = """
    SELECT
        transaction_id,
        amount,
        transaction_date,
        risk_score
    FROM transaction
    WHERE amount >= %s
    ORDER BY amount DESC;
    """

    search_results = run_query(search_query, (minimum_amount,))

    if search_results:
        df = pd.DataFrame(search_results)
        st.dataframe(df, use_container_width=True)
        st.success(f"{len(df)} transactions returned.")
    else:
        st.info("No matching transactions found.")

st.divider()

# -----------------------------
# INSERT TRANSACTION
# -----------------------------
st.subheader("➕ Insert New Transaction")

with st.form("insert_form"):

    amount = st.number_input("Amount", min_value=0.0)
    vendor_id = st.number_input("Vendor ID", min_value=1)
    department_id = st.number_input("Department ID", min_value=1)

    submitted = st.form_submit_button("Insert Transaction")

    if submitted:

        calculated_risk = 25

        if amount >= 10000:
            calculated_risk = 95
        elif amount >= 5000:
            calculated_risk = 75
        elif amount >= 1000:
            calculated_risk = 50

        insert_query = """
        INSERT INTO transaction
        (transaction_date, amount, vendor_id, department_id, risk_score)
        VALUES
        (CURDATE(), %s, %s, %s, %s);
        """

        run_query(
            insert_query,
            (amount, vendor_id, department_id, calculated_risk)
        )

        st.success(
            f"Transaction inserted successfully with risk score {calculated_risk}."
        )