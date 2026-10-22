import requests
import io
import pandas as pd

# UCI Thyroid Disease dataset URL from UCI ML repo / archive
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/thyroid-disease/allhypo.data"
try:
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        print("Successfully downloaded UCI allhypo.data! Length:", len(resp.text))
        lines = resp.text.strip().split('\n')
        print("First line:", lines[0])
        print("Total samples:", len(lines))
    else:
        print("Failed to download UCI dataset, status:", resp.status_code)
except Exception as e:
    print("Error downloading UCI dataset:", e)
