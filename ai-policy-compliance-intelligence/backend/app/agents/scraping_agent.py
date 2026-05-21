import logging
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ReadableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.parts: list[str] = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"p", "br", "li", "section", "article", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title = f"{self.title} {text}".strip()
        self.parts.append(text)

    def readable_text(self) -> str:
        text = " ".join(self.parts)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


class ScrapingAgent:
    def scrape(self, url: str) -> dict[str, str]:
        settings = get_settings()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return {"url": url, "title": "", "text": "", "status": "unsupported_scheme"}

        try:
            with httpx.Client(
                timeout=settings.scrape_timeout_seconds,
                follow_redirects=True,
                headers={"User-Agent": f"{settings.openrouter_app_name}/1.0 policy-compliance-bot"},
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "text/plain" not in content_type:
                    return {"url": url, "title": "", "text": "", "status": f"skipped_content_type:{content_type}"}

            if "text/plain" in content_type:
                text = " ".join(response.text.split())
                return {"url": str(response.url), "title": parsed.netloc, "text": text[: settings.max_scraped_chars_per_link], "status": "ok"}

            parser = ReadableHTMLParser()
            parser.feed(response.text)
            text = parser.readable_text()[: settings.max_scraped_chars_per_link]
            return {"url": str(response.url), "title": parser.title or parsed.netloc, "text": text, "status": "ok" if text else "empty"}
        except Exception as exc:
            logger.info("Link scraping failed for %s: %s", url, exc)
            return {"url": url, "title": "", "text": "", "status": "failed"}

    def scrape_many(self, urls: list[str]) -> list[dict[str, str]]:
        settings = get_settings()
        return [self.scrape(url) for url in urls[: settings.max_scraped_links]]
