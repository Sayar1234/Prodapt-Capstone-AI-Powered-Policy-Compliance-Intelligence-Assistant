import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import ValidationAppError
from app.ingestion.embeddings import embed_text
from app.models.domain_models import DocumentChunk

logger = logging.getLogger(__name__)


class LocalVectorIndex:
    def embed(self, text: str) -> list[float]:
        return embed_text(text)

    def embed_chunks(self, chunks: list[DocumentChunk]) -> dict[str, list[float]]:
        return {chunk.id: self.embed(chunk.text) for chunk in chunks}

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        return None


class WeaviateVectorIndex(LocalVectorIndex):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.weaviate_url:
            raise ValidationAppError("Set WEAVIATE_URL when VECTOR_STORE_PROVIDER=weaviate")
        self.base_url = settings.weaviate_url.rstrip("/")
        self.collection = settings.weaviate_collection
        self.headers = {"Content-Type": "application/json"}
        if settings.weaviate_api_key:
            self.headers["Authorization"] = f"Bearer {settings.weaviate_api_key}"
        self._ensure_schema()

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return
        objects = []
        for chunk in chunks:
            objects.append(
                {
                    "class": self.collection,
                    "id": chunk.id,
                    "properties": self._properties(chunk),
                    "vector": self.embed(chunk.text),
                }
            )
        payload = {"objects": objects}
        with httpx.Client(timeout=30) as client:
            response = client.post(f"{self.base_url}/v1/batch/objects", headers=self.headers, json=payload)
            response.raise_for_status()

    def search(self, query: str, top_k: int, policy_type: str | None = None) -> list[tuple[DocumentChunk, float]]:
        vector = self.embed(query)
        where = ""
        if policy_type:
            where = f', where: {{path: ["policy_type"], operator: Equal, valueText: "{policy_type}"}}'
        graphql = {
            "query": f"""
            {{
              Get {{
                {self.collection}(nearVector: {{vector: {json.dumps(vector)}}}, limit: {top_k}{where}) {{
                  chunk_id
                  document_id
                  title
                  text
                  chunk_index
                  policy_type
                  source
                  metadata_json
                  _additional {{ distance certainty }}
                }}
              }}
            }}
            """
        }
        with httpx.Client(timeout=30) as client:
            response = client.post(f"{self.base_url}/v1/graphql", headers=self.headers, json=graphql)
            response.raise_for_status()
            payload = response.json()
        rows = payload.get("data", {}).get("Get", {}).get(self.collection, [])
        results: list[tuple[DocumentChunk, float]] = []
        for row in rows:
            additional = row.pop("_additional", {})
            metadata_json = row.pop("metadata_json", "{}") or "{}"
            chunk = DocumentChunk(
                id=row.pop("chunk_id"),
                metadata=json.loads(metadata_json),
                **row,
            )
            score = additional.get("certainty")
            if score is None:
                distance = additional.get("distance", 1.0)
                score = max(0.0, 1.0 - float(distance))
            results.append((chunk, float(score)))
        return results

    def _ensure_schema(self) -> None:
        schema = {
            "class": self.collection,
            "vectorizer": "none",
            "properties": [
                {"name": "chunk_id", "dataType": ["text"]},
                {"name": "document_id", "dataType": ["text"]},
                {"name": "title", "dataType": ["text"]},
                {"name": "text", "dataType": ["text"]},
                {"name": "chunk_index", "dataType": ["int"]},
                {"name": "policy_type", "dataType": ["text"]},
                {"name": "source", "dataType": ["text"]},
                {"name": "metadata_json", "dataType": ["text"]},
            ],
        }
        try:
            with httpx.Client(timeout=15) as client:
                response = client.get(f"{self.base_url}/v1/schema/{self.collection}", headers=self.headers)
                if response.status_code == 404:
                    client.post(f"{self.base_url}/v1/schema", headers=self.headers, json=schema).raise_for_status()
                else:
                    response.raise_for_status()
        except Exception as exc:
            logger.warning("Could not ensure Weaviate schema: %s", exc)

    @staticmethod
    def _properties(chunk: DocumentChunk) -> dict[str, Any]:
        return {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "title": chunk.title,
            "text": chunk.text,
            "chunk_index": chunk.chunk_index,
            "policy_type": chunk.policy_type,
            "source": chunk.source,
            "metadata_json": json.dumps(chunk.metadata),
        }


def build_vector_index() -> LocalVectorIndex | WeaviateVectorIndex:
    return WeaviateVectorIndex() if get_settings().vector_store_provider == "weaviate" else LocalVectorIndex()


vector_index = build_vector_index()
