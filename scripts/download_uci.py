import requests
import os
import pandas as pd
import json

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

UCI_COLUMNS = [
    "age", "sex", "on_thyroxine", "query_on_thyroxine", "on_antithyroid_medication",
    "sick", "pregnant", "thyroid_surgery", "I131_treatment", "query_hypothyroid",
    "query_hyperthyroid", "lithium", "goitre", "tumor", "hypopituitary",
    "psych", "TSH_measured", "TSH", "T3_measured", "T3",
    "TT4_measured", "TT4", "T4U_measured", "T4U", "FTI_measured",
    "FTI", "TBG_measured", "TBG", "referral_source", "target"
]

files = {
    "uci_allhypo.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/thyroid-disease/allhypo.data",
    "uci_allhypo.test": "https://archive.ics.uci.edu/ml/machine-learning-databases/thyroid-disease/allhypo.test",
    "uci_allhypo.names": "https://archive.ics.uci.edu/ml/machine-learning-databases/thyroid-disease/allhypo.names"
}

for fname, url in files.items():
    dest = os.path.join(data_dir, fname)
    print(f"Fetching {url} -> {dest}...")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"Saved {fname} ({len(r.text)} bytes)")
        else:
            print(f"HTTP error {r.status_code} for {fname}")
    except Exception as e:
        print(f"Failed to download {fname}: {e}")

def parse_uci_file(filepath):
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) >= 30:
                # target is formatted like 'negative.|3733' or 'primary hypothyroid.|1024'
                raw_target = parts[29]
                target_clean = raw_target.split(".")[0].strip()
                row = parts[:29] + [target_clean]
                rows.append(row)
    return pd.DataFrame(rows, columns=UCI_COLUMNS)

train_df = parse_uci_file(os.path.join(data_dir, "uci_allhypo.data"))
test_df = parse_uci_file(os.path.join(data_dir, "uci_allhypo.test"))

print(f"UCI Train shape: {train_df.shape}")
print(f"UCI Test shape: {test_df.shape}")
print("UCI Train target distribution:")
print(train_df["target"].value_counts())
print("\nUCI Test target distribution:")
print(test_df["target"].value_counts())

train_df.to_csv(os.path.join(data_dir, "uci_train.csv"), index=False)
test_df.to_csv(os.path.join(data_dir, "uci_test.csv"), index=False)
print("Saved parsed UCI CSVs successfully.")
