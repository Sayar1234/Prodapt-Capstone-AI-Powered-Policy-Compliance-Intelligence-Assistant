export type RiskLevel = 'low' | 'medium' | 'high'

export type HealthResponse = {
  status: string
  version: string
  environment: string
  timestamp: string
  services: Record<string, string>
  providers: Record<string, string>
}

export type Citation = {
  document_id: string
  chunk_id: string
  title: string
  source: string
  excerpt: string
  score: number
}

export type ComplianceFinding = {
  control: string
  status: string
  risk_level: RiskLevel
  evidence: Citation[]
  rationale: string
  recommendation: string
}

export type ComplianceCheckResponse = {
  query: string
  answer: string
  risk_level: RiskLevel
  findings: ComplianceFinding[]
  citations: Citation[]
  recommendations: string[]
}

export type SearchResponse = {
  query: string
  results: Citation[]
}

export type IngestionResponse = {
  results: Array<{
    document_id: string
    title: string
    chunks_created: number
    policy_type: string
  }>
  message: string
}

export type AnalyticsResponse = {
  documents: number
  chunks: number
  policy_types: Record<string, number>
}
