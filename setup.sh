#!/bin/bash

# ==========================================
# AI Policy Compliance Intelligence Scaffold
# ==========================================

PROJECT="ai-policy-compliance-intelligence"

echo "Creating project structure..."

# Root
mkdir -p $PROJECT
cd $PROJECT || exit

# ---------------- BACKEND ----------------

mkdir -p backend/app/{api/routes,agents,ingestion,retrieval,database,services,models,prompts,security,evaluation,observability,utils,core}

mkdir -p backend/tests/{unit,integration,e2e}

mkdir -p backend/scripts

mkdir -p backend/data/{raw,processed,embeddings}

mkdir -p backend/docker

# ---------------- FRONTEND ----------------

mkdir -p frontend

# ---------------- DOCS ----------------

mkdir -p docs/{architecture,api,deployment}

# ---------------- API ----------------

touch backend/app/api/routes/{compliance.py,ingestion.py,health.py}
touch backend/app/api/dependencies.py

# ---------------- AGENTS ----------------

touch backend/app/agents/{retrieval_agent.py,compliance_agent.py,risk_agent.py,recommendation_agent.py,orchestrator.py}

# ---------------- INGESTION ----------------

touch backend/app/ingestion/{loaders.py,cleaner.py,chunker.py,embeddings.py,pipeline.py}

# ---------------- RETRIEVAL ----------------

touch backend/app/retrieval/{vector_search.py,hybrid_search.py,reranker.py,filters.py}

# ---------------- DATABASE ----------------

touch backend/app/database/{mongodb.py,weaviate.py,neo4j.py,redis.py}

# ---------------- SERVICES ----------------

touch backend/app/services/{compliance_service.py,ingestion_service.py,retrieval_service.py,analytics_service.py}

# ---------------- MODELS ----------------

touch backend/app/models/{request_models.py,response_models.py,domain_models.py}

# ---------------- PROMPTS ----------------

touch backend/app/prompts/{compliance_prompts.py,risk_prompts.py,guardrails.py}

# ---------------- SECURITY ----------------

touch backend/app/security/{validators.py,guardrails.py}

# ---------------- EVALUATION ----------------

touch backend/app/evaluation/{evaluators.py,benchmarks.py,metrics.py}

# ---------------- OBSERVABILITY ----------------

touch backend/app/observability/{logging.py,monitoring.py,telemetry.py}

# ---------------- UTILS ----------------

touch backend/app/utils/{document_utils.py,citation_utils.py,retry_utils.py}

# ---------------- CORE ----------------

touch backend/app/core/{config.py,constants.py,exceptions.py}

# ---------------- MAIN ----------------

touch backend/app/main.py

# ---------------- TESTS ----------------

touch backend/tests/unit/.gitkeep
touch backend/tests/integration/.gitkeep
touch backend/tests/e2e/.gitkeep

# ---------------- SCRIPTS ----------------

touch backend/scripts/{ingest_documents.py,run_benchmarks.py}

# ---------------- DATA ----------------

touch backend/data/raw/.gitkeep
touch backend/data/processed/.gitkeep
touch backend/data/embeddings/.gitkeep

# ---------------- DOCKER ----------------

touch backend/docker/{fastapi.Dockerfile,docker-compose.yml}

# ---------------- ROOT FILES ----------------

touch backend/requirements.txt
touch backend/.env
touch backend/README.md

touch .gitignore
touch LICENSE

echo "Project structure created successfully!"