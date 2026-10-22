import pandas as pd
import openpyxl

wb = openpyxl.load_workbook("sts thyroid data.xlsx", data_only=True)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    print(f"\n================ SHEET: {sheet} (max_row={ws.max_row}, max_col={ws.max_column}) ================")
    # Print the first 10 rows, columns 1 to 20
    for r in range(1, min(12, ws.max_row + 1)):
        row_vals = [ws.cell(r, c).value for c in range(1, min(25, ws.max_column + 1))]
        if any(v is not None for v in row_vals):
            print(f"Row {r}: {row_vals[:12]}")
