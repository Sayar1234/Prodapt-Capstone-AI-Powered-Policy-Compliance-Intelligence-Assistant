# AI-Powered Policy Compliance Intelligence Backend

FastAPI backend for ingesting policy documents, retrieving cited evidence, and producing compliance/risk guidance.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`; interactive docs are at `/docs`.

## Tests and Benchmarks

Run the standard-library test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Run deterministic evaluation benchmarks:

```bash
python scripts/run_benchmarks.py
```

The evaluation layer includes DeepEval-compatible custom metrics for compliance keyword recall and citation groundedness. These metrics are deterministic and can run without a live LLM judge.

## Link Scraping

Ingested documents are scanned for `http://` and `https://` links. When `ENABLE_LINK_SCRAPING=true`, the backend attempts to fetch readable text from those pages and appends it as linked evidence before chunking and indexing.

```env
ENABLE_LINK_SCRAPING=true
SCRAPE_TIMEOUT_SECONDS=8
MAX_SCRAPED_LINKS=5
MAX_SCRAPED_CHARS_PER_LINK=5000
```

Scraping is best-effort: failed links, blocked pages, and unsupported content types do not fail ingestion.

## Agent Orchestration

The backend wraps the individual agent steps as LangChain structured tools:

- `retrieve_policy_evidence`
- `assess_policy_risk`
- `recommend_compliance_actions`
- `synthesize_compliance_answer`

LangGraph orchestrates those tools as:

```text
guardrails
  -> blocked_response
  -> retrieve_evidence
  -> assess_risk
  -> recommend_actions
  -> synthesize_answer
```

The public API still calls `ComplianceOrchestrator.check(...)`, but the internal workflow is now graph-based when `langgraph` is installed.

## Environment

No paid API key is required for local fallback mode. Fill `backend/.env` when you want external services.

Required only for external AI through OpenRouter:

- `OPENROUTER_API_KEY`: needed if `LLM_PROVIDER=openrouter` or `EMBEDDING_PROVIDER=openrouter`.
- `OPENROUTER_MODEL`: the chat model to use, for example `openai/gpt-4o-mini`, `anthropic/claude-3.5-sonnet`, or another OpenRouter model id.
- `OPENROUTER_BASE_URL`: defaults to `https://openrouter.ai/api/v1`.
- `OPENROUTER_SITE_URL` and `OPENROUTER_APP_NAME`: optional OpenRouter attribution headers.

Required only for external storage/services:

- `MONGODB_URI`: needed if `DOCUMENT_STORE_PROVIDER=mongodb`.
- `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`: needed if `CACHE_PROVIDER=upstash`.
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: needed if `GRAPH_PROVIDER=neo4j`.
- `WEAVIATE_URL`, `WEAVIATE_API_KEY`: needed if `VECTOR_STORE_PROVIDER=weaviate`.

Keep all providers as `local` to run without keys. See `.env.example` for the full template.

### Upstash Redis

Upstash Redis is only needed if you want a real shared cache instead of the local in-memory fallback. For development, keep:

```env
CACHE_PROVIDER="local"
UPSTASH_REDIS_REST_URL=""
UPSTASH_REDIS_REST_TOKEN=""
```

For Upstash, open your Upstash Redis database dashboard and copy the REST credentials:

```env
CACHE_PROVIDER="upstash"
UPSTASH_REDIS_REST_URL="https://your-database-name.upstash.io"
UPSTASH_REDIS_REST_TOKEN="your-upstash-rest-token"
```

Use the REST URL/token pair, not the standard `redis://` connection string.

### Minimal OpenRouter Setup

To use OpenRouter for LLM calls later:

```env
LLM_PROVIDER="openrouter"
OPENROUTER_API_KEY="sk-or-v1-your-key-here"
OPENROUTER_MODEL="openai/gpt-4o-mini"
```

Leave `EMBEDDING_PROVIDER="local"` unless you specifically choose an OpenRouter model/route that supports embeddings.

### Provider Switches

The backend now supports real external providers. Keep a provider as `local` until its credentials are filled.

```env
DOCUMENT_STORE_PROVIDER="mongodb"
MONGODB_URI="mongodb+srv://user:password@cluster.example.mongodb.net/?retryWrites=true&w=majority"

GRAPH_PROVIDER="neo4j"
NEO4J_URI="neo4j+s://your-database.databases.neo4j.io"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-password"

VECTOR_STORE_PROVIDER="weaviate"
WEAVIATE_URL="https://your-cluster.weaviate.network"
WEAVIATE_API_KEY="your-weaviate-key"
WEAVIATE_COLLECTION="PolicyChunk"
```

When these are enabled, ingestion persists documents/chunks to MongoDB, writes graph relationships to Neo4j, and indexes/searches chunks in Weaviate.

## Main endpoints

- `GET /api/v1/health`
- `POST /api/v1/ingestion/text`
- `POST /api/v1/ingestion/files`
- `POST /api/v1/compliance/search`
- `POST /api/v1/compliance/check`
- `GET /api/v1/compliance/analytics`
- `GET /metrics`
