# Architecture Overview

This document summarizes the architecture of the AI-Powered Policy Compliance Intelligence Assistant and provides a diagram you can use to generate a formal architecture diagram.

**High-level components**

- **Frontend**: React + TypeScript app (Vite) that calls the backend API at `/api/v1`.
- **API / Backend**: FastAPI application (run with `uvicorn app.main:app`) exposing ingestion, compliance, and analytics endpoints.
- **Agent Layer**: Structured agents and an orchestrator that coordinate retrieval, risk assessment, recommendation, and answer synthesis.
- **Services**: Logical services (ingestion, retrieval, compliance, analytics, LLM client) that implement business logic and call lower-level providers.
- **Data Providers (pluggable)**:
  - Document store: Local JSON fallback or MongoDB (`DOCUMENT_STORE_PROVIDER`)
  - Vector store: Local deterministic embeddings + in-memory cosine search or Weaviate (`VECTOR_STORE_PROVIDER`)
  - Cache: In-memory local cache or Upstash REST Redis (`CACHE_PROVIDER`)
  - Knowledge graph: Local in-memory graph or Neo4j (`GRAPH_PROVIDER`)
  - LLM / Embeddings provider: Local template/fallback or OpenRouter (`LLM_PROVIDER`, `EMBEDDING_PROVIDER`)
- **External HTTP integrations**: OpenRouter (LLM & embeddings), Upstash (REST Redis), Weaviate (HTTP API), Neo4j (Bolt/HTTP), third-party web sites (link scraping via HTTP).

**Primary protocols**

- HTTP/HTTPS: Frontend ↔ Backend, Backend ↔ OpenRouter/Weaviate/Upstash/Weaviate GraphQL/Weaviate REST, link scraping.
- MongoDB driver (pymongo): Backend ↔ MongoDB when `DOCUMENT_STORE_PROVIDER=mongodb`.
- Neo4j driver (neo4j): Backend ↔ Neo4j when `GRAPH_PROVIDER=neo4j`.

**Mermaid diagram (high-level)**

```mermaid
graph LR
  User[User / Browser]
  FE[Frontend (React + Vite)]
  API[Backend (FastAPI / Uvicorn)]
  Agents[Agents & Orchestrator (Retrieval, Risk, Recommendation, Synthesis)]
  Tools[Agent Tools]
  LLM[LLM Provider\n(OpenRouter or Local)]
  DocStore[Document Store\n(JSON local or MongoDB)]
  VectorStore[Vector Store\n(Local embeddings or Weaviate)]
  Cache[Cache\n(Local or Upstash REST Redis)]
  Graph[Knowledge Graph\n(Local or Neo4j)]
  External[Websites (link scraping)]

  User --> FE -->|HTTP| API
  API --> Agents --> Tools
  Tools --> VectorStore
  Tools --> DocStore
  Tools --> Cache
  Tools --> Graph
  Tools --> LLM
  Tools --> External

  subgraph ExternalServices
    LLM
    DocStore
    VectorStore
    Cache
    Graph
  end
```

**Where responsibilities live**

- Frontend: UI, request composition to `/api/v1`.
- FastAPI: request validation, dependency wiring, route handlers under `backend/app/api/routes`.
- Services: `backend/app/services/*` (ingestion, retrieval, compliance, analytics).
- Agents: `backend/app/agents/*` (orchestrator, retrieval_agent, risk_agent, recommendation_agent, compliance_agent, scraping_agent).
- Persistence and provider adapters: `backend/app/database/*` (mongodb.py, weaviate.py, neo4j.py, redis.py) and local fallbacks in same modules.
- Retrieval stack: `backend/app/retrieval/*` (vector_search, hybrid_search, reranker, filters).
- Ingestion pipeline: `backend/app/ingestion/*` (loaders, cleaner, chunker, embeddings).

**Notes & design considerations**

- Provider switches are configured in `backend/.env` and `backend/app/core/config.py` (e.g. `VECTOR_STORE_PROVIDER`, `DOCUMENT_STORE_PROVIDER`, `LLM_PROVIDER`).
- The system is local-first: if external provider credentials are missing or calls fail, the code falls back to deterministic/local implementations.
- Agents may optionally use `langgraph` / `langchain` integration when those packages are installed; otherwise the orchestrator falls back to a simple in-process flow.

For diagram generation: use the mermaid graph above and expand boxes into sub-components (API routers, services, databases, external providers). Include dashed lines for optional/external services.
