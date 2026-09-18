import {
  ChatRequest,
  ChatResponse,
  LandProfileResponse,
  DashboardData,
  EnvironmentalState,
  RecommendationOutput,
  RetrievalTrace,
  CorpusDocument,
  SystemHealth,
} from './types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function sendChatMessage(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to send chat message');
  }
  return res.json();
}

export async function fetchLandProfiles(): Promise<LandProfileResponse[]> {
  const res = await fetch(`${API_BASE}/land-profiles`);
  if (!res.ok) throw new Error('Failed to fetch land profiles');
  return res.json();
}

export async function fetchProfileDashboard(profileId: string): Promise<DashboardData> {
  const res = await fetch(`${API_BASE}/land-profiles/${profileId}/dashboard`);
  if (!res.ok) throw new Error('Failed to fetch profile dashboard');
  return res.json();
}

export async function createLandProfile(data: {
  name: string;
  region: string;
  area_hectares: number;
  primary_crop: string;
  farming_system: string;
  current_state?: Partial<EnvironmentalState>;
}): Promise<LandProfileResponse> {
  const res = await fetch(`${API_BASE}/land-profiles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to create land profile');
  }
  return res.json();
}

export async function analyzeState(state: EnvironmentalState): Promise<RecommendationOutput[]> {
  const res = await fetch(`${API_BASE}/recommendations/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to analyze environmental state');
  }
  return res.json();
}

export async function searchKnowledge(
  query: string,
  targetMetric?: string,
  region?: string,
  topK = 3
): Promise<RetrievalTrace> {
  const params = new URLSearchParams({ query, top_k: String(topK) });
  if (targetMetric) params.append('target_metric', targetMetric);
  if (region) params.append('region', region);

  const res = await fetch(`${API_BASE}/knowledge/search?${params.toString()}`);
  if (!res.ok) throw new Error('Knowledge search failed');
  return res.json();
}

export async function fetchDocuments(): Promise<{ total_documents: number; documents: CorpusDocument[] }> {
  const res = await fetch(`${API_BASE}/knowledge/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}
