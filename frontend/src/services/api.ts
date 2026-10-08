import type {
  LeaseEvaluation,
  UnitOverview,
  PropertyIssue,
} from "../types/api";


import type { PhotoIssueResult } from "../types/photo";

const API_BASE_URL = "http://127.0.0.1:8000";


async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type");
  const body = contentType?.includes("application/json")
    ? await response.json().catch(() => null)
    : await response.text().catch(() => "");

  if (!response.ok) {
    const detail =
      typeof body === "object" && body !== null
        ? body.detail || body.message
        : body;

    throw new Error(
      typeof detail === "string" && detail.trim()
        ? `HTTP ${response.status}: ${detail}`
        : `HTTP ${response.status}: Request failed.`
    );
  }

  return body as T;
}


export async function getUnitOverview(
  unitId: number,
): Promise<UnitOverview> {
  const response = await fetch(
    `${API_BASE_URL}/api/units/${unitId}`,
  );

  return handleResponse<UnitOverview>(response);
}

export async function evaluateLease(
  leaseId: number,
): Promise<LeaseEvaluation> {
  const response = await fetch(
    `${API_BASE_URL}/api/leases/${leaseId}/evaluate`,
    {
      method: "POST",
    },
  );

  return handleResponse<LeaseEvaluation>(response);
}

export async function analyzePhoto(
  file: File,
  affectedUnit: string,
): Promise<PhotoIssueResult> {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("affected_unit", affectedUnit);

  const response = await fetch(
    `${API_BASE_URL}/api/photos/analyze`,
    {
      method: "POST",
      body: formData,
    },
  );

  return handleResponse<PhotoIssueResult>(response);
}

export async function createPropertyIssue(
  unitId: number,
  result: PropertyIssue,
): Promise<PropertyIssue> {
  const response = await fetch(
    `${API_BASE_URL}/api/property-issues/${unitId}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(result),
    },
  );

  return handleResponse<PropertyIssue>(response);
}

export async function acceptWorkOrder(
  workOrderId: number,
) {
  const response = await fetch(
    `${API_BASE_URL}/api/work-orders/${workOrderId}/accept`,
    {
      method: "PATCH",
    },
  );

  return handleResponse(response);
}

export async function rejectWorkOrder(
  workOrderId: number,
) {
  const response = await fetch(
    `${API_BASE_URL}/api/work-orders/${workOrderId}/reject`,
    {
      method: "PATCH",
    },
  );

  return handleResponse(response);
}



export interface LeaseUploadResponse {
  message: string;
  lease_id: number;
  filename: string;
  unit_number: string;
  extraction_mode: string;
  human_review_required: boolean;
  occupancy_updated: boolean;
  rules: {
    rule_id: string;
    status: "PASS" | "FAIL" | "NOT_DETERMINABLE";
    explanation: string;
  }[];
}

export async function uploadLease(file: File): Promise<LeaseUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/leases/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<LeaseUploadResponse>(response);
}
