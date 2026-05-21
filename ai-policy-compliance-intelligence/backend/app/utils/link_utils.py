import re


URL_PATTERN = re.compile(r"https?://[^\s<>)\]}\"']+", re.IGNORECASE)


def extract_links(text: str, limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    links: list[str] = []
    for match in URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,;:")
        if url in seen:
            continue
        seen.add(url)
        links.append(url)
        if limit and len(links) >= limit:
            break
    return links
