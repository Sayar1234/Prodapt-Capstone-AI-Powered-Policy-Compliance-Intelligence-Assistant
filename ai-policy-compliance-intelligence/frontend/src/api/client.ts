import type {
  AnalyticsResponse,
  ComplianceCheckResponse,
  HealthResponse,
  IngestionResponse,
  SearchResponse,
} from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        ...(init?.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...init?.headers,
      },
    })
  } catch {
    throw new Error(`Unable to reach backend at ${API_BASE_URL}`)
  }

  if (!response.ok) {
    throw new Error(await parseError(response))
  }

  return response.json() as Promise<T>
}

async function parseError(response: Response) {
  const fallback = `Request failed with status ${response.status}`
  const text = await response.text()
  try {
    const payload = JSON.parse(text)
    if (payload?.error?.message) return payload.error.message as string
    if (Array.isArray(payload?.detail)) {
      return payload.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join('; ') || fallback
    }
    if (typeof payload?.detail === 'string') return payload.detail
    return fallback
  } catch {
    return text || fallback
  }
}

export const api = {
  health: () => request<HealthResponse>('/health'),
  analytics: () => request<AnalyticsResponse>('/compliance/analytics'),
  ingestText: (payload: { title: string; text: string; source: string; policy_type: string }) =>
    request<IngestionResponse>('/ingestion/text', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  ingestFiles: (files: File[], policyType: string) => {
    const form = new FormData()
    files.forEach((file) => form.append('files', file))
    form.append('policy_type', policyType)
    return request<IngestionResponse>('/ingestion/files', {
      method: 'POST',
      body: form,
    })
  },
  search: (payload: { query: string; policy_type?: string; top_k: number }) =>
    request<SearchResponse>('/compliance/search', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  checkCompliance: (payload: {
    query: string
    policy_type?: string
    top_k: number
    include_recommendations: boolean
  }) =>
    request<ComplianceCheckResponse>('/compliance/check', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
