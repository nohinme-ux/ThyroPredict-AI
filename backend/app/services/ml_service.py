import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from backend.app.core.config import settings

class MLService:
    def __init__(self):
        self.sts_model = None
        self.sts_meta = None
        self.uci_model = None
        self.uci_meta = None
        self.load_models()

    def load_models(self):
        sts_model_path = os.path.join(settings.ARTIFACTS_DIR, "sts_decision_tree_v1.joblib")
        sts_meta_path = os.path.join(settings.ARTIFACTS_DIR, "sts_model_metadata.json")
        if os.path.exists(sts_model_path) and os.path.exists(sts_meta_path):
            self.sts_model = joblib.load(sts_model_path)
            with open(sts_meta_path, "r", encoding="utf-8") as f:
                self.sts_meta = json.load(f)
            print(f"[MLService] Loaded STS Clinical Model v{self.sts_meta.get('version')}")
        else:
            print(f"[MLService] Warning: STS model artifact not found at {sts_model_path}")

        uci_model_path = os.path.join(settings.ARTIFACTS_DIR, "uci_decision_tree_v1.joblib")
        uci_meta_path = os.path.join(settings.ARTIFACTS_DIR, "uci_model_metadata.json")
        if os.path.exists(uci_model_path) and os.path.exists(uci_meta_path):
            self.uci_model = joblib.load(uci_model_path)
            with open(uci_meta_path, "r", encoding="utf-8") as f:
                self.uci_meta = json.load(f)
            print(f"[MLService] Loaded UCI Benchmark Model v{self.uci_meta.get('version')}")
        else:
            print(f"[MLService] Warning: UCI model artifact not found at {uci_model_path}")

    def _extract_decision_rules(self, pipeline, sample_df: pd.DataFrame, feature_names: List[str]) -> List[str]:
        """Traverse the decision tree decision path for this individual sample to produce plain-language explanation rules."""
        preprocessor = pipeline.named_steps["preprocessor"]
        clf = pipeline.named_steps["classifier"]

        transformed = preprocessor.transform(sample_df)
        node_indicator = clf.decision_path(transformed)
        node_index = node_indicator.indices[node_indicator.indptr[0]:node_indicator.indptr[1]]

        rules = []
        feature_indices = clf.tree_.feature
        thresholds = clf.tree_.threshold

        for node_id in node_index:
            feat_idx = feature_indices[node_id]
            if feat_idx != -2:  # Not a leaf
                feat_name = feature_names[feat_idx] if feat_idx < len(feature_names) else f"Feature_{feat_idx}"
                threshold = thresholds[node_id]
                val = transformed[0, feat_idx]
                
                if val <= threshold:
                    rules.append(f"Decision Node {node_id}: {feat_name} ({val:.2f}) <= threshold {threshold:.2f} -> Branch Left")
                else:
                    rules.append(f"Decision Node {node_id}: {feat_name} ({val:.2f}) > threshold {threshold:.2f} -> Branch Right")

        return rules

    def predict_sts(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.sts_model:
            raise RuntimeError("STS Clinical Model is not loaded. Train the model artifact first.")

        # Re-map key names if needed (e.g. Anti_tpo to Anti tpo)
        cleaned = dict(feature_data)
        if "Anti_tpo" in cleaned and "Anti tpo" not in cleaned:
            cleaned["Anti tpo"] = cleaned.pop("Anti_tpo")

        features_order = [
            "AGE", "DURATION", "HGT", "WGT", "bmi", "SYS", "DIA", "FBS",
            "FT3", "FT4", "TSH", "Anti tpo", "Visfatin", "Thyroglobulin",
            "IL6", "TCHOL", "TGL", "HDL", "LDL", "HB", "WBC", "PLT", "SEX"
        ]
        
        row_dict = {f: cleaned.get(f, np.nan) for f in features_order}
        sample_df = pd.DataFrame([row_dict])

        predicted_class = self.sts_model.predict(sample_df)[0]
        probabilities = self.sts_model.predict_proba(sample_df)[0]
        classes = list(self.sts_model.named_steps["classifier"].classes_)
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probabilities)}

        all_transformed_features = self.sts_meta.get("features", {}).get("all_transformed", [])
        rules = self._extract_decision_rules(self.sts_model, sample_df, all_transformed_features)

        return {
            "model_name": "STS Clinical Decision Tree",
            "model_id": "sts_clinical",
            "model_version": self.sts_meta.get("version", "1.0.0"),
            "predicted_class": predicted_class,
            "class_probabilities": prob_dict,
            "explanation_rules": rules,
            "feature_importances": self.sts_meta.get("feature_importances", [])[:8],
            "limitations": self.sts_meta.get("limitations", [])
        }

    def predict_uci(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.uci_model:
            raise RuntimeError("UCI Benchmark Model is not loaded. Train the model artifact first.")

        cleaned = dict(feature_data)
        features_order = [
            "age", "TSH", "T3", "TT4", "T4U", "FTI",
            "on_thyroxine", "query_on_thyroxine", "on_antithyroid_medication",
            "sick", "pregnant", "thyroid_surgery", "I131_treatment",
            "query_hypothyroid", "query_hyperthyroid", "lithium", "goitre",
            "tumor", "hypopituitary", "psych", "sex"
        ]

        row_dict = {}
        for f in features_order:
            val = cleaned.get(f)
            if isinstance(val, bool):
                val = 1 if val else 0
            row_dict[f] = val

        sample_df = pd.DataFrame([row_dict])

        predicted_class = self.uci_model.predict(sample_df)[0]
        probabilities = self.uci_model.predict_proba(sample_df)[0]
        classes = list(self.uci_model.named_steps["classifier"].classes_)
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probabilities)}

        all_transformed_features = self.uci_meta.get("features", {}).get("all_transformed", [])
        rules = self._extract_decision_rules(self.uci_model, sample_df, all_transformed_features)

        return {
            "model_name": "UCI Benchmark Decision Tree",
            "model_id": "uci_benchmark",
            "model_version": self.uci_meta.get("version", "1.0.0"),
            "predicted_class": predicted_class,
            "class_probabilities": prob_dict,
            "explanation_rules": rules,
            "feature_importances": self.uci_meta.get("feature_importances", [])[:8],
            "limitations": self.uci_meta.get("limitations", [])
        }

ml_service = MLService()
