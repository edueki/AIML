import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

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
lg_model = LogisticRegression(max_iter=500)
model_lg = lg_model.fit(x_train, y_train)
results = model_lg.predict(x_test)
score = accuracy_score(y_test, results )
print (score)
if score > 0.80:
    joblib.dump(model_lg, "loan.pkl")
else:
    print ("Please continue the experiment")