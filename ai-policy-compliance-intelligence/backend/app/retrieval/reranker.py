from app.models.domain_models import DocumentChunk


def lexical_overlap(query: str, text: str) -> float:
    query_terms = {term.strip(".,:;()[]{}").lower() for term in query.split() if len(term) > 2}
    text_terms = {term.strip(".,:;()[]{}").lower() for term in text.split() if len(term) > 2}
    if not query_terms:
        return 0.0
    return len(query_terms & text_terms) / len(query_terms)


def rerank(query: str, results: list[tuple[DocumentChunk, float]]) -> list[tuple[DocumentChunk, float]]:
    rescored = [(chunk, (score * 0.65) + (lexical_overlap(query, chunk.text) * 0.35)) for chunk, score in results]
    return sorted(rescored, key=lambda item: item[1], reverse=True)
