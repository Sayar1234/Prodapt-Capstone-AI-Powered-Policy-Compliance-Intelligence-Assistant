# Operations Guide

This operations guide covers local development, production considerations, configuration, health checks, monitoring, backups, and common troubleshooting steps for the backend.

## Run & Development

- Create a Python 3.11 virtual environment and install deps:

```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

- Start the API locally:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Frontend (from workspace root):

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Configuration (environment variables)

Primary configuration is in `backend/.env` and `backend/app/core/config.py`.
Key env variables:

- `LLM_PROVIDER`, `EMBEDDING_PROVIDER` — `local` or `openrouter`.
- `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, model names.
- `DOCUMENT_STORE_PROVIDER` — `local` or `mongodb` (set `MONGODB_URI`, `MONGODB_DATABASE`).
- `CACHE_PROVIDER` — `local` or `upstash` (set `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`).
- `GRAPH_PROVIDER` — `local` or `neo4j` (set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`).
- `VECTOR_STORE_PROVIDER` — `local` or `weaviate` (set `WEAVIATE_URL`, `WEAVIATE_API_KEY`, `WEAVIATE_COLLECTION`).
- `CHUNK_SIZE`, `CHUNK_OVERLAP`, `RETRIEVAL_TOP_K`, `ENABLE_LINK_SCRAPING`, scraping timeouts.

## Health checks & endpoints

- `GET /api/v1/health` — returns service + provider statuses and cache health. Implemented in `backend/app/api/routes/health.py`.
- Prometheus metrics are optionally exposed if the Prometheus client is enabled in the codebase (see `backend/app/observability`).

## Persistence & Backups

- **MongoDB**: If `DOCUMENT_STORE_PROVIDER=mongodb`, backup/restore should follow standard MongoDB procedures (mongodump/mongorestore or managed provider snapshots).
- **Weaviate**: If using managed Weaviate, follow provider backup/restore. For local indexing, backup the local `backend/data/embeddings`+`processed/document_store.json` files.
- **Neo4j**: Back up via Neo4j tools or snapshots if `GRAPH_PROVIDER=neo4j`.

## Scaling considerations

- The app is synchronous in many parts; consider running behind Uvicorn/Gunicorn with multiple workers for higher concurrency.
- External providers (Weaviate, MongoDB, Neo4j, OpenRouter) should be provisioned for production throughput and availability.
- Cache (Upstash or Redis) reduces repeated LLM calls and heavy retrieval operations.

## Observability & Logging

- The codebase uses `structlog` and a Prometheus client (see `backend/app/observability/*`). Configure log level through `LOG_LEVEL` in `.env`.
- Instrument critical flows: ingestion, vector indexing, retrieval latency, LLM calls, and cache errors.

## Troubleshooting & Common Errors

- Missing API keys: If `OPENROUTER_API_KEY` or other provider keys are missing, the backend **falls back** to local deterministic implementations. Check logs for warnings like "falling back to local embeddings".
- MongoDB connection issues: ensure `MONGODB_URI` is reachable and the `pymongo` package is installed. Errors raise ValidationAppError with helpful messages.
- Upstash REST errors: `redis.py` uses the Upstash REST API — verify `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` are correct.
- Weaviate schema/index errors: `weaviate.py` will attempt to create the schema; network or permission issues are logged as warnings.
- Neo4j auth/connectivity: `neo4j.py` validates credentials at init and will raise a ValidationAppError if missing.

## Maintenance tasks

- Rebuild vector index: re-run ingestion for all documents or provide a maintenance script to re-index existing chunks (use `vector_index.index_chunks`).
- Recompute deterministic embeddings: embeddings are deterministic and can be recomputed from document text if needed.
- Cleanup local store: remove `backend/data/processed/document_store.json` and `backend/data/embeddings` to reset local state (not recommended in production).

## Backward compatibility and upgrades

- The data model is Pydantic; when changing model fields, migrate stored documents in MongoDB or local JSON accordingly.
- For production migrations, export and transform data to match new schemas, and re-index vectors if the embedding model or dimensions change.

## Emergency stop & safe mode

- If an external LLM or vector provider is failing, set `LLM_PROVIDER=local` and `VECTOR_STORE_PROVIDER=local` in `.env` to force local fallbacks and preserve availability.

## Useful commands

- Run backend tests:

```bash
cd backend
python -m unittest discover -s tests -p "test_*.py"
```

- Lint / format as per repository tooling (see frontend/backend readme sections).
