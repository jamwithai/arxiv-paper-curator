from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class DomainProfile:
    """Describes a corpus domain for prompt templating.

    Used by guardrail/generate_answer/out_of_scope nodes so the agent stops
    assuming every corpus is arXiv papers (see Stage 2 plan).
    """

    key: str
    label: str  # Human-readable description of the corpus, used in LLM prompts
    citation_style: str  # How sources should be cited in answers
    out_of_scope_suggestion: str  # What to suggest when a query is out of scope


DOMAIN_PROFILES: Dict[str, DomainProfile] = {
    "ai": DomainProfile(
        key="ai",
        label="academic research papers from arXiv (Computer Science, AI, and Machine Learning)",
        citation_style="the arXiv ID, e.g. [arXiv:1706.03762]",
        out_of_scope_suggestion="a general-purpose AI assistant or a domain-specific resource",
    ),
    "education": DomainProfile(
        key="education",
        label=(
            "Vietnamese and English regulatory documents and reference materials on education "
            "management (circulars, decisions from the Ministry of Education and Training, and "
            "academic literature on educational administration)"
        ),
        citation_style="the document number, e.g. [22/2021/TT-BGDDT]",
        out_of_scope_suggestion="official education ministry resources or a general-purpose assistant",
    ),
    "accounting": DomainProfile(
        key="accounting",
        label=(
            "Vietnamese and English accounting regulations and standards (Vietnamese Accounting "
            "Standards circulars/decisions, and international standards such as IFRS)"
        ),
        citation_style="the document number or standard code, e.g. [IFRS-16] or [200/2014/TT-BTC]",
        out_of_scope_suggestion="an accounting professional, official standards body, or a general-purpose assistant",
    ),
}


def get_domain_profile(domain: str) -> DomainProfile:
    """Resolve a domain key to its profile, defaulting to "ai" for unknown domains."""
    return DOMAIN_PROFILES.get(domain, DOMAIN_PROFILES["ai"])
