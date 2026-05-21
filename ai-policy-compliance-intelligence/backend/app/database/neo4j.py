from collections import defaultdict

from app.core.config import get_settings
from app.core.exceptions import ValidationAppError
from app.models.domain_models import DocumentChunk


class LocalKnowledgeGraph:
    def upsert_document_chunks(self, chunks: list[DocumentChunk]) -> None:
        return None

    def related_policy_types(self, chunks: list[DocumentChunk]) -> dict[str, list[str]]:
        graph: dict[str, set[str]] = defaultdict(set)
        for chunk in chunks:
            graph[chunk.policy_type].add(chunk.title)
        return {key: sorted(value) for key, value in graph.items()}


class Neo4jKnowledgeGraph:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.neo4j_uri or not settings.neo4j_user or not settings.neo4j_password:
            raise ValidationAppError("Set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD when GRAPH_PROVIDER=neo4j")
        try:
            from neo4j import GraphDatabase
        except ModuleNotFoundError as exc:
            raise ValidationAppError("Install neo4j to use Neo4j graph storage") from exc
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))

    def upsert_document_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return
        with self.driver.session() as session:
            for chunk in chunks:
                session.execute_write(self._merge_chunk, chunk.model_dump(mode="json"))

    def related_policy_types(self, chunks: list[DocumentChunk]) -> dict[str, list[str]]:
        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (type:PolicyType)<-[:HAS_TYPE]-(doc:PolicyDocument)
                RETURN type.name AS policy_type, collect(DISTINCT doc.title) AS titles
                """
            )
            return {row["policy_type"]: sorted(row["titles"]) for row in rows}

    @staticmethod
    def _merge_chunk(tx, chunk: dict) -> None:
        tx.run(
            """
            MERGE (doc:PolicyDocument {id: $document_id})
            SET doc.title = $title, doc.source = $source
            MERGE (type:PolicyType {name: $policy_type})
            MERGE (doc)-[:HAS_TYPE]->(type)
            MERGE (chunk:PolicyChunk {id: $id})
            SET chunk.text = $text, chunk.chunk_index = $chunk_index, chunk.source = $source
            MERGE (doc)-[:HAS_CHUNK]->(chunk)
            """,
            **chunk,
        )


def build_knowledge_graph() -> LocalKnowledgeGraph | Neo4jKnowledgeGraph:
    return Neo4jKnowledgeGraph() if get_settings().graph_provider == "neo4j" else LocalKnowledgeGraph()


knowledge_graph = build_knowledge_graph()
