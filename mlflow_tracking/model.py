import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import mlflow

le = LabelEncoder()
data = pd.read_csv('data.csv')
data.columns = [i.strip() for i in data.columns]
train_data = data.drop(columns="loan_status")
train_data = train_data.drop(columns="loan_id")
target_data = data['loan_status']
train_data ['total_asset_value'] = train_data['residential_assets_value'] + train_data['commercial_assets_value'] + train_data['luxury_assets_value'] + train_data['bank_asset_value']
train_data.drop(columns=['residential_assets_value','commercial_assets_value', 'luxury_assets_value', 'bank_asset_value'], inplace=True)
train_data['education'] = le.fit_transform(train_data['education'])
train_data['self_employed'] = le.fit_transform(train_data['self_employed'])
log_coumns = ['income_annum', 'loan_amount', 'total_asset_value']
train_data[log_coumns] = np.log(train_data[log_coumns])
target_data = le.fit_transform(target_data)

x_train,x_test,y_train,y_test =train_test_split(train_data,target_data,train_size=0.3, random_state=2)

params = {'C': 5, 'penalty': 'l2', 'solver': 'lbfgs','max_iter': 500, 'fit_intercept': True, 'class_weight': 'balanced','random_state': 40}

mlflow.set_tracking_uri("http://127.0.0.1:5000")

mlflow.set_experiment("Loan Application")

with mlflow.start_run():
    # Log the hyperparameters
    mlflow.log_params(params)

    # Train the model
    lr = LogisticRegression(**params)
    lr.fit(x_train, y_train)

    # Log the model
    model_info = mlflow.sklearn.log_model(sk_model=lr, name="loan_model")

    # Predict on the test set, compute and log the loss metric
    y_pred = lr.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric("accuracy", accuracy)

    # Optional: Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("Training Info", "Basic LR model for iris data")