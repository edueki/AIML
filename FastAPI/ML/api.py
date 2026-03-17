from fastapi import FastAPI, Form
from pydantic import BaseModel
import pandas as pd
import joblib
import uvicorn

app = FastAPI()

# Load the model
LG_model = joblib.load('loan.pkl')

class LoanApplication(BaseModel):
    no_of_dependents: int
    education: str
    self_employed: str
    income_annum: float
    loan_amount: float
    loan_term: float
    credit_score: int
    total_asset_value: float

@app.post("/predict")
def predict(application: LoanApplication):
    try:
        dataset = {
            "no_of_dependents": application.no_of_dependents,
            "education": 1 if application.education == "Graduate" else 0,
            "self_employed": 1 if application.self_employed == "Yes" else 0,
            "income_annum": application.income_annum,
            "loan_amount": application.loan_amount,
            "loan_term": application.loan_term,
            "credit_score": application.credit_score,
            "total_asset_value": application.total_asset_value
        }
        
        input_df = pd.DataFrame([dataset])
        pred_results = LG_model.predict(input_df)
        status = "Approved" if pred_results[0] == 1 else "Rejected"
        
        return {"Loan Approval Status": status}
    except Exception as e:
        return {"error": str(e)}
if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0", port=8000)
