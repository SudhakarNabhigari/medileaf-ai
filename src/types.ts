export type NavSection =
  | 'home'
  | 'identify'
  | 'results'
  | 'history'
  | 'analytics'
  | 'dataset'
  | 'settings';

export interface UserAccount {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface UserPreferences {
  theme: 'Light' | 'Dark' | 'System';
  notifications_enabled: boolean;
  save_history_enabled: boolean;
}

export interface PredictionRecord {
  id: number;
  user_id: number;
  filename: string;
  image_thumbnail_b64?: string | null;
  predicted_species: string;
  confidence: number | null;
  energy_score: number | null;
  status: 'Accepted' | 'Rejected';
  reason: string;
  created_at: string;
}

export interface PredictionResult {
  status: 'ACCEPTED' | 'UNCERTAIN' | 'MODEL_NOT_READY' | 'INVALID_IMAGE';
  accepted: boolean;
  predicted_species: string;
  raw_top_class?: string | null;
  confidence: number | null;
  energy_score: number | null;
  entropy?: number | null;
  threshold_used: number | null;
  gate_method: string | null;
  reason: string;
  top_k: Array<{ species: string; confidence: number }>;
  image_width?: number;
  image_height?: number;
}

export interface WorkspaceState {
  verifiedMendeleyMetadata: {
    dataset_name: string;
    source: string;
    record_id: string;
    version: string;
    doi: string;
    url: string;
    licence: string;
    contributors: string;
    poisonous_coverage_status: string;
  };
  checkpointExists: boolean;
  modelReady: boolean;
  datasetMeta: {
    valid_species_count?: number;
    valid_image_count?: number;
    total_files_scanned?: number;
    corrupted_count?: number;
    exact_duplicate_count?: number;
    class_imbalance_ratio?: number;
  } | null;
  classMapping: {
    num_classes?: number;
    held_out_ood_species?: string[];
  } | null;
  modelMeta: {
    status?: string;
    best_epoch?: number;
    best_val_accuracy?: number;
    best_val_loss?: number;
    fit_diagnosis?: string;
  } | null;
  rejectionConfig: {
    gate_method?: string;
    msp_threshold?: number;
    energy_threshold?: number | null;
    val_coverage?: number;
    val_selective_accuracy?: number;
  } | null;
  splitConfig: {
    seed?: number;
    known_species_count?: number;
    held_out_ood_species_count?: number;
    counts?: {
      train: number;
      validation: number;
      known_test: number;
      ood_test: number;
    };
  } | null;
  evaluationSummary: {
    closed_set_accuracy?: number;
    macro_precision?: number;
    macro_recall?: number;
    macro_f1?: number;
    known_coverage?: number;
    known_rejection_rate?: number;
    selective_accuracy?: number;
    msp_ood_auroc?: number;
    msp_ood_aupr?: number;
    energy_ood_auroc?: number;
    energy_ood_aupr?: number;
    ood_rejection_rate?: number;
    ood_false_acceptance_rate?: number;
  } | null;
  classDistribution: Array<{
    species: string;
    valid_image_count: string;
  }>;
  trainingHistory: Array<{
    epoch: string;
    train_loss: string;
    train_acc: string;
    val_loss: string;
    val_acc: string;
  }>;
  cvTechnologies?: CVTechnologyItem[];
  confusionMatrixAvailable: boolean;
  trainingCurvesAvailable: boolean;
}

export interface CVTechnologyItem {
  key: string;
  short_title: string;
  full_name: string;
  category: string;
  summary: string;
  what_is_this: string;
  why_used: string;
  how_it_works: string;
  where_used_in_medileaf: string;
  module_path: string;
  what_happens_when_runs: string;
  status: 'IMPLEMENTED' | 'VERIFIED' | 'NOT IMPLEMENTED';
  status_detail: string;
}

export const SAFETY_DISCLAIMER =
  'MEDILEAF.AI is an academic plant-image identification prototype. Its predictions are not medical advice or confirmation of plant safety. Do not consume, touch, or use any plant based solely on this application’s output. Consult a qualified botanist or relevant professional for verification.';
