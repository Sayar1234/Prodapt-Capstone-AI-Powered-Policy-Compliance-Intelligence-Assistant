# AI-Powered Policy Compliance Intelligence — Full Project Documentation

## 1. Project Summary

This project is an AI-powered policy compliance intelligence assistant. It is designed to ingest policy, procedure, and regulatory documents, convert them into searchable policy chunks, and answer compliance questions with evidence citations, risk assessment, and recommended actions.

The project is split into two main applications:

- `backend/` — FastAPI backend for ingestion, storage, retrieval, compliance evaluation, and optional external provider integration.
- `frontend/` — React + TypeScript frontend for user input, document upload, search, and compliance result display.

The design is local-first, with optional integrations to external systems for scale.

---

## 2. Tech Stack

### Backend

- Python 3.11+ (recommended)
- FastAPI for HTTP API endpoints
- Uvicorn for ASGI hosting
- Pydantic / pydantic-settings for typed validation and configuration
- HTTPX for external API calls and scraping
- LangChain / LangGraph for structured tool orchestration when available
- NumPy-style math functions for local vector search
- PyPDF and python-docx for document ingestion
- MongoDB / PyMongo for persistent document storage (optional)
- Neo4j for graph storage of document relationships (optional)
- Weaviate for vector similarity indexing/search (optional)
- Upstash Redis via REST for cache (optional)
- Prometheus client for metrics
- Structlog-like logging setup
- DeepEval for evaluation/benchmarking support

### Frontend

- React 19
- TypeScript
- Vite for development and build
- Tailwind CSS for styling
- Lucide React icons
- ESLint for linting

---

## 3. High-Level Architecture

### Backend

The backend is centered around a REST API in `backend/app/main.py`. It configures the application, registers middleware, and loads route modules.

Key subsystems:

- `api/` — route definitions for health, ingestion, compliance, and analytics.
- `services/` — service classes that implement business operations.
- `agents/` — compliance orchestration, retrieval, risk scoring, recommendations, answer generation, and scraping.
- `ingestion/` — document loading, cleaning, chunking, and embedding.
- `retrieval/` — semantic retrieval, reranking, and citation construction.
- `database/` — local and optional external persistence for documents, graphs, vectors, and cache.
- `security/` — guardrails and upload validation.
- `observability/` — metrics and logging.
- `utils/` — helper utilities for citations, documents, links, and retry logic.

### Frontend

Frontend uses React, Vite, and TypeScript. It provides:

- health status and analytics overview
- ingestion by text or file upload
- query input for search and compliance checks
- evidence citation display
- structured compliance result display with risk, findings, and recommendations

The frontend communicates with the backend via a small API client in `frontend/src/api/client.ts`.

---

## 4. Configuration and Environment

### Settings loader

- `backend/app/core/config.py` uses `pydantic-settings` to load `.env` values.
- It defines defaults for providers, directories, chunking parameters, retrieval settings, risk thresholds, and scraping options.
- Directory paths are automatically created when the app starts.

### `.env`

The backend supports local and external providers. Common variables include:

- `APP_NAME`, `APP_VERSION`, `ENVIRONMENT`
- `API_PREFIX`, `HOST`, `PORT`, `CORS_ORIGINS`
- `DATA_DIR`, `RAW_DIR`, `PROCESSED_DIR`, `EMBEDDINGS_DIR`
- `LLM_PROVIDER`, `EMBEDDING_PROVIDER`
- `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, `OPENROUTER_EMBEDDING_MODEL`
- `DOCUMENT_STORE_PROVIDER`, `MONGODB_URI`, `MONGODB_DATABASE`
- `CACHE_PROVIDER`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`
- `GRAPH_PROVIDER`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `VECTOR_STORE_PROVIDER`, `WEAVIATE_URL`, `WEAVIATE_API_KEY`, `WEAVIATE_COLLECTION`
- `MAX_UPLOAD_MB`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `RETRIEVAL_TOP_K`
- `RISK_THRESHOLD_HIGH`, `RISK_THRESHOLD_MEDIUM`
- `ENABLE_LINK_SCRAPING`, `SCRAPE_TIMEOUT_SECONDS`, `MAX_SCRAPED_LINKS`, `MAX_SCRAPED_CHARS_PER_LINK`

### Provider modes

Default mode is local for most providers, enabling the app to run without cloud services.

- `local` mode uses JSON file storage and in-memory fallbacks.
- `mongodb`, `weaviate`, `neo4j`, `upstash`, and `openrouter` are optional external modes.

---

## 5. Data Models

### Core domain models

Located in `backend/app/models/domain_models.py`:

- `PolicyDocument` — ingested policy references and metadata.
- `DocumentChunk` — chunked text segments used for retrieval.
- `Citation` — evidence returned for a query.
- `ComplianceFinding` — structured finding with control, risk, evidence, rationale, and recommendation.
- `IngestionResult` — ingestion response details.
- `RiskLevel` — three-level risk enum: `low`, `medium`, `high`.

### Request and response models

Defined in `backend/app/models/request_models.py` and `backend/app/models/response_models.py`:

- `TextIngestionRequest`
- `ComplianceCheckRequest`
- `SearchRequest`
- `RiskAssessmentRequest`
- `HealthResponse`
- `IngestionResponse`
- `SearchResponse`
- `ComplianceCheckResponse`
- `AnalyticsResponse`

These models enforce API payload shapes and validation constraints.

---

## 6. Ingestion Flow

### Entry points

- `POST /api/v1/ingestion/text` — ingest raw policy text.
- `POST /api/v1/ingestion/files` — ingest uploaded files.

### Validation and upload rules

- Uploads are validated by `backend/app/security/validators.py`.
- Supported file extensions: `.txt`, `.md`, `.pdf`, `.docx`.
- Files larger than `MAX_UPLOAD_MB` are rejected.

### Pipeline

Implemented in `backend/app/ingestion/pipeline.py`.

Steps:

1. **Text normalization**
   - `backend/app/ingestion/cleaner.py`
   - removes null characters, collapses whitespace, and normalizes linebreaks.

2. **Link extraction and scraping**
   - `backend/app/utils/link_utils.py` identifies URLs.
   - `backend/app/agents/scraping_agent.py` fetches HTML/plain text from those URLs.
   - Scraped text is appended to the policy text as linked evidence.

3. **Chunking**
   - `backend/app/ingestion/chunker.py` creates chunks from document text.
   - Default chunk size is `900` words, overlap `150` words.

4. **Document persistence**
   - `backend/app/database/mongodb.py` stores the raw policy document and chunks.
   - Local mode writes `data/processed/document_store.json`.
   - MongoDB mode uses `documents` and `chunks` collections.

5. **Vector indexing**
   - `backend/app/database/weaviate.py` indexes chunks in Weaviate when enabled.
   - Local mode does not persist vectors but still supports embeddings for search.

6. **Knowledge graph**
   - `backend/app/database/neo4j.py` optionally persists chunk/document relationships.
   - Local mode is a no-op.

7. **Result**
   - The ingestion response includes document ID, title, chunk count, and policy type.

---

## 7. Embedding and Search

### Embeddings

Generated in `backend/app/ingestion/embeddings.py`.

- Local fallback uses deterministic hashing to produce a stable vector representation.
- When `EMBEDDING_PROVIDER=openrouter`, the app calls OpenRouter’s embedding endpoint.
- External embedding failures fall back to local embeddings.

### Vector search

Implemented in `backend/app/retrieval/vector_search.py`.

Behavior:

- If Weaviate is active, use remote semantic search.
- Otherwise, embed query locally and score chunks by cosine similarity.
- When `policy_type` filtering is active, the backend first filters by policy type, then falls back to all chunks if necessary.

### Hybrid search

Implemented in `backend/app/retrieval/hybrid_search.py`.

- Retrieves vector candidates.
- Converts them into structured citations.
- Re-ranks candidates using lexical overlap and semantic score.

### Reranking

Implemented in `backend/app/retrieval/reranker.py`.

- Lexical overlap is computed between query and chunk text.
- Final score = `0.65 * semantic_score + 0.35 * lexical_overlap`.

### Citation output

Created in `backend/app/utils/citation_utils.py`.

- Builds `Citation` objects with excerpt, score, title, and source.

---

## 8. Compliance Decision Flow

### Entry point

- `POST /api/v1/compliance/check`

### Orchestration

The compliance flow is orchestrated by `backend/app/agents/orchestrator.py`.

Sequence:

1. **Cache lookup**
   - A hashed request key is used to find cached responses.
   - Cache provider may be local memory or Upstash Redis.

2. **Guardrail screening**
   - `backend/app/security/guardrails.py` blocks disallowed prompts.
   - Example blocked phrases: `ignore previous instructions`, `reveal system prompt`, `exfiltrate`.

3. **Evidence retrieval**
   - `retrieve_policy_evidence` calls `RetrievalAgent.search`.
   - This uses the hybrid search pipeline.

4. **Risk assessment**
   - `backend/app/agents/risk_agent.py` computes risk using keyword signals.
   - Signals include:
     - category keywords from `app/core/constants.py`
     - high-risk terms
     - medium-risk terms
     - negation terms like `without`, `bypass`, and `avoid`
   - Score thresholds determine `low`, `medium`, or `high` risk.

5. **Recommendations**
   - `backend/app/agents/recommendation_agent.py` returns action suggestions by risk level.
   - High risk → legal review and mitigation planning.
   - Medium risk → request clarifying evidence.
   - Low risk → proceed with standard approval workflow.

6. **Answer synthesis**
   - `backend/app/agents/compliance_agent.py` attempts LLM answer generation.
   - If `LLM_PROVIDER=openrouter` and API keys exist, it calls OpenRouter.
   - If no external LLM is configured or call fails, the backend returns a local synthesized answer.

7. **Final response**\n - Includes answer, risk level, citations, findings, and recommendations.

### Graph orchestration support

- If `langgraph` is installed, `ComplianceOrchestrator` builds a state graph.
- Otherwise, it falls back to sequential node invocation.

---

## 9. API Endpoints

### Health

- `GET /health`
- Returns API status, environment, cache health, storage mode, and provider configuration.

### Ingestion

- `POST /ingestion/text`
  - Accepts JSON payload for title, text, source, policy_type, and metadata.
- `POST /ingestion/files`
  - Accepts multipart file upload.
  - Supports multiple files.

### Compliance and search

- `POST /compliance/check`
  - Runs the full compliance workflow.
- `POST /compliance/search`
  - Runs evidence retrieval only and returns citations.
- `GET /compliance/analytics`
  - Returns counts for documents, chunks, and policy types.

### Metrics

- `GET /metrics`
  - Prometheus-compatible metrics if Prometheus is installed.

---

## 10. Frontend Flow

### Main UI

The main UI is implemented in `frontend/src/App.tsx`.

It contains:

- backend status and provider overview
- ingestion forms for text and files
- policy type selector
- query text area for compliance questions
- buttons for evidence search and compliance check
- display panels for results and citations

### API integration

`frontend/src/api/client.ts` provides a simple wrapper to call backend endpoints.

- Uses `VITE_API_BASE_URL` or defaults to `http://localhost:8000/api/v1`
- Handles errors and response parsing
- Supports JSON and multipart/form-data uploads

### Types

`frontend/src/types/api.ts` defines the TypeScript shapes for backend responses.

### User interaction

1. Load backend health and analytics on startup.
2. Ingest text or files to populate the document store.
3. Enter compliance query and choose retrieval depth + policy type.
4. Run evidence search or compliance check.
5. View citations, risk, answer, findings, and recommendations.

---

## 11. Deployment and Runtime

### Local backend

Run from `backend/`:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Local frontend

Run from `frontend/`:

```bash
npm install
npm run dev
```

### Docker

Backend container support exists in `backend/docker/docker-compose.yml` and `backend/docker/fastapi.Dockerfile`.

- `docker-compose.yml` mounts `../data` and exposes `8000`.
- `fastapi.Dockerfile` installs Python requirements and starts Uvicorn.

### Environment requirements

- front-end: `VITE_API_BASE_URL` for backend override
- back-end: `.env` file or environment variables for providers and credentials

---

## 12. Local vs External Provider Behavior

### Local mode

The app is fully usable with local fallbacks:

- document storage via local JSON file
- cache via in-memory Python dictionary
- vector search via deterministic embedding and cosine similarity
- no-op knowledge graph storage
- local answer fallback when external LLM is unavailable

### OpenRouter mode

If configured, the app can use OpenRouter for:

- LLM answer generation
- embeddings

### MongoDB mode

When enabled, the app stores documents and chunks in MongoDB instead of a JSON file.

### Weaviate mode

When enabled, the app stores chunk vectors and performs remote semantic search.

### Neo4j mode

When enabled, the app persists policy document/chunk relationships to Neo4j.

### Upstash mode

When enabled, the app uses Upstash Redis for caching compliance responses.

---

## 13. File Map and Key Files

### Backend key files

- `backend/app/main.py` — application startup and route registration
- `backend/app/core/config.py` — environment and configuration
- `backend/app/api/routes/` — endpoints for ingestion, compliance, health
- `backend/app/services/` — service layer connecting API to business logic
- `backend/app/agents/` — orchestrator, retrieval, risk, recommendations, compliance answer, scraping
- `backend/app/ingestion/` — document processing pipeline
- `backend/app/retrieval/` — search and ranking
- `backend/app/database/` — storage, cache, and provider abstraction
- `backend/app/security/` — validation and guardrails
- `backend/app/observability/` — logging and metrics
- `backend/app/utils/` — reusable utilities

### Frontend key files

- `frontend/src/App.tsx` — main UI and workflow
- `frontend/src/api/client.ts` — backend API wrapper
- `frontend/src/types/api.ts` — API response types
- `frontend/src/main.tsx` — React entry point

### Support files

- `backend/requirements.txt`
- `backend/docker/docker-compose.yml`
- `backend/docker/fastapi.Dockerfile`
- `backend/.env` — runtime configuration
- `frontend/package.json`
- `frontend/README.md`

---

## 14. Request/Response Lifecycle

### Ingestion request lifecycle

1. UI sends a text or file ingestion request.
2. API endpoint validates body or multipart upload.
3. Text is normalized and cleaned.
4. URLs are extracted and optionally scraped.
5. Policy text is chunked into searchable pieces.
6. Document and chunks are stored locally or in MongoDB.
7. Chunks are indexed in Weaviate if configured.
8. Knowledge graph entries are optionally created in Neo4j.
9. The API returns ingestion metadata.

### Compliance query lifecycle

1. UI sends `POST /compliance/check` with `query`, `policy_type`, `top_k`, and recommendation preference.
2. Backend checks cache for a previous answer.
3. Guardrails screen the query.
4. Relevant chunks are retrieved by hybrid search.
5. Risk score is calculated from query and evidence.
6. Recommendations are generated based on risk.
7. A compliance answer is generated with optional LLM support.
8. The API returns the answer, risk, findings, citations, and recommendations.

---

## 15. Strengths and Design Rationale

- **Local-first design** makes the project easy to run without external dependencies.
- **Layered pipeline** separates ingestion, storage, retrieval, and compliance evaluation.
- **Evidence-based output** keeps answers grounded in retrieved policy chunks.
- **Optional provider support** allows the system to scale from local dev to cloud-backed production.
- **Frontend workflow** provides a clean UI for ingestion, query, search, and decision support.

---

## 16. Useful Notes

- The backend can be run on `http://localhost:8000` and the frontend on `http://localhost:5173`.
- The backend exposes Swagger docs at `/docs` when running locally.
- The project supports both direct text ingestion and file-based ingestion.
- The compliance engine uses local keyword-based risk scoring by default, which is deterministic and explainable.
- Provider flags in `.env` let the project switch smoothly between local fallback and external cloud services.

---

## 17. Recommended Next Steps

If you want, this document can be further extended with:

- a `Architecture.md` with diagrams
- a provider configuration guide for OpenRouter, MongoDB, Weaviate, Neo4j, and Upstash
- an API reference section with example payloads
- a developer onboarding section for running tests and adding new policy types
