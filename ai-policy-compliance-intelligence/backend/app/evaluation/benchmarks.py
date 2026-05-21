from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    query: str
    policy_type: str
    seed_title: str
    seed_text: str
    expected_terms: list[str]


BENCHMARK_CASES = [
    BenchmarkCase(
        name="third_party_personal_data",
        query="Can employees share customer personal data with third-party vendors?",
        policy_type="privacy",
        seed_title="Privacy and Vendor Policy",
        seed_text=(
            "Customer personal data may be shared with approved third-party vendors only after a data "
            "processing agreement, business purpose review, encryption in transit, and privacy approval."
        ),
        expected_terms=["personal data", "third-party", "approval", "encryption"],
    ),
    BenchmarkCase(
        name="production_change",
        query="What controls are required before deploying a high-risk production change?",
        policy_type="security",
        seed_title="Change Management Policy",
        seed_text=(
            "High-risk production changes require documented approval, rollback planning, security review, "
            "testing evidence, and post-deployment monitoring."
        ),
        expected_terms=["approval", "rollback", "security review", "testing"],
    ),
    BenchmarkCase(
        name="regulated_incident",
        query="How should an incident involving regulated data be escalated?",
        policy_type="security",
        seed_title="Incident Response Policy",
        seed_text=(
            "Incidents involving regulated data must be reported to security and compliance within 24 hours, "
            "triaged by severity, preserved for audit, and escalated to legal when notification may be required."
        ),
        expected_terms=["24 hours", "compliance", "audit", "legal"],
    ),
]

BENCHMARK_QUERIES = [case.query for case in BENCHMARK_CASES]
