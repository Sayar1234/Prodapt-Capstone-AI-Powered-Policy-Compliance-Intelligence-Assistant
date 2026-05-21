from pathlib import Path

from app.agents.scraping_agent import ScrapingAgent
from app.core.config import get_settings
from app.database.mongodb import store
from app.database.neo4j import knowledge_graph
from app.database.weaviate import vector_index
from app.ingestion.chunker import build_chunks
from app.ingestion.cleaner import clean_document_text
from app.ingestion.loaders import load_file_text
from app.models.domain_models import IngestionResult, PolicyDocument
from app.security.validators import sanitize_policy_type
from app.utils.link_utils import extract_links


def ingest_text(title: str, text: str, source: str, policy_type: str = "general", metadata: dict | None = None) -> IngestionResult:
    metadata = dict(metadata or {})
    cleaned_text = clean_document_text(text)
    enriched_text, scraped_links = enrich_with_link_evidence(cleaned_text)
    if scraped_links:
        metadata["scraped_links"] = scraped_links

    document = PolicyDocument(
        title=title,
        source=source,
        policy_type=sanitize_policy_type(policy_type),
        text=enriched_text,
        metadata=metadata,
    )
    chunks = build_chunks(document)
    store.save_document(document, chunks)
    vector_index.index_chunks(chunks)
    knowledge_graph.upsert_document_chunks(chunks)
    return IngestionResult(document_id=document.id, title=document.title, chunks_created=len(chunks), policy_type=document.policy_type)


def ingest_file(path: Path, policy_type: str = "general", metadata: dict | None = None) -> IngestionResult:
    text = load_file_text(path)
    return ingest_text(path.stem, text, str(path), policy_type, metadata)


def enrich_with_link_evidence(text: str) -> tuple[str, list[dict[str, str]]]:
    settings = get_settings()
    if not settings.enable_link_scraping:
        return text, []

    links = extract_links(text, limit=settings.max_scraped_links)
    if not links:
        return text, []

    scraped_links = ScrapingAgent().scrape_many(links)
    sections = []
    for item in scraped_links:
        if item.get("status") != "ok" or not item.get("text"):
            continue
        title = item.get("title") or item["url"]
        sections.append(f"Linked source: {title}\nURL: {item['url']}\n{item['text']}")

    if not sections:
        return text, scraped_links
    return f"{text}\n\nLinked Evidence\n" + "\n\n".join(sections), scraped_links
