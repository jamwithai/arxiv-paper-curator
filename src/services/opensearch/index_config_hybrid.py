"""OpenSearch index configuration for hybrid search (BM25 + Vector).

This configuration supports both keyword search (BM25) and vector similarity search
using HNSW algorithm for approximate nearest neighbor search.
"""

ARXIV_PAPERS_CHUNKS_INDEX = "arxiv-papers-chunks"

# Index mapping for chunked papers with vector embeddings
ARXIV_PAPERS_CHUNKS_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "index.knn": True,
        "index.knn.space_type": "cosinesimil",
        "analysis": {
            "analyzer": {
                "standard_analyzer": {"type": "standard", "stopwords": "_english_"},
                "text_analyzer": {"type": "custom", "tokenizer": "standard", "filter": ["lowercase", "stop", "snowball"]},
            }
        },
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "chunk_id": {"type": "keyword"},
            "arxiv_id": {"type": "keyword"},
            "paper_id": {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            "chunk_text": {
                "type": "text",
                "analyzer": "text_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "chunk_word_count": {"type": "integer"},
            "start_char": {"type": "integer"},
            "end_char": {"type": "integer"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 1024,  # Jina v3 embeddings dimension
                "method": {
                    "name": "hnsw",  # Hierarchical Navigable Small World
                    "space_type": "cosinesimil",  # Cosine similarity
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 512,  # Higher value = better recall, slower indexing
                        "m": 16,  # Number of bi-directional links
                    },
                },
            },
            "title": {
                "type": "text",
                "analyzer": "text_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "authors": {
                "type": "text",
                "analyzer": "standard_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "abstract": {"type": "text", "analyzer": "text_analyzer"},
            "categories": {"type": "keyword"},
            "published_date": {"type": "date"},
            "section_title": {"type": "keyword"},
            "embedding_model": {"type": "keyword"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        },
    },
}

LEGAL_DOCS_CHUNKS_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "index.knn": True,
        "index.knn.space_type": "cosinesimil",
        "analysis": {
            "analyzer": {
                # Vietnamese has no dedicated OpenSearch stemmer; ICU tokenizer +
                # folding (accent/diacritic-insensitive) is the pragmatic baseline.
                # See Stage 2 plan (2b): revisit with word segmentation (pyvi/
                # underthesea) at ingest time if Recall@k/MRR falls short.
                "vi_analyzer": {
                    "type": "custom",
                    "tokenizer": "icu_tokenizer",
                    "filter": ["icu_folding", "lowercase"],
                },
                "en_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop", "snowball"],
                },
            }
        },
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "chunk_id": {"type": "keyword"},
            "doc_id": {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            # Bilingual chunks are indexed into both fields at ingest time based on
            # detected language (see Stage 2 plan 2b) so BM25 matches the right
            # analyzer instead of forcing one language's tokenizer on the other.
            "chunk_text_vi": {"type": "text", "analyzer": "vi_analyzer"},
            "chunk_text_en": {"type": "text", "analyzer": "en_analyzer"},
            "language": {"type": "keyword"},  # "vi" | "en" - which field is authoritative
            "chunk_word_count": {"type": "integer"},
            "start_char": {"type": "integer"},
            "end_char": {"type": "integer"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 1024,  # Jina v3 embeddings dimension (multilingual)
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 512,
                        "m": 16,
                    },
                },
            },
            "title": {
                "type": "text",
                "analyzer": "vi_analyzer",
                "fields": {
                    "en": {"type": "text", "analyzer": "en_analyzer"},
                    "keyword": {"type": "keyword", "ignore_above": 256},
                },
            },
            # Legal/regulatory document metadata - required per Stage 2 plan (2c):
            # citing a superseded regulation is a serious error in the accounting
            # and education theses this corpus supports.
            "doc_number": {"type": "keyword"},  # số hiệu văn bản
            "issuing_body": {"type": "keyword"},  # cơ quan ban hành
            "issued_date": {"type": "date"},  # ngày ban hành
            "effective_status": {"type": "keyword"},  # "active" | "superseded" | "expired"
            "source_language": {"type": "keyword"},  # "vi" | "en" - original document language
            "embedding_model": {"type": "keyword"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        },
    },
}

# Multi-match fields for bilingual BM25 queries against LEGAL_DOCS_CHUNKS_MAPPING.
# Both language fields are queried; OpenSearch's `operator: or` means a Vietnamese
# query still matches even though chunk_text_en is present but empty for that chunk.
LEGAL_DOCS_SEARCH_FIELDS = ["chunk_text_vi^3", "chunk_text_en^3", "title^2", "title.en^2"]

HYBRID_RRF_PIPELINE = {
    "id": "hybrid-rrf-pipeline",
    "description": "Post processor for hybrid RRF search",
    "phase_results_processors": [
        {
            "score-ranker-processor": {
                "combination": {
                    "technique": "rrf",  # Reciprocal Rank Fusion
                    "rank_constant": 60,  # Default k=60 for RRF formula: 1/(k+rank)
                }
            }
        }
    ],
}

# Alternative: Weighted average pipeline (commented out - not used by default)
# This could be used if you need explicit control over BM25 vs vector weights
# However, RRF generally provides better results without manual weight tuning
"""
HYBRID_SEARCH_PIPELINE = {
    "id": "hybrid-ranking-pipeline",
    "description": "Hybrid search pipeline using weighted average for BM25 and vector similarity",
    "phase_results_processors": [
        {
            "normalization-processor": {
                "normalization": {
                    "technique": "l2"  # L2 normalization for better score distribution
                },
                "combination": {
                    "technique": "harmonic_mean",  # Harmonic mean often works better than arithmetic
                    "parameters": {
                        "weights": [0.3, 0.7]  # 30% BM25, 70% vector similarity
                    }
                }
            }
        }
    ]
}
"""
