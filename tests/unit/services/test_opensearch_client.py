import pytest
from src.config import Settings
from src.services.opensearch.client import OpenSearchClient
from src.services.opensearch.index_config_hybrid import LEGAL_DOCS_SEARCH_FIELDS


@pytest.fixture
def client():
    return OpenSearchClient(host="http://localhost:9200", settings=Settings())


def test_resolve_index_uses_default_domain_when_none_given(client):
    assert client.resolve_index(None) == client.domain_indices["ai"]


def test_resolve_index_returns_configured_index_per_domain(client):
    assert client.resolve_index("ai") == "arxiv-papers-chunks"
    assert client.resolve_index("education") == "corpus-education-chunks"
    assert client.resolve_index("accounting") == "corpus-accounting-chunks"


def test_resolve_index_raises_for_unknown_domain(client):
    with pytest.raises(ValueError, match="Unknown domain"):
        client.resolve_index("not_a_real_domain")


def test_search_fields_for_bilingual_domains_uses_legal_docs_fields(client):
    assert client._search_fields_for("education") == LEGAL_DOCS_SEARCH_FIELDS
    assert client._search_fields_for("accounting") == LEGAL_DOCS_SEARCH_FIELDS


def test_search_fields_for_ai_domain_uses_query_builder_default(client):
    # None means "let QueryBuilder use its own default arXiv fields"
    assert client._search_fields_for("ai") is None
    assert client._search_fields_for(None) is None


def test_index_name_defaults_to_ai_domain_for_backward_compatibility(client):
    assert client.index_name == client.domain_indices["ai"]
