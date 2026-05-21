# Backend Implementation Checklist

This checklist tracks what has been implemented in the backend so far versus what still needs to be completed. It is based on the current project scaffold and the backend work already added. The original PDF was not accessible from the sandbox, so any PDF-specific requirement matching should be reviewed once the PDF contents are available inside the workspace.

## Implemented

- [x] FastAPI application entry point in `app/main.py`
- [x] Versioned API prefix support through `API_PREFIX`
- [x] Environment-based configuration through `backend/.env`
- [x] `.env.example` template with required provider variables
- [x] OpenRouter configuration placeholders
- [x] OpenRouter chat completion client for compliance answers
- [x] OpenRouter embedding endpoint support with local fallback
- [x] Upstash Redis REST configuration placeholders
- [x] Upstash Redis REST cache client
- [x] Compliance response caching for repeated checks
- [x] MongoDB document/chunk store provider
- [x] Neo4j knowledge graph provider for policy document/chunk/type relationships
- [x] Weaviate vector provider for chunk indexing and vector search
- [x] Local fallback mode that runs without external API keys
- [x] Health endpoint: `GET /api/v1/health`
- [x] Metrics endpoint: `GET /metrics`
- [x] CORS configuration through env values
- [x] Structured request and response models with Pydantic
- [x] Text policy ingestion endpoint: `POST /api/v1/ingestion/text`
- [x] File ingestion endpoint: `POST /api/v1/ingestion/files`
- [x] Support for `.txt`, `.md`, `.pdf`, and `.docx` document loading
- [x] Document text cleaning and normalization
- [x] Link extraction from ingested text/PDF/DOCX content
- [x] Website scraping agent for linked policy/reference pages
- [x] Scraped link evidence enrichment during ingestion
- [x] Policy document chunking with configurable chunk size and overlap
- [x] Local JSON-backed document store
- [x] Deterministic local embeddings for no-key development
- [x] Local vector-style retrieval
- [x] Hybrid retrieval with lexical reranking
- [x] Citation generation with excerpts and source metadata
- [x] Policy search endpoint: `POST /api/v1/compliance/search`
- [x] Compliance check endpoint: `POST /api/v1/compliance/check`
- [x] Analytics endpoint: `GET /api/v1/compliance/analytics`
- [x] Basic compliance orchestration agent
- [x] LangChain StructuredTool wrappers around retrieval, risk, recommendation, and synthesis agents
- [x] LangGraph workflow orchestration for guardrails, retrieval, risk assessment, recommendations, and answer synthesis
- [x] Retrieval agent
- [x] Risk assessment agent
- [x] Calibrated risk scoring for sensitive data, privileged access, incidents, vendors, and bypass/without-control language
- [x] Recommendation agent
- [x] Human-readable local compliance answer synthesis when no OpenRouter key is available
- [x] Basic prompt-injection guardrail screening
- [x] Basic risk keyword taxonomy
- [x] Evaluation helpers for citation coverage and average retrieval score
- [x] DeepEval-compatible custom evaluation metrics
- [x] Deterministic benchmark cases with quality gates
- [x] Benchmark script skeleton
- [x] Document ingestion CLI script
- [x] Dockerfile and Docker Compose file
- [x] Runtime README with setup instructions
- [x] Request ID propagation through `X-Request-ID`
- [x] Provider visibility in health response
- [x] Unit and integration tests using Python `unittest`

## Provider Integrations Completed

- [x] OpenRouter LLM calls
  - Set `LLM_PROVIDER=openrouter`.
  - Add `OPENROUTER_API_KEY`.
  - Compliance answers are generated with OpenRouter and fall back to local responses if the call fails.

- [x] OpenRouter embeddings
  - Set `EMBEDDING_PROVIDER=openrouter`.
  - Add `OPENROUTER_API_KEY`.
  - Embeddings fall back to deterministic local embeddings if the call fails.

- [x] Upstash Redis cache
  - Set `CACHE_PROVIDER=upstash`.
  - Add `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`.
  - Compliance checks are cached for repeated identical requests.

- [x] MongoDB document store
  - Set `DOCUMENT_STORE_PROVIDER=mongodb`.
  - Add `MONGODB_URI`.
  - Documents and chunks are persisted in MongoDB collections.

- [x] Neo4j knowledge graph
  - Set `GRAPH_PROVIDER=neo4j`.
  - Add `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD`.
  - Ingested documents, chunks, and policy types are upserted as graph nodes and relationships.

- [x] Weaviate vector database
  - Set `VECTOR_STORE_PROVIDER=weaviate`.
  - Add `WEAVIATE_URL` and optionally `WEAVIATE_API_KEY`.
  - Ingested chunks are indexed in Weaviate and retrieval uses Weaviate vector search.

## Partially Implemented

- [ ] Observability
  - Logging, Prometheus-style metrics, request IDs, and provider status are implemented.
  - Distributed tracing and dashboards are not implemented yet.

## Yet To Be Implemented

- [ ] Stronger OpenRouter retry/backoff policy and detailed provider error mapping
- [ ] Production-grade retrieval-augmented generation response synthesis with structured JSON output
- [ ] DeepEval LLM-as-judge metrics such as faithfulness/relevancy using a configured judge model
- [ ] Benchmark result persistence and historical regression reports
- [ ] Distributed tracing with OpenTelemetry
- [ ] Metrics dashboards and alerting
- [ ] User authentication and authorization
- [ ] Role-based access control for compliance teams
- [ ] Audit logs for ingestion, searches, and compliance decisions
- [ ] Document versioning and policy lifecycle management
- [ ] Policy approval workflow
- [ ] Risk register storage and tracking
- [ ] Control mapping to frameworks such as GDPR, HIPAA, SOC 2, ISO 27001, or internal policies
- [ ] Admin endpoints for deleting/reindexing documents
- [ ] Batch ingestion job status tracking
- [ ] Background task queue for large document ingestion
- [x] Unit tests
- [x] Integration tests
- [ ] End-to-end API tests
- [ ] CI pipeline configuration
- [ ] Production deployment manifests
- [ ] Frontend integration
- [ ] PDF requirement-by-requirement traceability review

## Current Minimum Working Flow

1. Start the backend.
2. Ingest policy text or upload policy documents.
3. Search ingested policy evidence.
4. Run a compliance check.
5. Receive a risk level, findings, recommendations, and citations.

## Notes

- Keep all providers as `local` to run without paid services.
- Set `LLM_PROVIDER=openrouter` only after adding `OPENROUTER_API_KEY`.
- Set `EMBEDDING_PROVIDER=openrouter` only if your selected OpenRouter route supports embeddings.
- Set `CACHE_PROVIDER=upstash` only after adding `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`.
- The next best backend milestone is adding tests around each provider integration.
