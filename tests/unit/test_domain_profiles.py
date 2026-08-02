from src.domain_profiles import DOMAIN_PROFILES, get_domain_profile


def test_get_domain_profile_returns_configured_domains():
    for key in ("ai", "education", "accounting"):
        profile = get_domain_profile(key)
        assert profile.key == key
        assert profile.label
        assert profile.citation_style
        assert profile.out_of_scope_suggestion


def test_get_domain_profile_falls_back_to_ai_for_unknown_domain():
    profile = get_domain_profile("nonexistent_domain")

    assert profile == DOMAIN_PROFILES["ai"]


def test_ai_domain_cites_by_arxiv_id():
    profile = get_domain_profile("ai")

    assert "arXiv" in profile.citation_style


def test_bilingual_domains_cite_by_document_number():
    for key in ("education", "accounting"):
        profile = get_domain_profile(key)
        assert "document number" in profile.citation_style
