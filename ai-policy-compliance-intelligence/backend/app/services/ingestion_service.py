from pathlib import Path

from app.ingestion.pipeline import ingest_file, ingest_text
from app.models.domain_models import IngestionResult


class IngestionService:
    def ingest_text_document(self, title: str, text: str, source: str, policy_type: str, metadata: dict | None = None) -> IngestionResult:
        return ingest_text(title=title, text=text, source=source, policy_type=policy_type, metadata=metadata)

    def ingest_path(self, path: Path, policy_type: str = "general", metadata: dict | None = None) -> IngestionResult:
        return ingest_file(path=path, policy_type=policy_type, metadata=metadata)
