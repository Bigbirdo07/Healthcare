export type CoverageStatus = 'Covered' | 'Conditional' | 'Not covered' | 'Unknown / needs verification';

export type BenefitPathway =
  | 'OTC allowance'
  | 'Prescription/pharmacy benefit'
  | 'Durable Medical Equipment (DME)'
  | 'Preventive-care benefit'
  | 'Medicaid benefit'
  | 'Medicare Advantage supplemental benefit'
  | 'Vision benefit'
  | 'Dental benefit'
  | 'Wellness benefit'
  | 'Chronic-condition supplemental benefit'
  | 'Nutrition/medical-food benefit'
  | 'Other plan-specific supplemental benefits';

export type StateCode = 'RI' | 'MA' | 'CT' | 'NH' | 'VT' | 'ME';
export type PlanType = 'Commercial' | 'Medicaid' | 'Medicare' | 'Medicare Advantage';

export type ActionType =
  | 'get_item'
  | 'find_pharmacy'
  | 'find_supplier'
  | 'ask_provider'
  | 'view_coverage'
  | 'check_eligibility';

export interface Insurer {
  id: string;
  name: string;
  code: string;
  states: StateCode[];
}

export interface Plan {
  id: string;
  insurer_id: string;
  plan_name: string;
  plan_year: number;
  state: StateCode;
  plan_type: PlanType;
}

export interface OfficialSource {
  source_id: string;
  source_name: string;
  source_url: string;
  source_effective_date: string;
  last_verified_date: string;
  is_verified_real_data: boolean;
}

export interface Product {
  id: string;
  product_name: string;
  generic_name: string;
  brand_name?: string;
  category: string;
  subcategory: string;
  description: string;
  icon: string;
  aliases: string[];
  synonyms: string[];
  keywords: string[];
}

export interface CoverageRule {
  rule_id: string;
  product_id: string;
  plan_id: string;
  benefit_pathway: BenefitPathway;
  coverage_status: CoverageStatus;
  state: StateCode;
  plan_type: PlanType;
  otc_allowance_eligible: boolean;
  prescription_required: boolean | 'Depends';
  provider_order_required: boolean | 'Depends';
  diagnosis_required: boolean | 'Depends';
  prior_authorization_required: boolean | 'Depends';
  quantity_limit?: string;
  age_restriction?: string;
  network_pharmacy_required: boolean;
  network_dme_supplier_required: boolean;
  member_cost: string;
  copay: string;
  coinsurance: string;
  allowance_amount?: number;
  allowance_frequency?: 'monthly' | 'quarterly' | 'annual';
  official_source_name: string;
  official_source_url: string;
  source_effective_date: string;
  last_verified_date: string;
  notes: string;
  plain_english_explanation: string;
  action_type: ActionType;
  action_label: string;
}
