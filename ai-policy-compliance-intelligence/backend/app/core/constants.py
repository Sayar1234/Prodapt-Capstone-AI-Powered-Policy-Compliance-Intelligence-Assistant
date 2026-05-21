SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

RISK_KEYWORDS = {
    "privacy": ["personal data", "pii", "consent", "gdpr", "ccpa", "privacy", "regulated data", "data processing"],
    "security": ["encrypt", "encryption", "mfa", "multi factor", "incident", "breach", "vulnerability", "access control"],
    "finance": ["audit", "sox", "financial reporting", "segregation of duties", "material weakness"],
    "hr": ["harassment", "discrimination", "equal opportunity", "workplace", "employee relations"],
    "operations": ["vendor", "third party", "third-party", "retention", "business continuity", "outsourcing"],
}

HIGH_RISK_TERMS = [
    "without approval",
    "without encryption",
    "without consent",
    "bypass",
    "breach",
    "regulated data",
    "personal data",
    "pii",
    "production",
    "privileged access",
    "incident",
    "legal",
    "notification",
]

MEDIUM_RISK_TERMS = [
    "vendor",
    "third party",
    "third-party",
    "customer",
    "audit",
    "review",
    "retention",
    "approval",
    "monitoring",
]

DEFAULT_POLICY_TYPES = ["security", "privacy", "finance", "hr", "operations", "general"]
