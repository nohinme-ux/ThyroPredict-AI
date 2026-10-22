import pandas as pd

df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
# Drop rows where NAME and AGE and SEX are all null
valid1 = df1[df1['NAME'].notna()]
print(f"Sheet 1 valid rows with NAME: {len(valid1)}")
print(valid1[['Unnamed: 0', 'NAME', 'AGE', 'SEX', 'TSH', 'FT3', 'FT4', 'Anti tpo', 'Unnamed: 20']].head(30))

print("\nValue counts of Unnamed: 20 in Sheet 1 valid rows:")
print(valid1['Unnamed: 20'].value_counts(dropna=False))
