import json
import logging

import httpx

from app.core.config import get_settings
from app.models.domain_models import Citation, RiskLevel

logger = logging.getLogger(__name__)


class LocalLLMClient:
    def generate_compliance_answer(
        self,
        query: str,
        risk_level: RiskLevel,
        citations: list[Citation],
        recommendations: list[str],
    ) -> str | None:
        return None


class OpenRouterClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.model = settings.openrouter_model
        self.site_url = settings.openrouter_site_url
        self.app_name = settings.openrouter_app_name

    def generate_compliance_answer(
        self,
        query: str,
        risk_level: RiskLevel,
        citations: list[Citation],
        recommendations: list[str],
    ) -> str | None:
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY is missing; falling back to local compliance answer")
            return None

        evidence = [
            {
                "title": citation.title,
                "source": citation.source,
                "score": citation.score,
                "excerpt": citation.excerpt,
            }
            for citation in citations[:6]
        ]
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a policy compliance analyst. Answer from the provided evidence only. "
                        "Be concise, cite evidence by document title, and state uncertainty when evidence is insufficient."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "query": query,
                            "risk_level": risk_level.value,
                            "evidence": evidence,
                            "recommended_actions": recommendations,
                        },
                        indent=2,
                    ),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 700,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name

        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            logger.warning("OpenRouter call failed; falling back to local answer: %s", exc)
            return None


def build_llm_client() -> LocalLLMClient | OpenRouterClient:
    return OpenRouterClient() if get_settings().llm_provider == "openrouter" else LocalLLMClient()
