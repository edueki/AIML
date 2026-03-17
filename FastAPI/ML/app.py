import streamlit as st
import requests
import json

st.set_page_config(page_title="Loan Approval Predictor", page_icon="💳", layout="centered")
st.title("💳 Loan Approval Predictor")

# Point this to your FastAPI /predict endpoint
API_URL = "http://127.0.0.1:8000/predict"

st.markdown("Fill out the application and click **Predict**.")

with st.form("loan_form", clear_on_submit=False):
    c1, c2 = st.columns(2)

    with c1:
        no_of_dependents = st.number_input("Number of Dependents", min_value=0, value=0, step=1)
        education = st.selectbox("Education", options=["Graduate", "Not Graduate"], index=0)
        self_employed = st.selectbox("Self Employed", options=["Yes", "No"], index=1)
        credit_score = st.number_input("Credit Score", min_value=0, value=700, step=1)

    with c2:
        income_annum = st.number_input("Annual Income", min_value=0.0, value=50000.0, step=1000.0)
        loan_amount = st.number_input("Loan Amount", min_value=0.0, value=10000.0, step=500.0)
        loan_term = st.number_input("Loan Term (months)", min_value=1.0, value=36.0, step=1.0)
        total_asset_value = st.number_input("Total Asset Value", min_value=0.0, value=150000.0, step=1000.0)

    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "no_of_dependents": int(no_of_dependents),
        "education": education,               # FastAPI converts "Graduate"->1 else 0
        "self_employed": self_employed,       # FastAPI converts "Yes"->1 else 0
        "income_annum": float(income_annum),
        "loan_amount": float(loan_amount),
        "loan_term": float(loan_term),
        "credit_score": int(credit_score),
        "total_asset_value": float(total_asset_value),
    }

    with st.spinner("Calling FastAPI..."):
        try:
            resp = requests.post(API_URL, json=payload, timeout=10)
            if resp.ok:
                data = resp.json()
                status = data.get("Loan Approval Status")
                err = data.get("error")
                if status is not None:
                    emoji = "✅" if status.lower() == "approved" else "❌"
                    st.success(f"{emoji} Loan Approval Status: **{status}**")
                elif err:
                    st.error(f"API error: {err}")
                else:
                    st.warning(f"Unexpected response: {json.dumps(data, indent=2)}")
            else:
                st.error(f"HTTP {resp.status_code}: {resp.text}")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")