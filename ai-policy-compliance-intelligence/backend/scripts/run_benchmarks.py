import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.evaluation.benchmarks import BENCHMARK_CASES
from app.evaluation.evaluators import evaluate_response, passes_quality_gate
from app.services.ingestion_service import IngestionService
from app.models.request_models import ComplianceCheckRequest
from app.services.compliance_service import ComplianceService


async def main() -> None:
    ingestion = IngestionService()
    service = ComplianceService()
    failures = 0
    for case in BENCHMARK_CASES:
        ingestion.ingest_text_document(
            title=case.seed_title,
            text=case.seed_text,
            source=f"benchmark:{case.name}",
            policy_type=case.policy_type,
        )
        response = await service.check(ComplianceCheckRequest(query=case.query, policy_type=case.policy_type))
        scores = evaluate_response(response, case.expected_terms)
        passed = passes_quality_gate(scores)
        failures += 0 if passed else 1
        print({"case": case.name, "passed": passed, "scores": scores})
    if failures:
        raise SystemExit(f"{failures} benchmark case(s) failed")


if __name__ == "__main__":
    asyncio.run(main())
