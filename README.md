# ThyroPredict AI — Decision Tree Based Thyroid Disease Research and Prediction System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-Research_Only-amber.svg)]()

> **RESEARCH DISCLAIMER**: This application is built strictly for investigational machine-learning research and educational decision-support analysis. Model outputs are probabilistic research screening predictions, **not confirmed medical diagnoses**. This software is not an FDA, CE, or CDSCO-cleared medical device and must never be used as the sole basis for prescribing medication or clinical interventions.

---

## 1. System Overview

**ThyroPredict AI** is an end-to-end clinical research platform that connects an interactive, responsive web portal to genuine, version-controlled **Decision Tree machine-learning models** trained on real thyroid patient cohorts.

### Core Capabilities:
- **Authentic ML Pipeline**: Powered by `scikit-learn` `DecisionTreeClassifier` with stratified train/validation/test isolation, hyperparameter pruning, and balanced class weights.
- **Dual Model Architecture**:
  1. **STS Clinical Model (Primary)**: Trained on the user's clinical cohort (`sts thyroid data.xlsx`), utilizing 22 high-yield laboratory parameters including Free T3, Free T4, TSH, Anti-TPO autoantibodies, Visfatin, IL-6, Thyroglobulin, Lipids, and CBC. **Held-out Test Accuracy: 94.44%, Balanced Accuracy: 94.87%, Macro-F1: 91.98%**.
  2. **UCI Benchmark Model (Alternate)**: Trained on the official UCI Machine Learning Repository Garavan Institute dataset (`allhypo.data` / `allhypo.test`, 3,772 records). **Held-out Test Accuracy: 99.07%, Macro-F1: 95.04%**.
- **Decision Path Explainability**: Decodes node inequality thresholds (`feat <= threshold` vs `feat > threshold`) directly from the fitted tree for every individual patient inference.
- **Persistent Relational Database**: SQLite (with PostgreSQL compatibility) via SQLAlchemy storing participant registry, submitted features, predicted condition, leaf probabilities, decision rules, and timestamps.
- **De-Identified Audit Trail & Export**: Research participant codes (e.g., `THYRO-PART-001`) with one-click anonymized CSV export for institutional audits.

---

## 2. Technology Stack

### Frontend:
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom medical theme tokens (Deep Navy `#0F172A`, Sky `#0284C7`, Clinical Neutral `#F8FAFC`)
- **Icons**: Lucide React
- **Analytics Charts**: Recharts (Donut distributions, Confusion Matrix heatmaps, Feature importance bar charts)

### Backend:
- **API Framework**: FastAPI + Uvicorn
- **Validation**: Pydantic v2 schemas
- **Database**: SQLite / SQLAlchemy 2.0 ORM
- **Machine Learning**: scikit-learn, NumPy, pandas, openpyxl, joblib
- **Security**: Bcrypt password hashing + PyJWT Bearer authentication

---

## 3. Dataset Profiling & Attribution

### A. STS Clinical Thyroid Study Dataset (`data/sts_cleaned.csv`):
- **Source**: ICMR STS Clinical Thyroid Investigation Cohort (`sts thyroid data.xlsx`)
- **Sample Count**: 269 records (215 train, 54 held-out test)
- **Key Parameters**:
  - `TSH` (Thyroid Stimulating Hormone, Ref: 0.40 - 4.50 uIU/mL)
  - `FT4` (Free Thyroxine, Ref: 0.80 - 1.80 ng/dL)
  - `FT3` (Free Triiodothyronine, Ref: 2.00 - 4.40 pg/mL)
  - `Anti tpo` (Anti-Thyroid Peroxidase, Normal < 34.0 IU/mL; primary autoimmune indicator)
  - `Visfatin` (Adipocytokine biomarker, ng/mL)
  - `IL6` (Interleukin-6 systemic inflammation marker, pg/mL)
  - `Thyroglobulin` (Serum protein marker, ng/mL)
  - `Lipid Panel` (Total Cholesterol, Triglycerides, HDL, LDL)
  - `CBC` (Hemoglobin, WBC, Platelets)
- **Diagnostic Classes**:
  - `Euthyroid / Normal` (128 cases): Normal TSH/FT4 with negative autoantibodies.
  - `Autoimmune Thyroid Disease` (60 cases): High Anti-TPO (>= 34 IU/mL) / Hashimoto's / Graves'.
  - `Primary Hypothyroidism` (56 cases): Elevated TSH (> 5.0 uIU/mL) with negative Anti-TPO.
  - `Hyperthyroid` (25 cases): Suppressed TSH (< 0.40 uIU/mL).

### B. UCI Benchmark Dataset (`data/uci_train.csv`, `data/uci_test.csv`):
- **Source**: UCI Machine Learning Repository / Garavan Institute (Sydney, Australia)
- **Sample Count**: 3,772 total (2,800 train, 972 official held-out test)
- **Diagnostic Classes**: `negative` (euthyroid), `compensated hypothyroid`, `primary hypothyroid`.

---

## 4. Model Training & Evaluation Metrics

All models were evaluated strictly on held-out test sets without data leakage:

### STS Clinical Decision Tree Model:
| Metric | Held-Out Test Value | Notes |
| :--- | :--- | :--- |
| **Test Accuracy** | **94.44%** | Evaluated on 54 held-out test subjects |
| **Balanced Accuracy** | **94.87%** | Equal weighting across all 4 classes |
| **Macro F1-Score** | **91.98%** | Robust harmonic mean across classes |
| **Weighted F1-Score** | **94.40%** | Weighted by class support |
| **5-Fold CV Macro F1** | **1.0000** | Cross-validation on training split |
| **Tree Depth / Leaves** | **5 / 9** | Pruned to prevent memorization (`min_samples_leaf=3`) |

#### STS Confusion Matrix (Test Split N=54):
```
Actual \ Predicted               Autoimmune   Euthyroid   Hyper   Hypothyroid
Autoimmune Thyroid Disease          10            0          1         1
Euthyroid / Normal                   0           25          1         0
Hyperthyroid                         0            0          5         0
Primary Hypothyroidism               0            0          0        11
```

---

## 5. Quickstart — Running Locally

### Prerequisites:
- Python 3.10+ (Anaconda Python 3.12 verified)
- Node.js 18+ (Node v22.17 verified) & npm

### Step 1: Clone & Install Backend Dependencies
```bash
# In project root
pip install -r backend/requirements.txt
```

### Step 2: Retrain or Verify ML Models (Optional)
```bash
python scripts/train_sts_model.py
python scripts/train_uci_model.py
python scripts/evaluate_models.py
```

### Step 3: Run Backend API Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- Interactive Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Status: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Step 4: Run Frontend Dev Server
In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
- Access Portal: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## 6. Automated Testing

Run the automated pytest suite:
```bash
python -m pytest backend/tests -v
```
**Test Results: 12 / 12 PASSED**
- `test_health_check`: Verifies API alive & models loaded
- `test_model_info` & `test_model_metrics`: Verifies genuine test metrics
- `test_participants_crud_and_prediction_flow`: End-to-end integration test
- `test_overview_stats` & `test_dataset_summary`: Analytics verification
- `test_auth_workflow`: Password hashing & JWT generation
- `test_sts_model_loaded` & `test_uci_model_loaded`: Artifact integrity
- `test_sts_prediction_inference` & `test_sts_autoimmune_inference`: Inference validation
- `test_uci_prediction_inference`: Benchmark inference

---

## 7. Production Deployment via Docker

Run the entire full-stack system with a single command:
```bash
docker-compose up --build -d
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## 8. Clinical Research Notice

1. **Assay Variation**: Anti-TPO and free hormone immunoassays vary across commercial diagnostic platforms (ECLIA vs CMIA). Cut-offs should be aligned with your institution's specific clinical laboratory reference standards.
2. **Clinical Decision Support**: Machine learning predictions should only be used in conjunction with a patient's history, physical examination, and ultrasound/cytological findings.
