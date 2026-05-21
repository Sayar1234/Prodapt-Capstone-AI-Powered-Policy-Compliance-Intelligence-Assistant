# AI-Powered Policy Compliance Intelligence Assistant

A full-stack assistant for policy compliance analysis, evidence-backed risk assessment, and recommended next steps. This repository combines a Python FastAPI backend with a React + TypeScript frontend and supports both local development and optional external providers for AI, vector search, caching, persistence, and knowledge graph storage.

---

## Project Overview

This project is designed to ingest policy, procedure, and regulatory documents, turn them into searchable policy chunks, and answer compliance questions with evidence citations, risk assessment, and recommended actions.

Key capabilities:

- Document ingestion from plain text and files
- Link scraping for referenced web evidence
- Document chunking and metadata organization
- Local and external embedding + vector search
- Keyword-based risk scoring and compliance recommendations
- Structured agent orchestration with a Graph workflow
- React frontend for user input, status, and results

The repo is split into two main apps:

- `backend/` — API, ingestion, storage, retrieval, agents, and risk/compliance logic
- `frontend/` — React user interface for calling the backend

---

## What makes this project special?

### 1. Real compliance intelligence pipeline

The backend is built around a layered workflow:

- ingest policy content
- normalize and chunk text
- build embeddings and optional vector index
- retrieve relevant citations for a query
- assess risk using policy keywords and evidence
- recommend actions based on risk level
- return a compliance answer with citations

### 2. Local-first fallback architecture

The system is intentionally runnable with no external services.
The backend supports the following local fallback implementations:

- Local JSON document store under `backend/data/processed/document_store.json`
- In-memory cache for temporary backend data
- Deterministic local embeddings via hashed token vectors
- Local cosine similarity search across indexed chunks
- Local knowledge-graph fallback with in-memory relationships
- Local compliance answer synthesis when no external LLM is configured

This makes the app easy to run in development without API keys, third-party services, or cloud infrastructure.

### 3. Optional external providers for scale and production

When you want more advanced functionality, the backend can switch providers via environment variables:

- `openrouter` for LLM and embedding calls
- `mongodb` for persistent document storage
- `weaviate` for vector search and semantic retrieval
- `neo4j` for knowledge graph relationships
- `upstash` for remote Redis-style cache

Each provider is configurable independently, so you can choose a hybrid deployment.

---

## Tech stack

### Backend

- Python 3.11+ (recommended)
- FastAPI for the HTTP API and developer-friendly docs
- Uvicorn for ASGI server hosting
- Pydantic / pydantic-settings for typed validation and environment configuration
- LangChain / LangGraph for structured tool and workflow orchestration
- HTTPX for external HTTP client calls
- `numpy`, `scikit-learn`-style similarity utilities for local search
- `pypdf`, `python-docx` for file ingestion
- `motor` / `pymongo` for MongoDB storage (optional)
- `neo4j` connector for graph persistence (optional)
- `weaviate-client` for vector storage (optional)
- `structlog` and Prometheus client for observability
- `deepeval` for deterministic evaluation/benchmarking

### Frontend

- React 19 for a modern component-based UI
- TypeScript for type safety
- Vite for fast development and build performance
- Tailwind CSS for responsive styling
- Lucide React icons for UI clarity
- ESLint for code quality checks

---

## Architecture

### Backend modules

`backend/app/` contains:

- `api/` — FastAPI routes for ingestion, compliance, health, and analytics
- `agents/` — policy retrieval, risk assessment, recommendation, compliance answer generation, and scraping
- `core/` — configuration, constants, exception handling, app metadata
- `database/` — provider wrappers for local and external stores
- `ingestion/` — text cleaning, chunking, link enrichment, loader utilities
- `retrieval/` — hybrid semantic retrieval and reranking
- `services/` — higher-level facade services such as LLM and retrieval
- `utils/` — citation formatting, document helpers, link extraction, retry helpers

### Frontend structure

`frontend/src/` contains the UI entrypoint and components that consume the backend API.
The app is designed to call the backend at `http://localhost:8000/api/v1` by default.

### Data flow

1. A policy document or text is ingested.
2. The text is cleaned, chunked, and optionally enriched with scraped link evidence.
3. Chunks are saved in the local JSON store or MongoDB.
4. Chunk embeddings are created locally or via OpenRouter.
5. Chunks are indexed into an in-memory vector index or external Weaviate.
6. A query triggers hybrid retrieval (vector search + rerank).
7. Risk is assessed using keyword taxonomy and evidence counts.
8. Recommendations and a compliance answer are returned.

---

## Provider fallback and environment configuration

The backend is configured in `backend/app/core/config.py` and reads values from `backend/.env`.

### Supported provider switches

| Provider area   | Local fallback                 | Optional provider | Env variable              |
| --------------- | ------------------------------ | ----------------- | ------------------------- |
| LLM             | local template answer          | openrouter        | `LLM_PROVIDER`            |
| Embeddings      | deterministic local embeddings | openrouter        | `EMBEDDING_PROVIDER`      |
| Document store  | local JSON                     | mongodb           | `DOCUMENT_STORE_PROVIDER` |
| Cache           | local in-memory                | upstash           | `CACHE_PROVIDER`          |
| Knowledge graph | local in-memory                | neo4j             | `GRAPH_PROVIDER`          |
| Vector store    | local cosine search            | weaviate          | `VECTOR_STORE_PROVIDER`   |

### Example fallback behavior

- `OPENROUTER_API_KEY` missing when `LLM_PROVIDER=openrouter` means the system logs a warning and falls back to local answer synthesis.
- `OPENROUTER_API_KEY` missing when `EMBEDDING_PROVIDER=openrouter` means the system falls back to deterministic embeddings.
- `CACHE_PROVIDER=local` uses an in-memory store, while `upstash` uses HTTP REST calls to Upstash Redis.
- `DOCUMENT_STORE_PROVIDER=local` stores policies in JSON; `mongodb` persists them to MongoDB.
- `VECTOR_STORE_PROVIDER=local` embeds chunks and calculates cosine similarity in Python; `weaviate` delegates search to Weaviate.
- `GRAPH_PROVIDER=local` keeps a simple in-memory relation map; `neo4j` persists graph entities.

### Core settings worth knowing

- `risk_threshold_high=0.72`
- `risk_threshold_medium=0.42`
- `enable_link_scraping=true`
- `max_scraped_links=5`
- `chunk_size=900`
- `chunk_overlap=150`
- `retrieval_top_k=6`

---

## Why these technologies were chosen

### FastAPI

- Fast startup and async support
- Auto-generated Swagger docs
- Good fit for a service that exposes structured agent workflows

### Pydantic / Settings

- Strong typed configuration from env variables
- Easy validation of provider URLs and optional credentials

### Local data providers

- Simplifies onboarding and proof-of-concept usage
- Supports offline experimentation
- Avoids forcing database or cloud dependencies for basic use

### OpenRouter support

- Vendor-agnostic way to call modern LLM/embedding models
- You can choose any compatible model without changing backend logic

### React + Vite + Tailwind

- Lightweight, fast frontend developer experience
- Minimal build complexity with modern defaults
- Easy to extend into a production UI

### LangChain / LangGraph

- Supports structured tool-based orchestration
- Makes the risk/recommendation/answer workflow explicit and extensible

### Optional persistence providers

- MongoDB for reliable document and chunk storage
- Weaviate for scalable semantic vector search
- Neo4j for knowledge graph exploration and relationships
- Upstash for a cloud-ready cache without provisioning infrastructure

---

## How to run

### Backend setup

1. Change into the backend folder:

```bash
cd backend
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Create and configure `backend/.env`.

4. Start the API server:

```bash
uvicorn app.main:app --reload
```

5. Open the API docs at:

```text
http://localhost:8000/docs
```

### Frontend setup

1. Change into the frontend folder:

```bash
cd frontend
```

2. Install npm dependencies:

```bash
npm install
```

3. Optionally configure the API base URL in `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

4. Start the dev server:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

5. Open the UI at:

```text
http://127.0.0.1:5173
```

### Running tests

Backend tests:

```bash
cd backend
python -m unittest discover -s tests -p "test_*.py"
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

---

## API surface

The backend exposes:

- `GET /api/v1/health`
- `POST /api/v1/ingestion/text`
- `POST /api/v1/ingestion/files`
- `POST /api/v1/compliance/search`
- `POST /api/v1/compliance/check`
- `GET /api/v1/compliance/analytics`
- `GET /metrics`

The root endpoint also returns app metadata:

- `GET /`

---

## Ingestion and retrieval details

### Document ingestion

- Accepts uploaded policy files or raw text
- Cleans and normalizes text
- Extracts links and optionally scrapes linked content for extra evidence
- Chunks documents into overlapping segments for semantic search
- Saves chunks to the chosen document store
- Indexes chunks for semantic retrieval
- Updates a knowledge graph for policy relationships

### Hybrid retrieval

- Performs vector-based retrieval followed by reranking
- Uses local or external embeddings depending on provider
- Filters by policy type when requested
- Returns citations with chunk excerpts and scores

### Risk assessment

- Uses keyword taxonomy defined in `backend/app/core/constants.py`
- Computes high-risk and medium-risk signal counts
- Uses a score formula and thresholds from settings
- Assigns `low`, `medium`, or `high` risk

### Compliance answer generation

- Tries an external LLM via OpenRouter when configured
- If external LLM is unavailable, falls back to a local synthesized answer
- Always returns evidence citations and a recommendation

---

## Useful files and folders

- `backend/README.md` — backend-specific run and provider notes
- `frontend/README.md` — frontend-specific run and package notes
- `backend/app/core/config.py` — environment configuration and provider switches
- `backend/app/core/constants.py` — risk keywords and taxonomy
- `backend/app/agents/` — core AI agent workflows
- `backend/app/database/` — storage provider wrappers and fallback implementations
- `backend/app/ingestion/` — document processing pipeline
- `backend/app/retrieval/` — search and reranking logic
- `backend/tests/` — unit and integration tests
- `backend/docs/` — architecture, API, and deployment documentation

---

## Recommended next steps

- Start with local mode first by leaving providers as `local` in `.env`
- Ingest a sample policy document using the backend API
- Query the compliance endpoint and review returned risk/recommendations
- Add OpenRouter credentials only when you need better generated answers or high-quality embeddings
- Add MongoDB / Weaviate / Neo4j only when you need persistence, scale, or graph relationships

---

## Notes

This project is built to support rapid experimentation with policy compliance intelligence while remaining usable without cloud dependencies. The local fallback design makes it a strong base for prototyping, while provider switches make it ready to scale into production-ready external capability.
