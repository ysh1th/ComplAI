export interface UserProfile {
  user_id: string;
  age: number;
  country: string;
  full_name: string;
  income_level: "low" | "medium" | "high";
  occupation: string;
  kyc_status: "verified" | "pending";
  risk_profile: "low" | "medium" | "high";
  historical_countries: string[];
}

export interface UserBaseline {
  user_id: string;
  avg_tx_amount_usd: number;
  avg_daily_total_usd: number;
  avg_tx_per_day: number;
  std_dev_amount: number;
  normal_hour_range: number[];
  excluded_anomalies_count: number;
  min_tx_amount_usd: number;
  max_tx_amount_usd: number;
}

export interface RawTransaction {
  user_id: string;
  timestamp: string;
  transaction_amount_usd: number;
  transaction_currency: string;
  transaction_type: string;
  transaction_country: string;
  transaction_city: string;
}

export interface PreprocessedTransaction {
  user_id: string;
  timestamp: string;
  transaction_amount_usd: number;
  transaction_currency: string;
  transaction_type: string;
  transaction_country: string;
  transaction_city: string;
  hour_of_day: number;
  time_since_last_sec: number;
  previous_country: string;
  previous_timestamp: string;
  distance_km: number;
  actual_travel_hours: number;
  daily_total_usd: number;
  tx_count_per_day: number;
  is_new_country: boolean;
}

export interface Regulation {
  regulation_update_id: string;
  update_title: string;
  summary: string;
  date_effective: string;
}

export interface RuleEntry {
  category: string;
  rule: string;
  points: number;
}

export interface Rulebook {
  amount_based: string[];
  frequency_based: string[];
  location_based: string[];
  behavioural_pattern: string[];
  risk_score: {
    range: string;
    rules: RuleEntry[];
    capping: string;
  };
  risk_bands: Record<string, string>;
}

export interface AgentLogEntry {
  agent: string;
  icon: string;
  status: "success" | "alert" | "high" | "complete" | "error";
  message: string;
  duration_ms: number;
  retry_count?: number;
  retry_type?: "technical" | "logical" | null;
}

export type RiskBand = "HIGH" | "MEDIUM" | "LOW" | "CLEAN";

export interface UserWithState {
  profile: UserProfile;
  baseline: UserBaseline;
  current_risk_score: number;
  current_risk_band: RiskBand;
  latest_analysis?: FullAnalysisResponse;
  historical_transactions?: RawTransaction[];
}

export interface InitResponse {
  users: UserWithState[];
}

export interface FullAnalysisResponse {
  user_id: string;
  user_name: string;
  jurisdiction: string;
  risk_score: number;
  risk_band: RiskBand;
  risk_profile: "low" | "medium" | "high";
  reasoning: string;
  flags: string[];
  regulations_violated: string[];
  agent_chain: AgentLogEntry[];
  preprocessed: PreprocessedTransaction;
  baseline: UserBaseline;
  generated_transactions: RawTransaction[];
  timestamp: string;
  trace_id?: string;
  validator_loops?: number;
}

export interface ComplianceData {
  jurisdiction: string;
  jurisdiction_code: string;
  current_version: string;
  old_regulations: Regulation[];
  new_regulations: Regulation[];
  rulebook: Rulebook;
  available_new_regulations: Regulation[];
}

export interface CompliancePushResponse {
  jurisdiction_code: string;
  new_version: string;
  summary: string;
  comparison_points: string[];
  impact_analysis: string;
  rulebook_changes: string;
  updated_rulebook: Rulebook;
  agent_chain: AgentLogEntry[];
  draft_id?: string;
  status?: string;
}

export interface ComplianceDraft {
  id: string;
  jurisdiction_code: string;
  proposed_version: string;
  rulebook: Rulebook;
  previous_rulebook?: Rulebook;
  changes_description: string;
  summary: string;
  comparison_points: string[];
  impact_analysis: string;
  agent_chain: AgentLogEntry[];
  regulation_id: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  reviewed_at?: string;
}

export interface IngestBatchRequest {
  user_id: string;
  num_transactions: number;
  min_amount?: number;
  max_amount?: number;
  variance?: number;
  countries?: string[];
  overrides?: {
    transaction_currency?: string;
  };
}
