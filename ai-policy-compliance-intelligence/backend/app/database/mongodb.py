import json
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.exceptions import ValidationAppError
from app.models.domain_models import DocumentChunk, PolicyDocument


class LocalDocumentStore:
    def __init__(self) -> None:
        self.path = get_settings().processed_dir / "document_store.json"

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"documents": [], "chunks": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")

    def save_document(self, document: PolicyDocument, chunks: list[DocumentChunk]) -> None:
        data = self._read()
        data["documents"] = [doc for doc in data["documents"] if doc["id"] != document.id]
        data["chunks"] = [chunk for chunk in data["chunks"] if chunk["document_id"] != document.id]
        data["documents"].append(document.model_dump(mode="json"))
        data["chunks"].extend(chunk.model_dump(mode="json") for chunk in chunks)
        self._write(data)

    def list_documents(self) -> list[PolicyDocument]:
        return [PolicyDocument.model_validate(item) for item in self._read()["documents"]]

    def list_chunks(self) -> list[DocumentChunk]:
        return [DocumentChunk.model_validate(item) for item in self._read()["chunks"]]

    def stats(self) -> dict[str, Any]:
        data = self._read()
        policy_types: dict[str, int] = {}
        for doc in data["documents"]:
            policy_types[doc.get("policy_type", "general")] = policy_types.get(doc.get("policy_type", "general"), 0) + 1
        return {"documents": len(data["documents"]), "chunks": len(data["chunks"]), "policy_types": policy_types}


class MongoDocumentStore:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.mongodb_uri:
            raise ValidationAppError("Set MONGODB_URI when DOCUMENT_STORE_PROVIDER=mongodb")
        self.uri = settings.mongodb_uri
        self.database_name = settings.mongodb_database
        self.client = None
        self.db = None
        self.documents = None
        self.chunks = None
        self._indexes_ready = False

    def _connect(self) -> None:
        if self.client is not None:
            return
        try:
            from pymongo import MongoClient
        except ModuleNotFoundError as exc:
            raise ValidationAppError("Install pymongo or motor to use MongoDB storage") from exc

        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[self.database_name]
        self.documents = self.db["documents"]
        self.chunks = self.db["chunks"]

    def _ensure_indexes(self) -> None:
        self._connect()
        if self._indexes_ready:
            return
        self.documents.create_index("id", unique=True)
        self.chunks.create_index("id", unique=True)
        self.chunks.create_index("document_id")
        self.chunks.create_index("policy_type")
        self._indexes_ready = True

    def save_document(self, document: PolicyDocument, chunks: list[DocumentChunk]) -> None:
        self._ensure_indexes()
        self.documents.replace_one({"id": document.id}, document.model_dump(mode="json"), upsert=True)
        self.chunks.delete_many({"document_id": document.id})
        if chunks:
            self.chunks.insert_many([chunk.model_dump(mode="json") for chunk in chunks])

    def list_documents(self) -> list[PolicyDocument]:
        self._connect()
        return [PolicyDocument.model_validate(self._strip_mongo_id(item)) for item in self.documents.find({})]

    def list_chunks(self) -> list[DocumentChunk]:
        self._connect()
        return [DocumentChunk.model_validate(self._strip_mongo_id(item)) for item in self.chunks.find({})]

    def stats(self) -> dict[str, Any]:
        self._connect()
        policy_types: dict[str, int] = {}
        for item in self.documents.aggregate([{"$group": {"_id": "$policy_type", "count": {"$sum": 1}}}]):
            policy_types[item["_id"] or "general"] = item["count"]
        return {"documents": self.documents.count_documents({}), "chunks": self.chunks.count_documents({}), "policy_types": policy_types}

    @staticmethod
    def _strip_mongo_id(item: dict[str, Any]) -> dict[str, Any]:
        item.pop("_id", None)
        return item


def build_document_store() -> LocalDocumentStore | MongoDocumentStore:
    settings = get_settings()
    return MongoDocumentStore() if settings.document_store_provider == "mongodb" else LocalDocumentStore()


store = build_document_store()
