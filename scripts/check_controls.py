import pandas as pd

df3 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet3")
print("Total rows in Sheet 3:", len(df3))
print("Sheet 3 non-empty NAME:", df3['NAME'].dropna().count())
print("Sheet 3 DURATION value counts:")
print(df3['DURATION'].value_counts(dropna=False))

# What about Sheet 1 vs Sheet 3?
# Let's see names in Sheet 3 that have 'C'
controls = df3[df3['DURATION'] == 'C']
print(f"\nNumber of controls ('C') in Sheet 3: {len(controls)}")
print(controls[['NAME', 'AGE', 'SEX', 'TSH', 'FT3', 'FT4', 'Anti tpo']].head(20))

# Does Sheet 1 have any 'C'?
df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
print("\nSheet 1 DURATION unique values:")
print(df1['DURATION'].dropna().unique())
