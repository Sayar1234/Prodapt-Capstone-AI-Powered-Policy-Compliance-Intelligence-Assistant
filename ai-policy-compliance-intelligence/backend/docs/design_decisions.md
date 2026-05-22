# Design Decisions & Trade-offs

This document articulates the key system design decisions made in the AI-Powered Policy Compliance Intelligence Assistant, their rationale, and the trade-offs involved.

---

## 1. Vector Database Selection: Pluggable Weaviate + Local Fallback

### Decision

The system supports two vector storage strategies:

- **Local**: In-memory deterministic embeddings (SHA256-based hashing of tokens) + cosine similarity search.
- **Weaviate**: Cloud-hosted or self-managed GraphQL-based vector database with native support for semantic search and filtering.

Selected via environment variable `VECTOR_STORE_PROVIDER` (`local` or `weaviate`).

### Rationale

1. **Local-first philosophy**: Policy documents in compliance systems are often sensitive and org-specific. Local deterministic embeddings ensure no external calls or data exposure during proof-of-concept or air-gapped deployments.
2. **Deterministic embeddings** (SHA256 hashing): Reproducible across runs and require zero external dependencies; perfect for testing and development.
3. **Weaviate for scale**: Weaviate provides sophisticated filtering (e.g., by policy_type), custom reranking, and production-grade indexing without managing infrastructure complexity (managed cloud option available).

### Trade-offs

| Aspect                     | Local Deterministic                                | Weaviate                                                      |
| -------------------------- | -------------------------------------------------- | ------------------------------------------------------------- |
| **Quality of embeddings**  | Lower (heuristic-based, no semantic understanding) | Higher (neural embeddings, semantic relevance)                |
| **Search latency**         | Fast (in-process, no network)                      | Slower (HTTP round-trip, but sub-second at scale)             |
| **Scalability**            | Limited to local memory; poor for 100k+ chunks     | Excellent; designed for millions of vectors                   |
| **Cost**                   | Free                                               | SaaS pricing (~$20/mo starter, more for larger clusters)      |
| **Setup complexity**       | None (built-in)                                    | Moderate (provision cloud instance or self-host)              |
| **Deployment flexibility** | Works anywhere, no external service                | Requires external service; harder for air-gapped environments |

### Alternatives Considered

- **Pinecone**: Simpler REST API but vendor lock-in and fewer filtering options than Weaviate.
- **Milvus**: Open-source, but requires separate service deployment; more operational burden than Weaviate's managed option.
- **LLM embeddings only (no reranking)**: Simpler; rejected because policy compliance requires precision — reranking improves recall significantly.

### Decision Justification

The pluggable architecture allows organizations to start with `local` mode (zero cost, fast iteration) and graduate to Weaviate (or other providers) only when retrieval quality or scale demands it. This aligns with the "local-first fallback" design principle of the entire system.

---

## 2. Chunking Strategy: Word-Based Overlap with 900/150 Defaults

### Decision

Policy documents are chunked using a **sliding-window strategy**:

- **Unit**: Words (split on whitespace).
- **Default chunk size**: 900 words (~3–4 KB of typical policy text).
- **Default overlap**: 150 words (~20% of chunk size).
- **Configurable**: Both are environment variables in `CHUNK_SIZE` and `CHUNK_OVERLAP`.

Implemented in `backend/app/ingestion/chunker.py`.

### Rationale

1. **Word-based (not character/token-based)**:
   - Simple and language-agnostic (works for English, multi-language documents).
   - Avoids tokenizer complexity and inconsistencies across LLM models.
   - Preserves semantic boundaries better than fixed-character chunking.

2. **900-word default**:
   - Typical policy section fits within one chunk, preserving context.
   - Balances embedding efficiency: large enough to be meaningful, small enough to embed quickly.
   - ~3–4 KB per chunk; reasonable for vector databases and LLM token limits.

3. **150-word overlap (20%)**:
   - Ensures continuity across chunk boundaries (e.g., a policy rule split at chunk end appears in both chunks).
   - Reduces false negatives in semantic search (a query matching the boundary is more likely to be found).
   - Modest memory/indexing overhead (20% redundant data).

### Trade-offs

| Aspect                  | Larger chunks (e.g., 2000 words)          | Smaller chunks (e.g., 300 words)    |
| ----------------------- | ----------------------------------------- | ----------------------------------- |
| **Context retention**   | Better; full policy sections in one chunk | Worse; may lose surrounding context |
| **Search precision**    | Balanced (less granular results)          | Higher (more targeted results)      |
| **Indexing overhead**   | Lower (fewer vectors to store/search)     | Higher (more vectors, more storage) |
| **Latency**             | Faster retrieval (fewer comparisons)      | Slower (more vectors to rank)       |
| **LLM context windows** | Risk exceeding token limit                | Safe; fewer tokens per chunk        |

### Alternatives Considered

- **Semantic chunking** (e.g., via LLM or sentence embeddings): More intelligent but computationally expensive and non-deterministic. Rejected for local-first simplicity.
- **Fixed character size (e.g., 1024 chars)**: Simpler but language-agnostic and risks breaking mid-word or mid-sentence. Word-based is cleaner.
- **No overlap**: Simpler but loses context at boundaries; rejected due to missed retrieval opportunities.

### Decision Justification

The 900/150 default is empirically justified for policy documents:

- Policies typically use formal language with ~150 words per paragraph.
- 900 words = 6 paragraphs ≈ one policy section or control requirement.
- 20% overlap is a conservative compromise: meaningful boundary preservation without excessive redundancy.

The configurability ensures adaptability for specialized use cases (e.g., structured regulatory tables might benefit from 500-word chunks).

---

## 3. Hybrid Search: Vector + Lexical Reranking vs Semantic-Only

### Decision

The system uses **hybrid retrieval**:

1. **Vector search** (semantic): Retrieve top-k\*3 candidates using embeddings similarity.
2. **Rerank** (hybrid): Re-score candidates using a blend of:
   - **Vector score** (65% weight): Semantic relevance from embeddings.
   - **Lexical overlap** (35% weight): Term frequency intersection between query and chunk.

Final top-k results returned. Implemented in `backend/app/retrieval/hybrid_search.py` and `reranker.py`.

### Rationale

1. **Semantic search alone** is insufficient for policy compliance:
   - Policies use consistent terminology (e.g., "multi-factor authentication" vs "MFA" vs "2FA").
   - Exact keyword presence is critical (e.g., query "bypass approval" must match chunks explicitly mentioning "bypass").
   - Neural embeddings may generalize too much, conflating unrelated concepts.

2. **Hybrid approach balances recall and precision**:
   - **Recall**: Vector search (semantic) finds related content even if keywords differ.
   - **Precision**: Lexical reranking prioritizes chunks with explicit query term matches.
   - **Trade-off**: Lexical-only search (Boolean) misses paraphrased content; semantic-only misses exact terms.

3. **Reranking formula** (65% vector + 35% lexical):
   - Weighted toward semantic (65%) because policy text is often tightly written; synonyms matter less than in natural conversation.
   - Lexical boost (35%) catches exact terminology critical for compliance ("without approval", "encryption", "audit").
   - Weights are configurable in code; could be tuned per domain.

### Trade-offs

| Aspect                              | Semantic-Only                                         | Hybrid (Vector + Lexical)                 | Lexical-Only (Boolean)               |
| ----------------------------------- | ----------------------------------------------------- | ----------------------------------------- | ------------------------------------ |
| **Handling paraphrases**            | Excellent; "MFA required" matches "multi-factor auth" | Good; catches both                        | Poor; misses paraphrases             |
| **Precision (few false positives)** | Moderate; may match loose semantic neighbors          | Excellent; lexical filter reduces noise   | Excellent (strict matching)          |
| **Handling synonyms**               | Excellent                                             | Good                                      | Poor                                 |
| **Compliance edge cases**           | Risky; may miss negations ("no approval required")    | Better; lexical catches negations         | Good if policy uses consistent terms |
| **Computational cost**              | Low (vector search only)                              | Moderate (two-stage retrieval)            | Low (simple substring matching)      |
| **Tuning complexity**               | Low (model-dependent)                                 | Moderate (weight tuning, overlap formula) | High (many Boolean rules)            |

### Alternatives Considered

- **LLM-based reranking** (e.g., "rank these chunks for relevance"): High quality but expensive (~0.01–0.05 sec per query + cost). Rejected for latency and cost.
- **Multi-stage dense retrieval** (e.g., ColBERT): Strong results but requires additional indexing infrastructure. Complexity not justified for initial MVP.
- **Query expansion** (e.g., "expand query with synonyms then search"): Helps recall but doesn't address precision; used as complement, not replacement.

### Decision Justification

For policy compliance, **false negatives (missed relevant policies) are worse than false positives (returned irrelevant ones)**. A human reviewer can quickly dismiss irrelevant results, but missed policy citations could lead to compliance violations. Hybrid search achieves high recall (semantic) while maintaining precision (lexical), making it the best fit for risk-averse compliance use cases.

---

## 4. Agent Orchestration: LangGraph with Fallback

### Decision

Policy compliance checks are orchestrated via a **state machine graph** (when LangGraph/LangChain available):

1. **Entry**: Guardrails screening (block malicious queries).
2. **Retrieval**: Vector + reranking for citations.
3. **Risk assessment**: Keyword taxonomy + evidence scoring.
4. **Recommendations**: Risk-level-based suggested actions.
5. **Synthesis**: LLM-based or local fallback answer generation.

Implemented in `backend/app/agents/orchestrator.py` using `langgraph.graph.StateGraph`. Falls back to sequential in-process execution if LangGraph is unavailable.

### Rationale

1. **Graph-based orchestration** (vs sequential function calls):
   - **Explicit state**: Each node reads/writes typed state (ComplianceGraphState).
   - **Auditability**: Graph structure is introspectable; useful for compliance logging and debugging.
   - **Extensibility**: New nodes (e.g., "escalate to legal") can be inserted easily.
   - **LangGraph ecosystem**: Integrates with LangChain tools, supports async/concurrency out-of-the-box.

2. **Conditional routing** (guardrails → retrieval):
   - Blocked queries never reach retrieval (security).
   - Reduces unnecessary compute for malicious inputs.

3. **Fallback to sequential** (if LangGraph unavailable):
   - Ensures the system runs even if LangGraph/LangChain aren't installed.
   - Maintains feature parity (same outputs, deterministic order).

### Trade-offs

| Aspect                   | LangGraph State Machine                | Sequential Function Pipeline          | Reactive Event System                |
| ------------------------ | -------------------------------------- | ------------------------------------- | ------------------------------------ |
| **Complexity**           | Higher; requires graph definition      | Lower; simple function calls          | Higher; event handlers               |
| **Debuggability**        | Better; state visible at each node     | Good; linear flow easy to trace       | Harder; async callbacks obscure flow |
| **Parallelization**      | Possible (nodes can run concurrently)  | Difficult (requires async refactor)   | Natural (event-driven)               |
| **Error handling**       | Structured (per-node try/catch)        | Simpler (single error propagation)    | Complex (error routing)              |
| **Monitoring/logging**   | Excellent (introspectable graph state) | Adequate (linear traces)              | Challenging (distributed tracing)    |
| **Production readiness** | High (production-grade orchestration)  | Lower (may need refactoring at scale) | Medium (depends on framework)        |

### Alternatives Considered

- **Simple sequential pipeline**: Simplest, but no auditability or easy extension. Rejected for compliance use case (audit trails critical).
- **Event-driven architecture** (Kafka, RabbitMQ): Overkill for single-machine MVP. Complexity not justified until multi-service decomposition.
- **Temporal Workflows** (Temporal.io): Excellent for distributed workflows but introduces operational complexity (separate service). Rejected for MVP.

### Decision Justification

For policy compliance, **auditability and control flow clarity are paramount**. LangGraph's state machine provides both, with a graceful fallback ensuring the system works even in minimal environments. As the system scales (e.g., workflow involves external reviews or approvals), the graph structure naturally extends to support those stages.

---

## 5. Guardrail Design: Keyword-Based Screening for Compliance Accuracy

### Decision

User queries are screened via simple **phrase-based guardrails** before processing:

- **Implementation**: `screen_user_text()` checks for blocked phrases (e.g., "ignore previous instructions", "reveal system prompt").
- **Scope**: Prevents prompt injection and off-policy queries.
- **Blocked response**: If query fails guardrails, return high-risk status with "Request blocked by safety guardrails" message.
- **Location**: `backend/app/security/guardrails.py`; invoked as the first node in the orchestration graph.

### Rationale

1. **Phrase-based screening** (vs full NLP/classifier):
   - Simple, deterministic, and fast (regex-like pattern matching).
   - No external ML model calls; works offline.
   - Transparent (easy to audit the blocked phrases).

2. **Early exit on block**: Guardrails run **first** in the orchestration graph, preventing wasted retrieval/inference compute on malicious queries.

3. **Conservative design**: Better to block a few legitimate queries than allow risky ones in a compliance system. Users can rephrase blocked queries.

### Trade-offs

| Aspect              | Keyword Guardrails                     | ML Classifier (BERT, etc.)  | LLM Judgment                |
| ------------------- | -------------------------------------- | --------------------------- | --------------------------- |
| **Precision**       | Lower; phrase lists are brittle        | Higher; learns context      | Highest; understands nuance |
| **False negatives** | Higher; misses paraphrased attacks     | Lower                       | Lowest                      |
| **Speed**           | Sub-millisecond (O(n) string matching) | 100–500ms (model inference) | 500ms–5s (LLM call)         |
| **Cost**            | Free                                   | Moderate (model serving)    | High (LLM API calls)        |
| **Debuggability**   | Excellent (inspect phrase list)        | Good (attention weights)    | Poor (black box)            |
| **Deployment**      | Any environment (no dependencies)      | Requires ML infrastructure  | External API dependency     |
| **False positives** | Possible; may block legitimate queries | Rare                        | Rare but possible           |

### Alternatives Considered

- **No guardrails**: Risky; allows prompt injection and off-topic queries. Rejected immediately.
- **ML-based classification** (e.g., "toxic language detector"): Better precision but slow and costly. Deferred to future work if false positives become a problem.
- **LLM-based judgment** ("Ask GPT if this query is compliant"): Defeats the purpose of local-first design; adds latency and cost.

### Current Guardrails Blocklist

```python
BLOCKED_PHRASES = [
    "ignore previous instructions",
    "reveal system prompt",
    "exfiltrate",
]
```

Minimal but extendable.

### Decision Justification

For an MVP compliance system, **simplicity and speed win**. Phrase-based guardrails block obvious attacks (prompt injection) with near-zero latency. As the system matures and usage patterns emerge, this can evolve to ML-based screening or more sophisticated heuristics. The current design is a baseline that ensures core compliance integrity without operational overhead.

---

## 6. Risk Scoring: Keyword Taxonomy + Evidence Boosting

### Decision

Policy compliance risk is assessed using a **deterministic keyword-based scoring algorithm** (not ML-based):

1. **Taxonomy tiers**:
   - 5 policy categories (privacy, security, finance, hr, operations) with category-specific keywords.
   - HIGH_RISK_TERMS (e.g., "breach", "personal data", "privileged access") — weighted 0.18 per hit.
   - MEDIUM_RISK_TERMS (e.g., "vendor", "audit", "retention") — weighted 0.08 per hit.
2. **Score formula**:
   ```
   score = (category_hits × 0.08) + (high_hits × 0.18) + (medium_hits × 0.08) + (negation_hits × 0.12) + evidence_boost
   ```

   - Capped at 1.0.
   - Thresholds: HIGH ≥ 0.72, MEDIUM ≥ 0.42, LOW < 0.42.
3. **Evidence boost**: +0.03 per citation (max +0.12 for 4+ citations).

Implemented in `backend/app/agents/risk_agent.py` and taxonomy in `backend/app/core/constants.py`.

### Rationale

1. **Deterministic & interpretable**: Every risk score is auditable and reproducible. No black-box ML model.
2. **Domain-aligned**: Weights reflect compliance risk (e.g., "breach" is riskier than "retention").
3. **No training data required**: No need for labeled compliance datasets; system works out-of-the-box.
4. **Fast**: Millisecond-level computation; no external API calls.
5. **Explainability**: Risk rationale includes hit counts and thresholds; users understand why a query is flagged high-risk.

### Trade-offs

| Aspect                | Keyword Taxonomy                     | ML Model (e.g., Logistic Regression)       | LLM-Based Judgment           |
| --------------------- | ------------------------------------ | ------------------------------------------ | ---------------------------- |
| **Accuracy**          | Moderate; depends on keyword quality | Higher; learns patterns from labeled data  | Highest; understands context |
| **Interpretability**  | Excellent; clear rules and weights   | Moderate; feature importance visible       | Poor; opaque LLM logic       |
| **Training cost**     | None                                 | High (labeled dataset creation + training) | None (but query cost)        |
| **Inference latency** | <1ms (O(n) keyword matching)         | 10–100ms (model inference)                 | 500ms–5s (LLM call)          |
| **Scalability**       | Unlimited (stateless)                | Limited by model server                    | Limited by LLM rate limits   |
| **Maintenance**       | Low (update keyword list)            | Moderate (retrain if patterns shift)       | Low (no training)            |
| **False negatives**   | Higher; misses novel risk patterns   | Lower                                      | Lowest                       |

### Alternatives Considered

- **ML classifier**: Strong accuracy but adds operational complexity (model training, retraining, version management). Deferred to Phase 2 if keyword taxonomy becomes insufficient.
- **Rule engine** (e.g., Drools): More expressive than keyword matching but overkill for current risk model. Keyword taxonomy is sufficient.
- **LLM-based risk**: "Ask GPT to assess risk" — contradicts local-first design and introduces latency/cost.

### Decision Justification

For an MVP, **deterministic keyword-based risk scoring is the right balance of accuracy, speed, and simplicity**. It provides tangible compliance value (risk flags + recommendations) with minimal infrastructure. As the system scales and processes more policy documents, the keyword taxonomy can be refined empirically (e.g., "which keywords correlate with actual compliance violations?"). This data can later inform an ML model, but the keyword baseline is sufficient now.

---

## Summary: Design Philosophy

The system embodies these principles:

1. **Local-first with optional scale**: Start simple (deterministic, no external services); add external providers when needed.
2. **Auditability & transparency**: Every decision is logged and explainable (risk scores, retrieval citations, orchestration steps).
3. **Deterministic over ML**: For MVP, predictable keyword-based logic beats black-box models. ML can augment later.
4. **Pluggability**: Every major component (LLM, vector store, cache, graph) is swappable via environment configuration.
5. **Compliance-first**: Err on the side of caution; false positives are acceptable; false negatives (missed policies) are unacceptable.

These decisions prioritize **clarity, correctness, and auditability** over cutting-edge AI sophistication. As the system matures, each design can evolve to incorporate more advanced techniques while preserving backward compatibility and operational simplicity.
