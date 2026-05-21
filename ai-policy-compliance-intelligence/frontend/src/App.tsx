import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Database,
  FileSearch,
  FileText,
  Loader2,
  RefreshCw,
  Search,
  Send,
  ShieldCheck,
  Upload,
  type LucideIcon,
} from 'lucide-react'
import type { FormEvent, ReactNode } from 'react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api/client'
import { cn } from './lib/utils'
import type {
  AnalyticsResponse,
  Citation,
  ComplianceCheckResponse,
  HealthResponse,
  IngestionResponse,
  RiskLevel,
  SearchResponse,
} from './types/api'

const policyTypes = ['general', 'security', 'privacy', 'finance', 'hr', 'operations']

type AsyncState = 'idle' | 'loading' | 'success' | 'error'

function riskStyles(level?: RiskLevel) {
  if (level === 'high') return 'border-rose-200 bg-rose-50 text-rose-700'
  if (level === 'medium') return 'border-amber-200 bg-amber-50 text-amber-700'
  return 'border-emerald-200 bg-emerald-50 text-emerald-700'
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null)
  const [ingestion, setIngestion] = useState<IngestionResponse | null>(null)
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)
  const [compliance, setCompliance] = useState<ComplianceCheckResponse | null>(null)
  const [status, setStatus] = useState<AsyncState>('idle')
  const [message, setMessage] = useState('')

  const [title, setTitle] = useState('Vendor Data Handling Policy')
  const [policyType, setPolicyType] = useState('privacy')
  const [text, setText] = useState(
    'Customer personal data may be shared with approved vendors only after privacy approval, encryption in transit, and documented business purpose review.',
  )
  const [files, setFiles] = useState<File[]>([])
  const [query, setQuery] = useState('Can customer personal data be shared with vendors without encryption?')
  const [topK, setTopK] = useState(6)
  const [includeRecommendations, setIncludeRecommendations] = useState(true)

  const providerRows = useMemo(() => Object.entries(health?.providers ?? {}), [health])
  const busy = status === 'loading'

  const loadOverview = useCallback(async () => {
    try {
      setStatus('loading')
      const [healthData, analyticsData] = await Promise.all([api.health(), api.analytics()])
      setHealth(healthData)
      setAnalytics(analyticsData)
      setStatus('success')
      setMessage('Backend overview refreshed.')
    } catch (error) {
      setStatus('error')
      setMessage(error instanceof Error ? error.message : 'Unable to reach backend')
    }
  }, [])

  useEffect(() => {
    queueMicrotask(() => {
      void loadOverview()
    })
  }, [loadOverview])

  async function handleTextIngest(event: FormEvent) {
    event.preventDefault()
    try {
      setStatus('loading')
      const result = await api.ingestText({
        title,
        text,
        source: 'frontend',
        policy_type: policyType,
      })
      setIngestion(result)
      setMessage(result.message)
      await loadOverview()
    } catch (error) {
      setStatus('error')
      setMessage(error instanceof Error ? error.message : 'Text ingestion failed')
    }
  }

  async function handleFileIngest() {
    if (!files.length) {
      setMessage('Choose at least one file before uploading.')
      return
    }
    try {
      setStatus('loading')
      const result = await api.ingestFiles(files, policyType)
      setIngestion(result)
      setMessage(result.message)
      setFiles([])
      await loadOverview()
    } catch (error) {
      setStatus('error')
      setMessage(error instanceof Error ? error.message : 'File upload failed')
    }
  }

  async function handleSearch() {
    try {
      setStatus('loading')
      setSearchResults(await api.search({ query, policy_type: policyType, top_k: topK }))
      setStatus('success')
    } catch (error) {
      setStatus('error')
      setMessage(error instanceof Error ? error.message : 'Search failed')
    }
  }

  async function handleComplianceCheck() {
    try {
      setStatus('loading')
      setCompliance(
        await api.checkCompliance({
          query,
          policy_type: policyType,
          top_k: topK,
          include_recommendations: includeRecommendations,
        }),
      )
      setStatus('success')
    } catch (error) {
      setStatus('error')
      setMessage(error instanceof Error ? error.message : 'Compliance check failed')
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-ink-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-600 text-white">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-semibold tracking-normal text-ink-950">
                Policy Compliance Intelligence
              </h1>
              <p className="text-sm text-ink-500">
                Backend-connected workspace for evidence search and compliance decisions
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge health={health} />
            <button
              type="button"
              onClick={() => void loadOverview()}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-medium text-ink-700 shadow-line hover:bg-slate-100"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-5 px-5 py-5 lg:grid-cols-[360px_minmax(0,1fr)]">
        <aside className="space-y-5">
          <Panel title="Backend Status" icon={Activity}>
            <div className="grid grid-cols-2 gap-3">
              <Metric label="Documents" value={analytics?.documents ?? 0} />
              <Metric label="Chunks" value={analytics?.chunks ?? 0} />
            </div>
            <div className="mt-4 space-y-2">
              {providerRows.map(([name, value]) => (
                <div key={name} className="flex items-center justify-between gap-3 text-sm">
                  <span className="capitalize text-ink-500">{name.replaceAll('_', ' ')}</span>
                  <span
                    className={cn(
                      'rounded-md px-2 py-1 font-medium',
                      value === 'local' ? 'bg-slate-100 text-ink-700' : 'bg-blue-50 text-blue-700',
                    )}
                  >
                    {value}
                  </span>
                </div>
              ))}
              {!providerRows.length ? <EmptyLine text="Backend providers will appear after health check." /> : null}
            </div>
          </Panel>

          <Panel title="Policy Type" icon={Database}>
            <select
              value={policyType}
              onChange={(event) => setPolicyType(event.target.value)}
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
            >
              {policyTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            <label className="mt-4 block text-sm font-medium text-ink-700" htmlFor="topK">
              Retrieval depth
            </label>
            <input
              id="topK"
              type="range"
              min={1}
              max={20}
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
              className="mt-2 w-full accent-blue-600"
            />
            <div className="mt-1 text-sm text-ink-500">{topK} citations max</div>
            <div className="mt-3 rounded-md border border-blue-100 bg-blue-50 px-3 py-2 text-sm leading-5 text-blue-800">
              The selected type labels new uploads and filters searches. If no document exists for that type, the backend falls back to all indexed policies.
            </div>
            <div className="mt-4 border-t border-slate-200 pt-4">
              <div className="mb-2 text-sm font-medium text-ink-700">Indexed policy mix</div>
              <div className="space-y-2">
                {Object.entries(analytics?.policy_types ?? {}).length ? (
                  Object.entries(analytics?.policy_types ?? {}).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between rounded-md bg-slate-50 px-2 py-2 text-sm">
                      <span className="capitalize text-ink-600">{type}</span>
                      <span className="font-semibold text-ink-950">{count}</span>
                    </div>
                  ))
                ) : (
                  <EmptyLine text="No indexed policies yet." />
                )}
              </div>
            </div>
          </Panel>

          <Panel title="Activity" icon={BarChart3}>
            <div
              className={cn(
                'rounded-md border px-3 py-3 text-sm',
                status === 'error'
                  ? 'border-rose-200 bg-rose-50 text-rose-700'
                  : 'border-slate-200 bg-slate-100 text-ink-700',
              )}
            >
              <div className="flex items-center gap-2 font-medium">
                {status === 'loading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                {status}
              </div>
              {message ? <p className="mt-2 break-words text-sm">{message}</p> : null}
            </div>
          </Panel>
        </aside>

        <section className="space-y-5">
          <div className="grid gap-5 xl:grid-cols-2">
            <Panel title="Ingest Policy Text" icon={FileText}>
              <form className="space-y-3" onSubmit={(event) => void handleTextIngest(event)}>
                <input
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
                  placeholder="Policy title"
                />
                <textarea
                  value={text}
                  onChange={(event) => setText(event.target.value)}
                  className="min-h-36 w-full resize-y rounded-md border border-slate-300 bg-white px-3 py-2 text-sm leading-6"
                  placeholder="Paste policy text"
                />
                <PrimaryButton
                  type="submit"
                  icon={Upload}
                  label="Ingest Text"
                  loading={busy}
                  disabled={title.trim().length === 0 || text.trim().length < 20}
                />
              </form>
            </Panel>

            <Panel title="Upload Documents" icon={Upload}>
              <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center">
                <input
                  type="file"
                  multiple
                  accept=".txt,.md,.pdf,.docx"
                  onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
                  className="mx-auto block max-w-full text-sm text-ink-600 file:mr-3 file:rounded-md file:border-0 file:bg-blue-600 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
                />
                <p className="mt-3 text-sm text-ink-500">
                  {files.length ? `${files.length} file selected` : 'TXT, MD, PDF, and DOCX supported'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => void handleFileIngest()}
                disabled={busy || files.length === 0}
                className="mt-3 inline-flex h-10 items-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-medium text-ink-700 hover:bg-slate-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-ink-500"
              >
                <Upload className="h-4 w-4" />
                Upload Files
              </button>
              {ingestion ? <IngestionSummary ingestion={ingestion} /> : null}
            </Panel>
          </div>

          <Panel title="Compliance Workspace" icon={FileSearch}>
            <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_220px]">
              <textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="min-h-28 resize-y rounded-md border border-slate-300 bg-white px-3 py-2 text-sm leading-6"
                placeholder="Ask a compliance question"
              />
              <div className="space-y-3">
                <label className="flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
                  <input
                    type="checkbox"
                    checked={includeRecommendations}
                    onChange={(event) => setIncludeRecommendations(event.target.checked)}
                    className="h-4 w-4 accent-blue-600"
                  />
                  Include recommendations
                </label>
                <PrimaryButton
                  type="button"
                  icon={Search}
                  label="Search Evidence"
                  onClick={() => void handleSearch()}
                  loading={busy}
                  disabled={query.trim().length < 2}
                />
                <PrimaryButton
                  type="button"
                  icon={Send}
                  label="Check Compliance"
                  onClick={() => void handleComplianceCheck()}
                  loading={busy}
                  disabled={query.trim().length < 3}
                />
              </div>
            </div>
          </Panel>

          {compliance ? <ComplianceResult result={compliance} /> : null}
          {searchResults ? <CitationList title="Search Evidence" citations={searchResults.results} /> : null}
        </section>
      </div>
    </main>
  )
}

function Panel({
  title,
  icon: Icon,
  children,
}: {
  title: string
  icon: LucideIcon
  children: ReactNode
}) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-line">
      <div className="mb-4 flex items-center gap-2">
        <Icon className="h-5 w-5 text-blue-600" />
        <h2 className="text-base font-semibold tracking-normal text-ink-950">{title}</h2>
      </div>
      {children}
    </section>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
      <div className="text-2xl font-semibold text-ink-950">{value}</div>
      <div className="text-sm text-ink-500">{label}</div>
    </div>
  )
}

function EmptyLine({ text }: { text: string }) {
  return <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-ink-500">{text}</div>
}

function StatusBadge({ health }: { health: HealthResponse | null }) {
  const online = health?.status === 'ok'
  return (
    <div
      className={cn(
        'inline-flex h-10 items-center gap-2 rounded-md border px-3 text-sm font-medium',
        online ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-amber-200 bg-amber-50 text-amber-700',
      )}
    >
      {online ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
      {online ? `API ${health.version}` : 'API pending'}
    </div>
  )
}

function PrimaryButton({
  type,
  icon: Icon,
  label,
  loading,
  disabled,
  onClick,
}: {
  type: 'button' | 'submit'
  icon: LucideIcon
  label: string
  loading?: boolean
  disabled?: boolean
  onClick?: () => void
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={loading || disabled}
      className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-blue-600 px-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Icon className="h-4 w-4" />}
      {label}
    </button>
  )
}

function IngestionSummary({ ingestion }: { ingestion: IngestionResponse }) {
  return (
    <div className="mt-4 space-y-2">
      {ingestion.results.map((item) => (
        <div key={item.document_id} className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm">
          <div className="font-medium text-ink-900">{item.title}</div>
          <div className="mt-1 text-ink-500">
            {item.chunks_created} chunks · {item.policy_type}
          </div>
        </div>
      ))}
    </div>
  )
}

function ComplianceResult({ result }: { result: ComplianceCheckResponse }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-line">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-base font-semibold tracking-normal text-ink-950">Compliance Result</h2>
          <p className="mt-1 text-sm text-ink-500">{result.query}</p>
        </div>
        <span className={cn('rounded-md border px-3 py-1 text-sm font-semibold capitalize', riskStyles(result.risk_level))}>
          {result.risk_level} risk
        </span>
      </div>
      <p className="mt-4 rounded-md bg-slate-50 p-3 text-sm leading-6 text-ink-700">{result.answer}</p>
      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <div>
          <h3 className="text-sm font-semibold text-ink-950">Findings</h3>
          <div className="mt-2 space-y-2">
            {result.findings.map((finding) => (
              <div key={`${finding.control}-${finding.status}`} className="rounded-md border border-slate-200 p-3 text-sm">
                <div className="font-medium text-ink-900">{finding.control}</div>
                <div className="mt-1 text-ink-500">{finding.rationale}</div>
                <div className="mt-2 text-ink-700">{finding.recommendation}</div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-ink-950">Recommendations</h3>
          <ul className="mt-2 space-y-2">
            {result.recommendations.map((recommendation) => (
              <li key={recommendation} className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-ink-700">
                {recommendation}
              </li>
            ))}
          </ul>
        </div>
      </div>
      <CitationList title="Citations" citations={result.citations} compact />
    </section>
  )
}

function CitationList({
  title,
  citations,
  compact,
}: {
  title: string
  citations: Citation[]
  compact?: boolean
}) {
  return (
    <section className={cn(!compact && 'rounded-lg border border-slate-200 bg-white p-4 shadow-line', compact && 'mt-4')}>
      <h2 className="text-base font-semibold tracking-normal text-ink-950">{title}</h2>
      <div className="mt-3 grid gap-3">
        {citations.length ? (
          citations.map((citation) => (
            <article key={citation.chunk_id} className="rounded-md border border-slate-200 bg-white p-3 text-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="font-medium text-ink-900">{citation.title}</div>
                <div className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-ink-600">
                  {(citation.score * 100).toFixed(0)}%
                </div>
              </div>
              <p className="mt-2 leading-6 text-ink-600">{citation.excerpt}</p>
              <div className="mt-2 break-words text-xs text-ink-500">{citation.source}</div>
            </article>
          ))
        ) : (
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-ink-500">No citations yet.</div>
        )}
      </div>
    </section>
  )
}

export default App
