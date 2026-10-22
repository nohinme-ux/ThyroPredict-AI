export interface User {
  id: string;
  email: string;
  role: string;
  account_status: string;
  created_at: string;
}

export interface ResearchParticipant {
  id: string;
  research_participant_code: string;
  display_name?: string;
  age?: number;
  sex?: string;
  consent_status: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
  prediction_count?: number;
}

export interface Prediction {
  id: string;
  participant_id: string;
  participant_code?: string;
  display_name?: string;
  model_name: string;
  model_version: string;
  predicted_class: string;
  class_probabilities: Record<string, number>;
  explanation_rules: string[];
  feature_importances: Array<{ feature: string; importance: number }>;
  submitted_feature_values: Record<string, any>;
  prediction_timestamp: string;
  record_status: string;
}

export interface OverviewStats {
  total_participants: number;
  total_predictions: number;
  active_models_count: number;
  predicted_classes_breakdown: Record<string, number>;
  recent_predictions: Array<{
    id: string;
    participant_code: string;
    model_name: string;
    predicted_class: string;
    timestamp: string;
  }>;
  model_performance_summary: {
    sts_clinical: {
      version: string;
      accuracy: number;
      macro_f1: number;
      test_samples: number;
    };
    uci_benchmark: {
      version: string;
      accuracy: number;
      macro_f1: number;
      test_samples: number;
    };
  };
}

export interface ModelMetrics {
  model_id: string;
  version: string;
  algorithm: string;
  training_timestamp: string;
  dataset: {
    name: string;
    file?: string;
    fingerprint_md5: string;
    total_samples?: number;
    train_samples: number;
    test_samples: number;
    split_strategy: string;
  };
  hyperparameters: Record<string, any>;
  classes: string[];
  metrics: {
    accuracy: number;
    balanced_accuracy: number;
    macro_f1: number;
    weighted_f1: number;
    cross_val_macro_f1_mean?: number;
    cross_val_macro_f1_std?: number;
    confusion_matrix: {
      labels: string[];
      matrix: number[][];
    };
    per_class: Record<string, {
      precision: number;
      recall: number;
      f1_score: number;
      support: number;
    }>;
  };
  feature_importances: Array<{ feature: string; importance: number }>;
  tree_structure: {
    depth: number;
    n_leaves: number;
    rules_text: string;
  };
  limitations: string[];
}

export interface DatasetFeature {
  name: string;
  type: string;
  unit?: string;
  normal_range?: string;
  description: string;
  options?: string[];
}

export interface DatasetSummary {
  dictionary: {
    sts_clinical_dataset?: {
      title: string;
      source: string;
      description: string;
      sample_count: number;
      classes: Record<string, string>;
      features: DatasetFeature[];
    };
    uci_benchmark_dataset?: {
      title: string;
      source: string;
      description: string;
      sample_count: number;
      classes: Record<string, string>;
      features: DatasetFeature[];
    };
  };
  sts_stats: {
    total_records: number;
    class_distribution: Record<string, number>;
    numerical_summary: Record<string, {
      mean: number;
      std: number;
      min: number;
      max: number;
    }>;
  };
  uci_stats: {
    train_records: number;
    class_distribution: Record<string, number>;
  };
}
