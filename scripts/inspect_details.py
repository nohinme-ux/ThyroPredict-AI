import openpyxl
import pandas as pd

excel_path = "sts thyroid data.xlsx"
xl = pd.ExcelFile(excel_path)

for s in xl.sheet_names:
    print(f"\n{'='*20} SHEET {s} DETAILS {'='*20}")
    df = xl.parse(s)
    # Check for text in columns that might be diagnostic
    for col in df.columns:
        if df[col].dtype == 'object':
            vals = df[col].dropna().unique()
            if len(vals) < 30:
                print(f"Sheet {s} - Col '{col}' unique values ({len(vals)}):", vals[:10])

    # Check first row and header row
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb[s]
    print(f"\nSheet {s} First 5 rows raw:")
    for r in list(ws.iter_rows(values_only=True))[:5]:
        # print non-none
        non_none = [f"c{i}:{v}" for i, v in enumerate(r) if v is not None]
        if non_none:
            print("  ", non_none[:8])
