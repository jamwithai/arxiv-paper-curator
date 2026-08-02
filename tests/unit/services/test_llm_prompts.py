from src.domain_profiles import get_domain_profile
from src.services.llm.prompts import RAGPromptBuilder


def test_default_domain_is_ai():
    builder = RAGPromptBuilder()

    assert "arXiv" in builder.system_prompt


def test_system_prompt_is_scoped_to_education_domain():
    builder = RAGPromptBuilder("education")

    assert "education" in builder.system_prompt.lower()
    assert "arXiv" not in builder.system_prompt


def test_system_prompt_is_scoped_to_accounting_domain():
    builder = RAGPromptBuilder("accounting")

    assert "accounting" in builder.system_prompt.lower()
    assert "arXiv" not in builder.system_prompt


def test_create_rag_prompt_cites_arxiv_chunks_by_arxiv_id():
    builder = RAGPromptBuilder("ai")
    chunks = [{"arxiv_id": "1706.03762", "chunk_text": "Transformers use self-attention."}]

    prompt = builder.create_rag_prompt("What is a transformer?", chunks)

    assert "[1. 1706.03762]" in prompt
    assert "Transformers use self-attention." in prompt


def test_create_rag_prompt_falls_back_to_bilingual_chunk_text_fields():
    """Bilingual domain chunks use chunk_text_vi/chunk_text_en instead of chunk_text."""
    builder = RAGPromptBuilder("education")
    chunks = [
        {"doc_number": "22/2021/TT-BGDDT", "chunk_text_vi": "Quy định đánh giá học sinh."},
    ]

    prompt = builder.create_rag_prompt("đánh giá học sinh", chunks)

    assert "[1. 22/2021/TT-BGDDT]" in prompt
    assert "Quy định đánh giá học sinh." in prompt


def test_create_rag_prompt_uses_domain_citation_style_in_answer_instructions():
    builder = RAGPromptBuilder("accounting")
    profile = get_domain_profile("accounting")

    prompt = builder.create_rag_prompt("query", [])

    assert profile.citation_style in prompt
