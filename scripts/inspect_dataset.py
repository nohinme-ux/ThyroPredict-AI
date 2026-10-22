import openpyxl
import pandas as pd
import numpy as np

excel_path = "sts thyroid data.xlsx"
xl = pd.ExcelFile(excel_path)
print("Sheet names:", xl.sheet_names)

for sheet in xl.sheet_names:
    print(f"\n{'='*30} SHEET: {sheet} {'='*30}")
    df = xl.parse(sheet)
    print("Shape:", df.shape)
    print("Columns (all):", df.columns.tolist())
    print("\nSample Rows:")
    print(df.head(2))
    print("\nNon-null counts:")
    print(df.notnull().sum())
