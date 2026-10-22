import pandas as pd
import numpy as np

df1 = pd.read_excel("sts thyroid data.xlsx", sheet_name="Sheet1")
valid = df1[df1['NAME'].notna()].copy()

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

# Let's inspect Anti-TPO threshold: clinical cut-off is typically 34 or 35 IU/mL
# Check rows with Anti-TPO > 34 vs rows labeled in Col 21
labeled_autoimmune = valid['Unnamed: 20'].str.contains('auto immune|graves|thyroiditis', case=False, na=False)
high_atpo = valid['atpo_num'] >= 34.0

print("Rows labeled as Autoimmune/Graves/Thyroiditis in Col 21:", labeled_autoimmune.sum())
print("Rows with Anti-TPO >= 34 IU/mL:", high_atpo.sum())
print("Overlap between both:", (labeled_autoimmune & high_atpo).sum())

# Let's see rows with high TSH (> 5.0) and normal/low Anti-TPO (< 34.0)
high_tsh_non_autoimmune = (valid['tsh_num'] > 5.0) & (~high_atpo) & (~labeled_autoimmune)
print("Rows with TSH > 5.0 (Hypothyroidism) and normal Anti-TPO (< 34):", high_tsh_non_autoimmune.sum())

# Normal TSH (0.4 - 5.0) and normal Anti-TPO (< 34)
normal_tsh_normal_atpo = (valid['tsh_num'] >= 0.4) & (valid['tsh_num'] <= 5.0) & (~high_atpo) & (~labeled_autoimmune)
print("Rows with normal TSH (0.4-5.0) and normal Anti-TPO (< 34):", normal_tsh_normal_atpo.sum())

# Low TSH (< 0.4)
low_tsh = (valid['tsh_num'] < 0.4) & (~high_atpo) & (~labeled_autoimmune)
print("Rows with low TSH (< 0.4) and normal Anti-TPO:", low_tsh.sum())
