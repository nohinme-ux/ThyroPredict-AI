import pandas as pd
import openpyxl

wb = openpyxl.load_workbook("sts thyroid data.xlsx", data_only=True)

for sheetname in ["Sheet1", "Sheet2", "Sheet3", "Sheet4"]:
    ws = wb[sheetname]
    print(f"\n==================== {sheetname} ====================")
    # Check if there are any title blocks or text outside table
    for r in range(1, 20):
        vals = [ws.cell(r, c).value for c in range(1, 25)]
        # Check non-empty
        ne = [(c, v) for c, v in enumerate(vals, 1) if v is not None]
        if ne:
            print(f"Row {r}: {ne[:6]}")
