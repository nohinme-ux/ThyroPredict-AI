import pandas as pd
import numpy as np

df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
valid = df1[df1['NAME'].notna()].copy()

# clean TSH
def clean_num(x):
    if pd.isna(x):
        return np.nan
    s = str(x).replace('<', '').replace('>', '').strip()
    try:
        return float(s)
    except:
        return np.nan

valid['tsh_num'] = valid['TSH'].apply(clean_num)
valid['ft3_num'] = valid['FT3'].apply(clean_num)
valid['ft4_num'] = valid['FT4'].apply(clean_num)
valid['atpo_num'] = valid['Anti tpo'].apply(clean_num)

print("valid count:", len(valid))
print("TSH summary stats:")
print(valid['tsh_num'].describe())
print("\nAnti TPO summary stats:")
print(valid['atpo_num'].describe())
print("\nFT4 summary stats:")
print(valid['ft4_num'].describe())

print("\nTSH > 5.0 count:", (valid['tsh_num'] > 5.0).sum())
print("TSH < 0.4 count:", (valid['tsh_num'] < 0.4).sum())
print("TSH normal (0.4-5.0) count:", ((valid['tsh_num'] >= 0.4) & (valid['tsh_num'] <= 5.0)).sum())

# What about rows with Unnamed: 20 notna?
labeled = valid[valid['Unnamed: 20'].notna()]
print("\nLabeled rows TSH and Anti-TPO:")
print(labeled[['NAME', 'Unnamed: 20', 'tsh_num', 'ft4_num', 'atpo_num']].head(20))
