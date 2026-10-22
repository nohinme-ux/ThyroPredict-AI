import json

dictionary = {
    "sts_clinical_dataset": {
        "title": "STS Clinical Thyroid Study Dataset",
        "source": "ICMR STS Clinical Thyroid Investigation Cohort (sts thyroid data.xlsx)",
        "description": "Comprehensive clinical cohort containing endocrinological parameters, autoimmune titers (Anti-TPO), inflammatory markers (IL-6), adipokines (Visfatin), lipid panels, and complete blood counts for thyroid disease research.",
        "sample_count": 269,
        "classes": {
            "Euthyroid / Normal": "Healthy reference state with normal pituitary-thyroid axis (TSH 0.4–4.5 uIU/mL, normal FT4/FT3) and negative anti-thyroid autoantibodies.",
            "Primary Hypothyroidism": "Elevated serum TSH (>5.0 uIU/mL) reflecting thyroid gland underactivity without elevated autoimmune antibody titers.",
            "Autoimmune Thyroid Disease": "High anti-thyroid peroxidase antibody titers (Anti-TPO >= 34 IU/mL) characteristic of autoimmune thyroiditis (Hashimoto's disease) or Graves' pathology.",
            "Hyperthyroid": "Suppressed serum TSH (<0.4 uIU/mL) indicating thyroid hormone excess/hyperactivity."
        },
        "features": [
            {"name": "AGE", "type": "numerical", "unit": "years", "range": "18 - 85", "description": "Patient age in completed years"},
            {"name": "SEX", "type": "categorical", "options": ["F", "M"], "description": "Biological sex"},
            {"name": "TSH", "type": "numerical", "unit": "uIU/mL", "normal_range": "0.40 - 4.50", "description": "Thyroid Stimulating Hormone"},
            {"name": "FT3", "type": "numerical", "unit": "pg/mL", "normal_range": "2.00 - 4.40", "description": "Free Triiodothyronine"},
            {"name": "FT4", "type": "numerical", "unit": "ng/dL", "normal_range": "0.80 - 1.80", "description": "Free Thyroxine"},
            {"name": "Anti tpo", "type": "numerical", "unit": "IU/mL", "normal_range": "< 34.0", "description": "Anti-Thyroid Peroxidase Antibody titer"},
            {"name": "Thyroglobulin", "type": "numerical", "unit": "ng/mL", "normal_range": "1.4 - 78.0", "description": "Serum Thyroglobulin protein"},
            {"name": "Visfatin", "type": "numerical", "unit": "ng/mL", "normal_range": "10.0 - 50.0", "description": "NAMPT/Visfatin adipocytokine biomarker"},
            {"name": "IL6", "type": "numerical", "unit": "pg/mL", "normal_range": "< 7.0", "description": "Interleukin-6 systemic inflammatory cytokine"},
            {"name": "bmi", "type": "numerical", "unit": "kg/m^2", "normal_range": "18.5 - 24.9", "description": "Body Mass Index calculated from weight/height"},
            {"name": "SYS", "type": "numerical", "unit": "mmHg", "normal_range": "90 - 120", "description": "Systolic blood pressure"},
            {"name": "DIA", "type": "numerical", "unit": "mmHg", "normal_range": "60 - 80", "description": "Diastolic blood pressure"},
            {"name": "FBS", "type": "numerical", "unit": "mg/dL", "normal_range": "70 - 100", "description": "Fasting Blood Sugar"},
            {"name": "TCHOL", "type": "numerical", "unit": "mg/dL", "normal_range": "< 200", "description": "Total serum cholesterol"},
            {"name": "TGL", "type": "numerical", "unit": "mg/dL", "normal_range": "< 150", "description": "Triglycerides"},
            {"name": "HDL", "type": "numerical", "unit": "mg/dL", "normal_range": "40 - 60", "description": "High-Density Lipoprotein ('good cholesterol')"},
            {"name": "LDL", "type": "numerical", "unit": "mg/dL", "normal_range": "< 100", "description": "Low-Density Lipoprotein ('bad cholesterol')"},
            {"name": "HB", "type": "numerical", "unit": "g/dL", "normal_range": "12.0 - 16.0", "description": "Hemoglobin concentration"},
            {"name": "WBC", "type": "numerical", "unit": "cells/uL", "normal_range": "4000 - 11000", "description": "Total White Blood Cell count"},
            {"name": "PLT", "type": "numerical", "unit": "x10^3/uL", "normal_range": "150 - 450", "description": "Platelet count"}
        ]
    },
    "uci_benchmark_dataset": {
        "title": "UCI Thyroid Disease Benchmark Dataset",
        "source": "UCI Machine Learning Repository / Garavan Institute (Sydney, Australia)",
        "description": "Standard international benchmark dataset for thyroid classification containing clinical queries, thyroxine medications, and radioimmunoassay laboratory results.",
        "sample_count": 3772,
        "train_samples": 2800,
        "test_samples": 972,
        "classes": {
            "negative": "Patient does not exhibit hypothyroid condition (euthyroid baseline).",
            "compensated hypothyroid": "Early or mild thyroid underactivity where elevated TSH compensates to keep thyroxine (TT4/FTI) within normal limits.",
            "primary hypothyroid": "Overt clinical hypothyroidism with elevated TSH and deficient circulating thyroid hormone."
        },
        "features": [
            {"name": "age", "type": "numerical", "unit": "years", "description": "Patient age"},
            {"name": "sex", "type": "categorical", "options": ["F", "M"], "description": "Biological sex"},
            {"name": "on_thyroxine", "type": "boolean", "description": "Whether patient is actively prescribed thyroxine hormone"},
            {"name": "query_on_thyroxine", "type": "boolean", "description": "Query regarding thyroxine status"},
            {"name": "on_antithyroid_medication", "type": "boolean", "description": "Antithyroid drug treatment (e.g., methimazole/PTU)"},
            {"name": "sick", "type": "boolean", "description": "Presence of concurrent non-thyroidal systemic illness"},
            {"name": "pregnant", "type": "boolean", "description": "Pregnancy status"},
            {"name": "thyroid_surgery", "type": "boolean", "description": "Prior thyroidectomy or partial resection"},
            {"name": "I131_treatment", "type": "boolean", "description": "Radioactive iodine-131 ablation therapy"},
            {"name": "query_hypothyroid", "type": "boolean", "description": "Clinical suspicion of hypothyroidism"},
            {"name": "query_hyperthyroid", "type": "boolean", "description": "Clinical suspicion of hyperthyroidism"},
            {"name": "lithium", "type": "boolean", "description": "Concurrent lithium therapy"},
            {"name": "goitre", "type": "boolean", "description": "Visible or palpable thyroid gland enlargement"},
            {"name": "tumor", "type": "boolean", "description": "Suspected or verified thyroid nodule or tumor"},
            {"name": "hypopituitary", "type": "boolean", "description": "Pituitary deficiency / hypopituitarism"},
            {"name": "psych", "type": "boolean", "description": "Psychiatric symptoms or medications"},
            {"name": "TSH", "type": "numerical", "unit": "uIU/mL", "description": "Thyroid Stimulating Hormone"},
            {"name": "T3", "type": "numerical", "unit": "nmol/L", "description": "Total Triiodothyronine"},
            {"name": "TT4", "type": "numerical", "unit": "nmol/L", "description": "Total Thyroxine"},
            {"name": "T4U", "type": "numerical", "unit": "ratio", "description": "Thyroxine Uptake ratio"},
            {"name": "FTI", "type": "numerical", "unit": "index", "description": "Free Thyroxine Index (TT4 / T4U)"}
        ]
    }
}

with open("data/dataset_dictionary.json", "w", encoding="utf-8") as f:
    json.dump(dictionary, f, indent=2)

print("Created data/dataset_dictionary.json successfully.")
