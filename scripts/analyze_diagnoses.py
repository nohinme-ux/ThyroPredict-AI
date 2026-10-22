import pandas as pd
import openpyxl

wb = openpyxl.load_workbook("sts thyroid data.xlsx", data_only=True)

# Let's inspect Sheet 1, Sheet 2, Sheet 3
df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
df2 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet2")
df3 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet3")

print("DF1 shape:", df1.shape)
print("DF2 shape:", df2.shape)
print("DF3 shape:", df3.shape)

# Let's see what non-null values are in DF1['Unnamed: 20']
print("\nDF1 Unnamed: 20 value counts:")
print(df1['Unnamed: 20'].value_counts(dropna=False))

# What is DF1? Let's check TSH, FT3, FT4 in DF1
print("\nDF1 TSH sample:")
print(df1[['NAME', 'AGE', 'SEX', 'TSH', 'FT3', 'FT4', 'Anti tpo', 'Unnamed: 20']].head(15))

# What about the rest of DF1 where Unnamed: 20 is NaN?
# Are they Hypothyroid?
print("\nDF1 rows where Unnamed: 20 is NaN:")
print(df1[df1['Unnamed: 20'].isna()][['NAME', 'AGE', 'SEX', 'TSH', 'FT3', 'FT4', 'Anti tpo']].head(10))

# What about Sheet 2 and Sheet 3?
print("\nDF2 Unnamed: 4 value counts:")
print(df2['Unnamed: 4'].value_counts(dropna=False))

print("\nDF3 DURATION value counts (where 'C' appeared):")
print(df3['DURATION'].value_counts(dropna=False))
