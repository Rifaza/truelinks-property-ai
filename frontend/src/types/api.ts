export interface WorkOrder {
  id?: number;
  title: string;
  description: string;
  affected_unit: string;
  recommended_action: string;
  status?: string;
}

export interface PropertyIssue {
  id?: number;
  issue: string;
  description: string;
  severity: string;
  condition: string;
  visible_items: string[];
  status?: string;
  work_order?: WorkOrder | null;
}

export interface Lease {
  id: number;
  tenant_name: string | null;
  monthly_rent: number | null;
  annual_rent: number | null;
  deposit_amount: number | null;
  start_date: string | null;
  end_date: string | null;
  term_months: number | null;
}

export interface UnitOverview {
  id: number;
  unit_number: string;
  label: string;
  unit_type: string;
  area_sqm: number;
  parking_bay: string | null;
  status: string;
  lease: Lease | null;
  issues: PropertyIssue[];
}

export interface RuleResult {
  rule_id: string;
  status: "PASS" | "FAIL" | "NOT_DETERMINABLE";
  explanation: string;
  evidence: {
    field_name: string;
    source_reference: string;
    source_text: string;
    confidence: number;
  }[];
}

export interface LeaseEvaluation {
  lease_id: number;
  rules: RuleResult[];
}