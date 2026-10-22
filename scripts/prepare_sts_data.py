import pandas as pd
import numpy as np
import json
import os

excel_path = "data/sts thyroid data.xlsx"

# Sheet 1 has the primary clinical cohort
df1 = pd.read_excel(excel_path, sheet_name="Sheet1")
# Sheet 3 has additional control subjects labeled 'C' in DURATION
df3 = pd.read_excel(excel_path, sheet_name="Sheet3")

# Filter valid patient records from Sheet 1
sheet1_valid = df1[df1['NAME'].notna()].copy()

def clean_val(v):
    if pd.isna(v):
        return np.nan
    s = str(v).strip().replace('<', '').replace('>', '').replace('#VALUE!', '').replace('#REF!', '')
    if '/' in s and len(s.split('/')) == 2:
        try:
            parts = s.split('/')
            return float(parts[0]) / float(parts[1]) if float(parts[1]) != 0 else float(parts[0])
        except:
            return np.nan
    try:
        return float(s)
    except:
        return np.nan

# Clean numeric columns in Sheet 1
num_cols = [
    'AGE', 'DURATION', 'HGT', 'WGT', 'bmi', 'SYS', 'DIA', 'FBS',
    'FT3', 'FT4', 'TSH', 'Thyrotroph T4 Resistance Index', 'Anti tpo',
    'Visfatin', 'Thyroglobulin', 'IL6', 'TCHOL', 'TGL', 'HDL', 'LDL',
    'VLDL', 'Calcium', 'Phos', 'HB', 'RBC', 'HCT', 'MCV', 'MCH',
    'MCHC', 'RDW', 'WBC', 'N', 'L', 'M', 'E', 'B', 'PLT', 'UREA', 'CREAT'
]

for col in num_cols:
    if col in sheet1_valid.columns:
        sheet1_valid[col] = sheet1_valid[col].apply(clean_val)

# Normalize SEX
sheet1_valid['SEX'] = sheet1_valid['SEX'].astype(str).str.strip().str.upper()
sheet1_valid['SEX'] = sheet1_valid['SEX'].map({'F': 'F', 'M': 'M'}).fillna('F')

# Define target:
# 1. Autoimmune Thyroid Disease: labeled autoimmune/graves/thyroiditis OR Anti-TPO >= 34.0
# 2. Primary Hypothyroidism: TSH > 5.0 and Anti-TPO < 34.0
# 3. Euthyroid / Normal: TSH between 0.4 and 5.0 and Anti-TPO < 34.0
# 4. Hyperthyroid: TSH < 0.4 and Anti-TPO < 34.0

def assign_sts_class(row):
    label_txt = str(row.get('Unnamed: 20', '')).lower()
    atpo = row.get('Anti tpo', np.nan)
    tsh = row.get('TSH', np.nan)
    
    if any(k in label_txt for k in ['auto immune', 'graves', 'thyroiditis']) or (pd.notna(atpo) and atpo >= 34.0):
        return 'Autoimmune Thyroid Disease'
    elif pd.notna(tsh) and tsh > 5.0:
        return 'Primary Hypothyroidism'
    elif pd.notna(tsh) and tsh < 0.4:
        return 'Hyperthyroid'
    else:
        return 'Euthyroid / Normal'

sheet1_valid['target'] = sheet1_valid.apply(assign_sts_class, axis=1)

# Add controls from Sheet 3 that are not in Sheet 1
controls_sheet3 = df3[df3['DURATION'] == 'C'].copy()
control_records = []
existing_names = set(sheet1_valid['NAME'].astype(str).str.lower().str.strip())

for idx, r in controls_sheet3.iterrows():
    name = str(r['NAME']).strip()
    if name.lower() not in existing_names:
        row_dict = {
            'NAME': f"Ctrl_{name}",
            'AGE': clean_val(r.get('AGE')),
            'SEX': 'F' if str(r.get('SEX')).strip().upper().startswith('F') else 'M',
            'DURATION': 0.0,
            'FT3': clean_val(r.get('FT3')),
            'FT4': clean_val(r.get('FT4')),
            'TSH': clean_val(r.get('TSH')),
            'Anti tpo': clean_val(r.get('Anti tpo')),
            'FBS': clean_val(r.get('FBS')),
            'Visfatin': clean_val(r.get('Visfatin')),
            'Thyroglobulin': clean_val(r.get('Thyroglobulin')),
            'IL6': clean_val(r.get('IL6')),
            'TCHOL': clean_val(r.get('TCHOL')),
            'TGL': clean_val(r.get('TGL')),
            'HDL': clean_val(r.get('HDL')),
            'LDL': clean_val(r.get('LDL')),
            'VLDL': clean_val(r.get('VLDL')),
            'target': 'Euthyroid / Normal'
        }
        control_records.append(row_dict)

if control_records:
    ctrl_df = pd.DataFrame(control_records)
    combined_sts = pd.concat([sheet1_valid, ctrl_df], ignore_index=True)
else:
    combined_sts = sheet1_valid.copy()

print(f"Total STS records: {len(combined_sts)}")
print("STS Class distribution:")
print(combined_sts['target'].value_counts())

# Save clean STS dataset
out_path = "data/sts_cleaned.csv"
combined_sts.to_csv(out_path, index=False)
print(f"Saved {out_path} successfully.")
