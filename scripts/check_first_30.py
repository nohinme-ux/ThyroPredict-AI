import pandas as pd

df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
print(df1[['NAME', 'AGE', 'SEX', 'DURATION', 'TSH', 'FT3', 'FT4', 'Anti tpo', 'Unnamed: 20']].head(30))
