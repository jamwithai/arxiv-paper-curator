"""Re-exports the shared domain profiles for agent nodes.

The canonical definitions live in `src.domain_profiles` so both the agent
graph and the plain `/ask` LLM prompt builder (`src.services.llm.prompts`)
can use the same domain descriptions without a circular import.
"""

from src.domain_profiles import DOMAIN_PROFILES, DomainProfile, get_domain_profile

__all__ = ["DOMAIN_PROFILES", "DomainProfile", "get_domain_profile"]
