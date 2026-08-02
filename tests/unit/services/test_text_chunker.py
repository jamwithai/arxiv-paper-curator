import pytest

from src.services.indexing.text_chunker import TextChunker


@pytest.fixture
def chunker():
    return TextChunker(chunk_size=600, overlap_size=100, min_chunk_size=100)


def test_chunk_text_below_min_size_returns_single_chunk(chunker):
    """Regression test: _reconstruct_text() takes only `words`, not `(words, text)` -
    calling it with the extra `text` arg raised TypeError for any paper whose fallback
    full_text chunking path hit the < min_chunk_size branch, silently dropping the
    paper from the index (caught by a bare except in HybridIndexingService.index_paper)."""
    short_text = "This is a short paper abstract with only a handful of words in it."

    chunks = chunker.chunk_text(short_text, arxiv_id="1234.5678", paper_id="paper-1")

    assert len(chunks) == 1
    assert chunks[0].text == short_text
    assert chunks[0].metadata.word_count == len(short_text.split())


def test_chunk_text_empty_returns_no_chunks(chunker):
    assert chunker.chunk_text("", arxiv_id="1234.5678", paper_id="paper-1") == []


def test_chunk_text_above_chunk_size_splits_with_overlap(chunker):
    text = " ".join(f"word{i}" for i in range(1500))

    chunks = chunker.chunk_text(text, arxiv_id="1234.5678", paper_id="paper-1")

    assert len(chunks) > 1
    assert chunks[0].metadata.word_count == 600
    assert chunks[0].metadata.overlap_with_next == 100
