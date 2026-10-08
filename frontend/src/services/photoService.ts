import type { PhotoIssueResult } from "../types/photo";

const API_BASE_URL = "http://localhost:8000";

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

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Photo analysis failed.");
  }

  return response.json();
}