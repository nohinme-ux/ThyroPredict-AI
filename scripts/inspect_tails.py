import pandas as pd

df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
print("DF1 tail(20):")
print(df1[['Unnamed: 0', 'NAME', 'AGE', 'SEX', 'TSH', 'FT3', 'FT4', 'Anti tpo', 'Unnamed: 20']].tail(20))

print("\nDF2 tail(10):")
df2 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet2")
print(df2[['Unnamed: 0', 'NAME', 'AGE', 'SEX']].tail(10))

print("\nDF3 tail(10):")
df3 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet3")
print(df3[['Unnamed: 0', 'NAME', 'AGE', 'SEX', 'DURATION']].tail(10))

print("\nDF4 info:")
df4 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet4")
print(df4.dropna(how='all'))
