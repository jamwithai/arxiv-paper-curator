ARXIV_PAPERS_INDEX = "arxiv-papers"

# Index mapping configuration for arXiv papers
ARXIV_PAPERS_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
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
            "arxiv_id": {"type": "keyword"},
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
            "raw_text": {"type": "text", "analyzer": "text_analyzer"},
            "pdf_url": {"type": "keyword"},
            "published_date": {"type": "date"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        },
    },
}
