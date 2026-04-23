import pandas as pd

df = pd.read_csv("data/raw/telco_churn.csv")
print(df.head())
print(df.columns.tolist())
print(df.shape)
print(df.dtypes)
print(df["customerID"].nunique(), len(df))