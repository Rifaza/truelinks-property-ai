export interface WorkOrderDraft {
  title: string;
  description: string;
  affected_unit: string;
  recommended_action: string;
}

export interface PhotoIssueResult {
  issue: string;
  description: string;
  severity: string;
  condition: string;
  visible_items: string[];
  work_order: WorkOrderDraft;
}