import streamlit as st
import joblib
import pandas as pd
import numpy as np

st.title("Salary Prediction System")
st.header("Salary Prediction System")

no_of_dependents = st.number_input("Number of Dependents", 1, 10)
education = st.selectbox("Education", ['Graduate', "Not Graduate"])
self_employed = st.selectbox("Self Employed", ['Yes', "No"])
income_annum = st.number_input("Income Annually", min_value=1000)
loan_amount = st.number_input("Loan Amount", min_value=500)
loan_term = st.number_input("Loan Term", min_value=12)
credit_score = st.number_input("Credit Score", min_value=100)
asset_value = st.number_input("Asset Value", min_value=2000)

if st.button("Apply Loan!"):
    dataset = {
        "no_of_dependents": no_of_dependents,
        "education": 0 if education == "Graduate" else 1,
        "self_employed": 0 if self_employed == "Yes" else 1,
        "income_annum": np.log(income_annum),
        "loan_amount": np.log(loan_amount),
        "loan_term": loan_term,
        "credit_score": credit_score,
        "asset_value": np.log(asset_value),
    }
    df_data = pd.DataFrame([dataset])
    model = joblib.load("final_loan_pre.pkl")
    predictions = model.predict(df_data)
    st.write("Approved" if predictions == 0 else "Rejected")


