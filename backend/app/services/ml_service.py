import os
import json
from typing import Dict, Any, List, Tuple
from backend.app.core.config import settings

try:
    import joblib
    import pandas as pd
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

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
        
        if os.path.exists(sts_meta_path):
            with open(sts_meta_path, "r", encoding="utf-8") as f:
                self.sts_meta = json.load(f)
            if HAS_SKLEARN and os.path.exists(sts_model_path):
                self.sts_model = joblib.load(sts_model_path)
                print(f"[MLService] Loaded STS Clinical Model pipeline v{self.sts_meta.get('version')}")
            else:
                self.sts_model = "native_tree_v1"
                print(f"[MLService] Loaded STS Clinical Native Decision Tree v{self.sts_meta.get('version')}")
        else:
            print(f"[MLService] Warning: STS metadata not found at {sts_meta_path}")

        uci_model_path = os.path.join(settings.ARTIFACTS_DIR, "uci_decision_tree_v1.joblib")
        uci_meta_path = os.path.join(settings.ARTIFACTS_DIR, "uci_model_metadata.json")

        if os.path.exists(uci_meta_path):
            with open(uci_meta_path, "r", encoding="utf-8") as f:
                self.uci_meta = json.load(f)
            if HAS_SKLEARN and os.path.exists(uci_model_path):
                self.uci_model = joblib.load(uci_model_path)
                print(f"[MLService] Loaded UCI Benchmark Model pipeline v{self.uci_meta.get('version')}")
            else:
                self.uci_model = "native_tree_v1"
                print(f"[MLService] Loaded UCI Benchmark Native Decision Tree v{self.uci_meta.get('version')}")
        else:
            print(f"[MLService] Warning: UCI metadata not found at {uci_meta_path}")

    def _extract_decision_rules_sklearn(self, pipeline, sample_df, feature_names: List[str]) -> List[str]:
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
            if feat_idx != -2:
                feat_name = feature_names[feat_idx] if feat_idx < len(feature_names) else f"Feature_{feat_idx}"
                threshold = thresholds[node_id]
                val = transformed[0, feat_idx]
                
                if val <= threshold:
                    rules.append(f"Decision Node {node_id}: {feat_name} ({val:.2f}) <= threshold {threshold:.2f} -> Branch Left")
                else:
                    rules.append(f"Decision Node {node_id}: {feat_name} ({val:.2f}) > threshold {threshold:.2f} -> Branch Right")

        return rules

    def _native_predict_sts(self, feature_data: Dict[str, Any]) -> Tuple[str, Dict[str, float], List[str]]:
        cleaned = dict(feature_data)
        anti_tpo = float(cleaned.get("Anti tpo") if "Anti tpo" in cleaned else cleaned.get("Anti_tpo", 0.0))
        tsh = float(cleaned.get("TSH", 0.0))

        rules = []
        if anti_tpo > 37.5:
            rules.append(f"Decision Node 0: Anti tpo ({anti_tpo:.2f}) > threshold 37.50 -> Branch Right")
            pred_class = "Autoimmune Thyroid Disease"
            probs = {
                "Autoimmune Thyroid Disease": 1.0,
                "Euthyroid / Normal": 0.0,
                "Hyperthyroid": 0.0,
                "Primary Hypothyroidism": 0.0
            }
            return pred_class, probs, rules

        rules.append(f"Decision Node 0: Anti tpo ({anti_tpo:.2f}) <= threshold 37.50 -> Branch Left")
        if tsh <= 0.5815:
            rules.append(f"Decision Node 1: TSH ({tsh:.2f}) <= threshold 0.58 -> Branch Left")
            pred_class = "Hyperthyroid"
            probs = {
                "Autoimmune Thyroid Disease": 0.0,
                "Euthyroid / Normal": 0.0,
                "Hyperthyroid": 1.0,
                "Primary Hypothyroidism": 0.0
            }
            return pred_class, probs, rules

        rules.append(f"Decision Node 1: TSH ({tsh:.2f}) > threshold 0.58 -> Branch Right")
        if tsh > 5.165:
            rules.append(f"Decision Node 3: TSH ({tsh:.2f}) > threshold 5.16 -> Branch Right")
            pred_class = "Primary Hypothyroidism"
            probs = {
                "Autoimmune Thyroid Disease": 0.0,
                "Euthyroid / Normal": 0.0,
                "Hyperthyroid": 0.0,
                "Primary Hypothyroidism": 1.0
            }
            return pred_class, probs, rules

        rules.append(f"Decision Node 3: TSH ({tsh:.2f}) <= threshold 5.16 -> Branch Left")
        if tsh <= 0.9253:
            rules.append(f"Decision Node 4: TSH ({tsh:.2f}) <= threshold 0.93 -> Branch Left")
        else:
            rules.append(f"Decision Node 4: TSH ({tsh:.2f}) > threshold 0.93 -> Branch Right")

        pred_class = "Euthyroid / Normal"
        probs = {
            "Autoimmune Thyroid Disease": 0.0,
            "Euthyroid / Normal": 1.0,
            "Hyperthyroid": 0.0,
            "Primary Hypothyroidism": 0.0
        }
        return pred_class, probs, rules

    def _native_predict_uci(self, feature_data: Dict[str, Any]) -> Tuple[str, Dict[str, float], List[str]]:
        cleaned = dict(feature_data)
        tsh = float(cleaned.get("TSH", 0.0) if cleaned.get("TSH") is not None else 1.5)
        fti = float(cleaned.get("FTI", 0.0) if cleaned.get("FTI") is not None else 105.0)
        tt4 = float(cleaned.get("TT4", 0.0) if cleaned.get("TT4") is not None else 108.0)
        t3 = float(cleaned.get("T3", 0.0) if cleaned.get("T3") is not None else 2.0)
        age = float(cleaned.get("age", 0.0) if cleaned.get("age") is not None else 50.0)
        
        on_thyroxine = 1.0 if cleaned.get("on_thyroxine") in [1, True, "t"] else 0.0
        thyroid_surgery = 1.0 if cleaned.get("thyroid_surgery") in [1, True, "t"] else 0.0
        sex_m = 1.0 if cleaned.get("sex") in ["M", "m", 1] else 0.0

        rules = []
        if tsh <= 6.05:
            rules.append(f"Decision Node 0: TSH ({tsh:.2f}) <= threshold 6.05 -> Branch Left")
            return "negative", {"compensated hypothyroid": 0.0, "negative": 1.0, "primary hypothyroid": 0.0}, rules

        rules.append(f"Decision Node 0: TSH ({tsh:.2f}) > threshold 6.05 -> Branch Right")
        if fti <= 64.5:
            rules.append(f"Decision Node 2: FTI ({fti:.2f}) <= threshold 64.50 -> Branch Left")
            if thyroid_surgery <= 0.5:
                rules.append(f"Decision Node 3: thyroid_surgery ({thyroid_surgery:.1f}) <= threshold 0.50 -> Branch Left")
                if t3 <= 2.25:
                    rules.append(f"Decision Node 4: T3 ({t3:.2f}) <= threshold 2.25 -> Branch Left")
                else:
                    rules.append(f"Decision Node 4: T3 ({t3:.2f}) > threshold 2.25 -> Branch Right")
            else:
                rules.append(f"Decision Node 3: thyroid_surgery ({thyroid_surgery:.1f}) > threshold 0.50 -> Branch Right")
            return "primary hypothyroid", {"compensated hypothyroid": 0.0, "negative": 0.0, "primary hypothyroid": 1.0}, rules

        rules.append(f"Decision Node 2: FTI ({fti:.2f}) > threshold 64.50 -> Branch Right")
        if tt4 <= 59.0:
            rules.append(f"Decision Node 8: TT4 ({tt4:.2f}) <= threshold 59.00 -> Branch Left")
            return "primary hypothyroid", {"compensated hypothyroid": 0.12, "negative": 0.01, "primary hypothyroid": 0.87}, rules

        rules.append(f"Decision Node 8: TT4 ({tt4:.2f}) > threshold 59.00 -> Branch Right")
        if age <= 6.0:
            rules.append(f"Decision Node 10: age ({age:.1f}) <= threshold 6.00 -> Branch Left")
            return "primary hypothyroid", {"compensated hypothyroid": 0.29, "negative": 0.01, "primary hypothyroid": 0.70}, rules

        rules.append(f"Decision Node 10: age ({age:.1f}) > threshold 6.00 -> Branch Right")
        if on_thyroxine <= 0.5:
            rules.append(f"Decision Node 12: on_thyroxine ({on_thyroxine:.1f}) <= threshold 0.50 -> Branch Left")
            if thyroid_surgery <= 0.5:
                rules.append(f"Decision Node 13: thyroid_surgery ({thyroid_surgery:.1f}) <= threshold 0.50 -> Branch Left")
                return "compensated hypothyroid", {"compensated hypothyroid": 0.98, "negative": 0.0, "primary hypothyroid": 0.02}, rules
            else:
                rules.append(f"Decision Node 13: thyroid_surgery ({thyroid_surgery:.1f}) > threshold 0.50 -> Branch Right")
                return "negative", {"compensated hypothyroid": 0.0, "negative": 1.0, "primary hypothyroid": 0.0}, rules
        else:
            rules.append(f"Decision Node 12: on_thyroxine ({on_thyroxine:.1f}) > threshold 0.50 -> Branch Right")
            if sex_m <= 0.5:
                rules.append(f"Decision Node 16: sex_M ({sex_m:.1f}) <= threshold 0.50 -> Branch Left")
            else:
                rules.append(f"Decision Node 16: sex_M ({sex_m:.1f}) > threshold 0.50 -> Branch Right")
            return "negative", {"compensated hypothyroid": 0.0, "negative": 1.0, "primary hypothyroid": 0.0}, rules

    def predict_sts(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.sts_model:
            raise RuntimeError("STS Clinical Model is not loaded. Train the model artifact first.")

        if HAS_SKLEARN and not isinstance(self.sts_model, str):
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
            rules = self._extract_decision_rules_sklearn(self.sts_model, sample_df, all_transformed_features)
        else:
            predicted_class, prob_dict, rules = self._native_predict_sts(feature_data)

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

        if HAS_SKLEARN and not isinstance(self.uci_model, str):
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
            rules = self._extract_decision_rules_sklearn(self.uci_model, sample_df, all_transformed_features)
        else:
            predicted_class, prob_dict, rules = self._native_predict_uci(feature_data)

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
