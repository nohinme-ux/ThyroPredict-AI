import pandas as pd

df2 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet2")
df3 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet3")

print("DF2 Unnamed: 4 unique values and counts:")
print(df2['Unnamed: 4'].value_counts(dropna=False))

print("\nDF3 Unnamed: 4 unique values and counts:")
print(df3['Unnamed: 4'].value_counts(dropna=False))
