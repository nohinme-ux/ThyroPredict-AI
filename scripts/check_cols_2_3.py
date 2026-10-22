import pandas as pd

df2 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet2")
print("DF2 Columns:")
for c in df2.columns:
    if not c.startswith("Unnamed:"):
        print(" ", c)
    else:
        # check if it has values
        cnt = df2[c].dropna().count()
        if cnt > 5:
            print(f"  {c} (count={cnt}, sample={df2[c].dropna().unique()[:3]})")

print("\nDF3 Columns:")
df3 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet3")
for c in df3.columns:
    if not c.startswith("Unnamed:"):
        print(" ", c)
    else:
        cnt = df3[c].dropna().count()
        if cnt > 5:
            print(f"  {c} (count={cnt}, sample={df3[c].dropna().unique()[:3]})")
