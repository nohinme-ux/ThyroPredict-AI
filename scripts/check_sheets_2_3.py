import pandas as pd

df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
df2 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet2")
df3 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet3")

print("DF2 non-null counts:")
print(df2.dropna(how='all').shape)
print("DF2 sample:")
print(df2[['NAME', 'AGE', 'SEX', 'Unnamed: 4', 'DURATION', 'TREATMENT', 'FT3', 'FT4', 'TSH']].dropna(subset=['NAME']).head(25))

print("\nDF3 sample:")
print(df3[['NAME', 'AGE', 'SEX', 'DURATION', 'FT3', 'FT4', 'TSH']].dropna(subset=['NAME']).head(25))
