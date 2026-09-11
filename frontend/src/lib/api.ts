export interface ExtractedField {
  name: string;
  label: string;
  value: string;
  confidence: number;
}

export type DocumentStatus =
  | "auto_approved"
  | "pending_review"
  | "approved"
  | "boundary_drawn";

export interface AnalyzeResult {
  document_id: string;
  filename: string;
  processed_at: string;
  fields: ExtractedField[];
  overall_confidence: number;
  review_required: boolean;
  status: DocumentStatus;
  boundary: number[][] | null;
}

const API_BASE_URL = "http://localhost:8000";

export async function analyzeDocument(file: File): Promise<AnalyzeResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Analysis failed");
  }

  return response.json();
}

export async function listDocuments(status?: DocumentStatus): Promise<AnalyzeResult[]> {
  const url = status
    ? `${API_BASE_URL}/api/documents?status=${status}`
    : `${API_BASE_URL}/api/documents`;
  const response = await fetch(url);
  if (!response.ok) throw new Error("Failed to list documents");
  const body = await response.json();
  return body.documents;
}

export async function getDocument(documentId: string): Promise<AnalyzeResult> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);
  if (!response.ok) throw new Error("Document not found");
  return response.json();
}

export async function approveDocument(documentId: string): Promise<AnalyzeResult> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/approve`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Approve failed");
  return response.json();
}

export async function saveBoundary(
  documentId: string,
  points: number[][]
): Promise<AnalyzeResult> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/boundary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ points }),
  });
  if (!response.ok) throw new Error("Save boundary failed");
  return response.json();
}
