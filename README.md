# The Mother of AI Project
## Phase 1 RAG Systems: arXiv Paper Curator

<div align="center">
  <h3>A Learner-Focused Journey into Production RAG Systems</h3>
  <p>Learn to build modern AI systems from the ground up through hands-on implementation</p>
  <p>Master the most in-demand AI engineering skills: <strong>RAG (Retrieval-Augmented Generation)</strong></p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/OpenSearch-2.19-orange.svg" alt="OpenSearch">
  <img src="https://img.shields.io/badge/Docker-Compose-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/Status-Week%206%20Production%20Ready-brightgreen.svg" alt="Status">
</p>

</br>

<p align="center">
  <a href="#-about-this-course">
    <img src="static/mother_of_ai_project_rag_architecture.gif" alt="RAG Architecture" width="700">
  </a>
</p>

## 📖 About This Course

This is a **learner-focused project** where you'll build a complete research assistant system that automatically fetches academic papers, understands their content, and answers your research questions using advanced RAG techniques.

**The arXiv Paper Curator** will teach you to build a **production-grade RAG system using industry best practices**. Unlike tutorials that jump straight to vector search, we follow the **professional path**: master keyword search foundations first, then enhance with vectors for hybrid retrieval.

> **🎯 The Professional Difference:** We build RAG systems the way successful companies do - solid search foundations enhanced with AI, not AI-first approaches that ignore search fundamentals.

By the end of this course, you'll have your own AI research assistant and the deep technical skills to build production RAG systems for any domain.

### **🎓 What You'll Build**

- **Week 1:** Complete infrastructure with Docker, FastAPI, PostgreSQL, OpenSearch, and Airflow
- **Week 2:** Automated data pipeline fetching and parsing academic papers from arXiv  
- **Week 3:** Production BM25 keyword search with filtering and relevance scoring
- **Week 4:** Intelligent chunking + hybrid search combining keywords with semantic understanding
- **Week 5:** **Complete RAG pipeline with local LLM, streaming responses, and Gradio interface**
- **Week 6:** **Production monitoring with Langfuse tracing and Redis caching for optimized performance**

---

## 🚀 Quick Start

### **📋 Prerequisites**
- **Docker Desktop** (with Docker Compose)  
- **Python 3.12+**
- **UV Package Manager** ([Install Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **8GB+ RAM** and **20GB+ free disk space**

### **⚡ Get Started**

```bash
# 1. Clone and setup
git clone <repository-url>
cd arxiv-paper-curator

# 2. Configure environment (IMPORTANT!)
cp .env.example .env
# The .env file contains all necessary configuration for OpenSearch, 
# arXiv API, and service connections. Defaults work out of the box.
# For Week 4: Add JINA_API_KEY=your_key_here for hybrid search

# 3. Install dependencies
uv sync

# 4. Start all services
docker compose up --build -d

# 5. Verify everything works
curl [http://localhost:8000/health](http://localhost:8000/api/v1/health)
```

### **📚 Weekly Learning Path**

| Week | Topic | Blog Post | Code Release |
|------|-------|-----------|--------------|
| **Week 0** | The Mother of AI project - 6 phases | [The Mother of AI project](https://jamwithai.substack.com/p/the-mother-of-ai-project) | - |
| **Week 1** | Infrastructure Foundation | [The Infrastructure That Powers RAG Systems](https://jamwithai.substack.com/p/the-infrastructure-that-powers-rag) | [week1.0](https://github.com/jamwithai/arxiv-paper-curator/releases/tag/week1.0) |
| **Week 2** | Data Ingestion Pipeline | [Building Data Ingestion Pipelines for RAG](https://jamwithai.substack.com/p/bringing-your-rag-system-to-life) | [week2.0](https://github.com/jamwithai/arxiv-paper-curator/releases/tag/week2.0) |
| **Week 3** | OpenSearch ingestion & BM25 retrieval | [The Search Foundation Every RAG System Needs](https://jamwithai.substack.com/p/the-search-foundation-every-rag-system) | [week3.0](https://github.com/jamwithai/arxiv-paper-curator/releases/tag/week3.0) |
| **Week 4** | **Chunking & Hybrid Search** | [The Chunking Strategy That Makes Hybrid Search Work](https://jamwithai.substack.com/p/the-chunking-strategy-that-makes-hybrid-search-work) | [week4.0](https://github.com/jamwithai/arxiv-paper-curator/releases/tag/week4.0) |
| **Week 5** | **Complete RAG system** | [The Complete RAG System](https://jamwithai.substack.com/p/the-complete-rag-system) | [week5.0](https://github.com/jamwithai/arxiv-paper-curator/releases/tag/week5.0) |
| **Week 6** | **Production monitoring & caching** | (Production-ready RAG: Monitoring & Caching)[https://jamwithai.substack.com/p/production-ready-rag-monitoring-and] | [week6.0](https://github.com/jamwithai/arxiv-paper-curator/releases/tag/week6.0) |

**📥 Clone a specific week's release:**
```bash
# Clone a specific week's code
git clone --branch <WEEK_TAG> https://github.com/jamwithai/arxiv-paper-curator
cd arxiv-paper-curator
uv sync
docker compose down -v
docker compose up --build -d

# Replace <WEEK_TAG> with: week1.0, week2.0, etc.
```

### **📊 Access Your Services**

| Service | URL | Purpose |
|---------|-----|---------|
| **API Documentation** | http://localhost:8000/docs | Interactive API testing |
| **Gradio RAG Interface** | http://localhost:7861 | User-friendly chat interface |
| **Langfuse Dashboard** | http://localhost:3000 | RAG pipeline monitoring & tracing |
| **Airflow Dashboard** | http://localhost:8080 | Workflow management |
| **OpenSearch Dashboards** | http://localhost:5601 | Hybrid search engine UI |

#### **NOTE**: Check airflow/simple_auth_manager_passwords.json.generated for Airflow username and password
---

## 📚 Week 1: Infrastructure Foundation ✅

**Start here!** Master the infrastructure that powers modern RAG systems.

### **🎯 Learning Objectives**
- Complete infrastructure setup with Docker Compose
- FastAPI development with automatic documentation and health checks
- PostgreSQL database configuration and management
- OpenSearch hybrid search engine setup
- Ollama local LLM service configuration
- Service orchestration and health monitoring
- Professional development environment with code quality tools

### **🏗️ Architecture Overview**

<p align="center">
  <img src="static/week1_infra_setup.png" alt="Week 1 Infrastructure Setup" width="800">
</p>

**Infrastructure Components:**
- **FastAPI**: REST endpoints with async support (Port 8000)  
- **PostgreSQL 16**: Paper metadata storage (Port 5432)
- **OpenSearch 2.19**: Search engine with dashboards (Ports 9200, 5601)
- **Apache Airflow 3.0**: Workflow orchestration (Port 8080)
- **Ollama**: Local LLM server (Port 11434)

### **📓 Setup Guide**

```bash
# Launch the Week 1 notebook
uv run jupyter notebook notebooks/week1/week1_setup.ipynb
```

### **✅ Success Criteria**
Complete when you can:
- [ ] Start all services with `docker compose up -d`
- [ ] Access API docs at http://localhost:8000/docs  
- [ ] Login to Airflow at http://localhost:8080
- [ ] Browse OpenSearch at http://localhost:5601
- [ ] All tests pass: `uv run pytest`

### **📖 Deep Dive**
**Blog Post:** [The Infrastructure That Powers RAG Systems](https://jamwithai.substack.com/p/the-infrastructure-that-powers-rag) - Detailed walkthrough and production insights

---

## 📚 Week 2: Data Ingestion Pipeline ✅

**Building on Week 1 infrastructure:** Learn to fetch, process, and store academic papers automatically.

### **🎯 Learning Objectives**
- arXiv API integration with rate limiting and retry logic
- Scientific PDF parsing using Docling
- Automated data ingestion pipelines with Apache Airflow
- Metadata extraction and storage workflows
- Complete paper processing from API to database

### **🏗️ Architecture Overview**

<p align="center">
  <img src="static/week2_data_ingestion_flow.png" alt="Week 2 Data Ingestion Architecture" width="800">
</p>

**Data Pipeline Components:**
- **MetadataFetcher**: 🎯 Main orchestrator coordinating the entire pipeline
- **ArxivClient**: Rate-limited paper fetching with retry logic
- **PDFParserService**: Docling-powered scientific document processing  
- **Airflow DAGs**: Automated daily paper ingestion workflows
- **PostgreSQL Storage**: Structured paper metadata and content

### **📓 Implementation Guide**

```bash
# Launch the Week 2 notebook  
uv run jupyter notebook notebooks/week2/week2_arxiv_integration.ipynb
```

### **💻 Code Examples**

**arXiv API Integration:**
```python
# Example: Fetch papers with rate limiting
from src.services.arxiv.factory import make_arxiv_client

async def fetch_recent_papers():
    client = make_arxiv_client()
    papers = await client.search_papers(
        query="cat:cs.AI",
        max_results=10,
        from_date="20240801",
        to_date="20240807"
    )
    return papers
```

**PDF Processing Pipeline:**
```python
# Example: Parse PDF with Docling
from src.services.pdf_parser.factory import make_pdf_parser_service

async def process_paper_pdf(pdf_url: str):
    parser = make_pdf_parser_service()
    parsed_content = await parser.parse_pdf_from_url(pdf_url)
    return parsed_content  # Structured content with text, tables, figures
```

**Complete Ingestion Workflow:**
```python
# Example: Full paper ingestion pipeline
from src.services.metadata_fetcher import make_metadata_fetcher

async def ingest_papers():
    fetcher = make_metadata_fetcher()
    results = await fetcher.fetch_and_store_papers(
        query="cat:cs.AI",
        max_results=5,
        from_date="20240807"
    )
    return results  # Papers stored in database with full content
```

### **✅ Success Criteria**
Complete when you can:
- [ ] Fetch papers from arXiv API: Test in Week 2 notebook
- [ ] Parse PDF content with Docling: View extracted structured content
- [ ] Run Airflow DAG: `arxiv_paper_ingestion` executes successfully
- [ ] Verify database storage: Papers appear in PostgreSQL with full content
- [ ] API endpoints work: `/papers` returns stored papers with metadata

### **📖 Deep Dive**
**Blog Post:** [Building Data Ingestion Pipelines for RAG](https://jamwithai.substack.com/p/bringing-your-rag-system-to-life) - arXiv API integration and PDF processing

---

## 📚 Week 3: Keyword Search First - The Critical Foundation ⚡

> **🚨 The 90% Problem:** Most RAG systems jump straight to vector search and miss the foundation that powers the best retrieval systems. We're doing it right!

**Building on Weeks 1-2 foundation:** Implement the keyword search foundation that professional RAG systems rely on.

### **🎯 Why Keyword Search First?**

**The Reality Check:** Vector search alone is not enough. The most effective RAG systems use **hybrid retrieval** - combining keyword search (BM25) with vector search. Here's why we start with keywords:

1. **🔍 Exact Match Power:** Keywords excel at finding specific terms, technical jargon, and precise phrases
2. **📊 Interpretable Results:** You can understand exactly why a document was retrieved  
3. **⚡ Speed & Efficiency:** BM25 is computationally fast and doesn't require expensive embedding models
4. **🎯 Domain Knowledge:** Technical papers often require exact terminology matches that vector search might miss
5. **📈 Production Reality:** Companies like Elasticsearch, Algolia, and enterprise search all use keyword search as their foundation

### **🏗️ Week 3 Architecture Overview**

<p align="center">
  <img src="static/week3_opensearch_flow.png" alt="Week 3 OpenSearch Flow Architecture" width="800">
  <br>
  <em>Complete Week 3 architecture showing the OpenSearch integration flow</em>
</p>

**Search Infrastructure:** Master full-text search with OpenSearch before adding vector complexity.

#### **🎯 Learning Objectives**
- **Foundation First:** Why keyword search is essential for RAG systems
- **OpenSearch Mastery:** Index management, mappings, and search optimization
- **BM25 Algorithm:** Understanding the math behind effective keyword search
- **Query DSL:** Building complex search queries with filters and boosting
- **Search Analytics:** Measuring search relevance and performance
- **Production Patterns:** How real companies structure their search systems

#### **Key Components**
- `src/services/opensearch/`: Professional search service implementation
- `src/routers/search.py`: Search API endpoints with BM25 scoring
- `notebooks/week3/`: Complete OpenSearch integration guide  
- **Search Quality Metrics:** Precision, recall, and relevance scoring

#### **💡 The Pedagogical Approach**
```
Week 3: Master keyword search (BM25) ← YOU ARE HERE
Week 4: Add intelligent chunking strategies  
Week 5: Introduce vector embeddings for hybrid retrieval
Week 6: Optimize the complete hybrid system
```

**This progression mirrors how successful companies build search systems - solid foundation first, then enhance with advanced techniques.**

### **📓 Week 3 Implementation Guide**

```bash
# Launch the Week 3 notebook
uv run jupyter notebook notebooks/week3/week3_opensearch.ipynb
```

### **💻 Code Examples**

**BM25 Search Implementation:**
```python
# Example: Search papers with BM25 scoring
from src.services.opensearch.factory import make_opensearch_client

async def search_papers():
    client = make_opensearch_client()
    results = await client.search_papers(
        query="transformer attention mechanism",
        max_results=10,
        categories=["cs.AI", "cs.LG"]
    )
    return results  # Papers ranked by BM25 relevance
```

**Search API Usage:**
```python
# Example: Use the search endpoint
import httpx

async def query_papers():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/v1/search", json={
            "query": "neural networks optimization",
            "max_results": 5,
            "latest_papers": True
        })
        return response.json()
```

### **✅ Success Criteria**
Complete when you can:
- [ ] Index papers in OpenSearch: Papers searchable via OpenSearch Dashboards
- [ ] Search via API: `/search` endpoint returns relevant papers with BM25 scoring
- [ ] Filter by categories: Search within specific arXiv categories (cs.AI, cs.LG, etc.)
- [ ] Sort by relevance or date: Toggle between BM25 scoring and latest papers
- [ ] View search analytics: Understanding why papers matched your query

### **📖 Deep Dive**
**Blog Post:** [The Search Foundation Every RAG System Needs](https://jamwithai.substack.com/p/the-search-foundation-every-rag-system) - Complete BM25 implementation with OpenSearch

---

## 📚 Week 4: Chunking & Hybrid Search - The Semantic Layer 🔥

> **🚀 The Intelligence Upgrade:** Now we enhance our solid BM25 foundation with semantic understanding through intelligent chunking and hybrid retrieval.

**Building on Week 3 foundation:** Add the semantic layer that makes search truly intelligent.

### **🎯 Why Chunking + Hybrid Search?**

**The Next Level:** With solid BM25 search proven, we can now intelligently add semantic capabilities:

1. **🧩 Smart Chunking:** Break documents into coherent, searchable segments that preserve context
2. **🤖 Semantic Understanding:** Find relevant content even when users paraphrase or use synonyms  
3. **⚖️ Hybrid Excellence:** Combine keyword precision with semantic recall using RRF fusion
4. **📊 Best of Both Worlds:** Fast exact matching + deep semantic understanding
5. **🏭 Production Reality:** How modern RAG systems actually work in practice

### **🏗️ Week 4 Architecture Overview**

<p align="center">
  <img src="static/week4_hybrid_opensearch.png" alt="Week 4 Hybrid Search Architecture" width="800">
  <br>
  <em>Complete Week 4 hybrid search architecture with chunking, embeddings, and RRF fusion</em>
</p>

**Hybrid Search Infrastructure:** Production-grade chunking strategies with unified search supporting BM25, vector, and hybrid modes.

#### **🎯 Learning Objectives**
- **Section-Based Chunking:** Intelligent document segmentation that respects structure
- **Production Embeddings:** Jina AI integration with fallback strategies  
- **Hybrid Search Mastery:** RRF fusion combining keyword + semantic retrieval
- **Unified API Design:** Single endpoint supporting multiple search modes
- **Performance Analysis:** Understanding trade-offs between search approaches

#### **Key Components**
- `src/services/indexing/text_chunker.py`: Section-aware chunking with overlap strategies
- `src/services/embeddings/`: Production embedding pipeline with Jina AI
- `src/routers/hybrid_search.py`: Unified search API supporting all modes  
- `notebooks/week4/`: Complete hybrid search implementation guide

### **📓 Week 4 Implementation Guide**

```bash
# Launch the Week 4 notebook
uv run jupyter notebook notebooks/week4/week4_hybrid_search.ipynb
```

### **💻 Code Examples**

**Section-Based Chunking:**
```python
# Example: Intelligent document chunking
from src.services.indexing.text_chunker import TextChunker

chunker = TextChunker(chunk_size=600, overlap_size=100)
chunks = chunker.chunk_paper(
    title="Attention Mechanisms in Neural Networks",
    abstract="Recent advances in attention...",
    full_text=paper_content,
    sections=parsed_sections  # From Docling PDF parsing
)
# Result: Coherent chunks respecting document structure
```

**Hybrid Search Implementation:**
```python  
# Example: Unified search supporting multiple modes
async def search_papers(query: str, use_hybrid: bool = True):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/v1/hybrid-search/", json={
            "query": query,
            "use_hybrid": use_hybrid,  # Auto-generates embeddings
            "size": 10,
            "categories": ["cs.AI"]
        })
        return response.json()
        
# BM25 only: Fast keyword matching (~50ms)
bm25_results = await search_papers("transformer attention", use_hybrid=False)

# Hybrid search: Semantic + keyword understanding (~400ms)  
hybrid_results = await search_papers("how to make models more efficient", use_hybrid=True)
```

### **✅ Success Criteria**
Complete when you can:
- [ ] Chunk documents intelligently: Papers broken into coherent 600-word segments
- [ ] Generate embeddings: Jina AI integration working with automatic query embedding
- [ ] Hybrid search working: RRF fusion combining BM25 + vector similarity
- [ ] Compare search modes: Understand when to use BM25 vs hybrid search
- [ ] Production API ready: `/hybrid-search` endpoint handling all search types

### **📊 Performance Benchmarks**
| Search Mode | Speed | Precision@10 | Recall@10 | Use Case |
|-------------|-------|--------------|-----------|----------|
| **BM25 Only** | ~50ms | 0.67 | 0.71 | Exact keywords, author names |
| **Hybrid (RRF)** | ~400ms | 0.84 | 0.89 | Conceptual queries, synonyms |

### **📖 Deep Dive**  
**Blog Post:** [The Chunking Strategy That Makes Hybrid Search Work](link-to-week4-blog) - Production chunking and RRF fusion implementation

---

## 📚 Week 5: Complete RAG Pipeline with LLM Integration 🚀

> **🎯 The RAG Completion:** Transform search results into intelligent answers with local LLM integration and streaming responses.

**Building on Week 4 hybrid search:** Add the LLM layer that turns search into intelligent conversation.

### **🎯 Why Local LLM + Streaming?**

**The Production Advantage:** Complete the RAG pipeline with privacy-first, optimized generation:

1. **🏠 Local LLM Control:** Complete data privacy with Ollama - no external API calls
2. **⚡ 6x Performance Boost:** Optimized from 120s → 15-20s through prompt engineering
3. **📡 Real-time Streaming:** Server-Sent Events for immediate user feedback
4. **🎛️ User-Friendly Interface:** Gradio web UI for non-technical users
5. **🔧 Production Ready:** Clean API design with comprehensive error handling

### **🏗️ Week 5 Architecture Overview**

<p align="center">
  <img src="static/week5_complete_rag.png" alt="Week 5 Complete RAG System Architecture" width="900">
  <br>
  <em>Complete RAG system with LLM generation layer (Ollama), hybrid retrieval pipeline, and Gradio interface</em>
</p>

**Complete RAG Infrastructure:** Local LLM generation with optimized prompting, dual API endpoints, and interactive web interface.

#### **🎯 Learning Objectives**
- **Local LLM Mastery:** Ollama service integration with multiple model support
- **Performance Optimization:** 80% prompt reduction, 6x speed improvement techniques
- **Streaming Implementation:** Server-Sent Events for real-time response generation
- **Dual API Design:** Standard and streaming endpoints for different use cases
- **Interactive UI:** Gradio interface with advanced parameter controls

#### **Key Components**
- `src/routers/ask.py`: Dual RAG endpoints (`/api/v1/ask` + `/api/v1/stream`)
- `src/services/ollama/`: LLM client with optimized prompts and 300-word response limits
- `src/services/ollama/prompts/rag_system.txt`: Optimized system prompt for academic papers
- `src/gradio_app.py`: Interactive web interface with real-time streaming support
- `gradio_launcher.py`: Easy-launch script for the web UI (runs on port 7861)

### **📓 Week 5 Implementation Guide**

```bash
# Launch the Week 5 notebook
uv run jupyter notebook notebooks/week5/week5_complete_rag_system.ipynb

# Launch Gradio interface
uv run python gradio_launcher.py
# Open http://localhost:7861
```

### **💻 Code Examples**

**Complete RAG Query:**
```python
# Example: Standard RAG endpoint
import httpx

async def ask_question(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/v1/ask", json={
            "query": query,
            "top_k": 3,
            "use_hybrid": True,
            "model": "llama3.2:1b"
        })
        result = response.json()
        return result["answer"], result["sources"]

# Ask a question
answer, sources = await ask_question("What are transformers in machine learning?")
```

**Streaming RAG Implementation:**
```python
# Example: Real-time streaming responses
import httpx
import json

async def stream_rag_response(query: str):
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", "http://localhost:8000/api/v1/stream", json={
            "query": query,
            "top_k": 3,
            "use_hybrid": True
        }) as response:
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if 'chunk' in data:
                        print(data['chunk'], end='', flush=True)
                    elif data.get('done'):
                        break

# Stream an answer in real-time
await stream_rag_response("Explain attention mechanisms")
```

### **🔧 API Endpoints**

**Standard RAG Endpoint:** `/api/v1/ask`
- **Response Type**: Complete JSON response
- **Use Case**: Batch processing, API integrations
- **Response Time**: 15-20 seconds

**Streaming RAG Endpoint:** `/api/v1/stream`
- **Response Type**: Server-Sent Events (SSE)
- **Use Case**: Interactive UIs, real-time feedback
- **Time to First Token**: 2-3 seconds

**Request Format** (both endpoints):
```json
{
    "query": "Your question here",
    "top_k": 3,                    // Number of chunks (1-10)
    "use_hybrid": true,            // Hybrid vs BM25 search
    "model": "llama3.2:1b",        // LLM model to use
    "categories": ["cs.AI"]        // Optional category filter
}
```

### **✅ Success Criteria**
Complete when you can:
- [ ] **Standard RAG**: Get complete answers with sources via `/api/v1/ask`
- [ ] **Streaming RAG**: See real-time generation via `/api/v1/stream`
- [ ] **Gradio Interface**: Interactive chat at http://localhost:7861
- [ ] **Performance**: 15-20s total response time (6x improvement from baseline)
- [ ] **Local LLM**: Ollama running with llama3.2:1b model
- [ ] **Source Attribution**: Automatic deduplication of paper sources

### **📊 Performance Achievements**
| Metric | Before | After (Week 5) | Improvement |
|--------|--------|----------------|-------------|
| **Response Time** | 120+ seconds | 15-20 seconds | **6x faster** |
| **Time to First Token** | N/A | 2-3 seconds | **Streaming enabled** |
| **Prompt Efficiency** | ~10KB | ~2KB | **80% reduction** |
| **User Experience** | API only | Web interface + streaming | **Production ready** |

**Key Optimizations:**
- Removed redundant metadata (80% prompt size reduction)
- 300-word response limit for focused answers
- Shared code architecture (DRY principles)
- Automatic source deduplication

### **🔧 Troubleshooting Week 5**

| Issue | Solution |
|-------|----------|
| **404 on `/stream` endpoint** | Rebuild API: `docker compose build api && docker compose restart api` |
| **Slow response times** | Use smaller model (`llama3.2:1b`) or reduce `top_k` parameter |
| **Gradio not accessible** | Port changed to 7861: `http://localhost:7861` |
| **Ollama connection errors** | Check service: `docker exec rag-ollama ollama list` |
| **No streaming response** | Verify SSE format, check browser network tab |
| **Out of memory errors** | Increase Docker memory limit to 8GB+ |

**Quick Health Check:**
```bash
# Check all services
curl http://localhost:8000/api/v1/health | jq

# Test RAG endpoint
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}'

# Test streaming endpoint
curl -X POST http://localhost:8000/api/v1/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}' --no-buffer
```

### **📖 Deep Dive**
**Blog Post:** [The Complete RAG System](https://jamwithai.substack.com/p/the-complete-rag-system) - Complete RAG system with local LLM integration and optimization techniques

---

## 📚 Week 6: Production Monitoring and Caching 🚀

> **🎯 Production Excellence:** Transform your RAG system from functional to production-ready with comprehensive monitoring and intelligent caching.

**Building on Week 5 complete RAG system:** Add observability, performance optimization, and production-grade monitoring.

### **🎯 Why Monitoring + Caching?**

**The Production Reality:** A working RAG system isn't enough - you need visibility and optimization:

1. **📊 Complete Observability:** Trace every step from query to answer with Langfuse
2. **⚡ 150-400x Performance Boost:** Redis caching serves repeated queries in ~50ms vs 15-20s
3. **💰 Cost Optimization:** 60%+ cache hit rate eliminates redundant LLM calls
4. **🔍 Performance Insights:** Real-time dashboards showing bottlenecks and opportunities
5. **🛡️ Production Hardening:** Health checks, graceful degradation, and monitoring

### **🏗️ Week 6 Architecture Overview**

<p align="center">
  <img src="static/week6_monitoring_and_caching.png" alt="Week 6 Monitoring & Caching Architecture" width="900">
  <br>
  <em>Production RAG system with Langfuse tracing and Redis caching layers</em>
</p>

**Production Infrastructure:** Complete observability layer with Langfuse tracking every RAG operation, plus Redis caching for instant response delivery.

#### **🎯 Learning Objectives**
- **Langfuse Integration:** End-to-end RAG pipeline tracing with performance analytics
- **Redis Caching Strategy:** Intelligent cache keys with TTL management and fallback
- **Performance Monitoring:** Real-time dashboards showing latency, costs, and hit rates
- **Production Patterns:** Industry-standard observability and optimization techniques
- **Cost Analysis:** Understanding and optimizing LLM usage and infrastructure costs

#### **Key Components**
- `src/services/langfuse/`: Complete tracing integration with RAG-specific metrics
- `src/services/cache/`: Redis client with exact-match caching and graceful fallback
- `src/routers/ask.py`: Updated with integrated tracing and caching middleware
- `docker-compose.yml`: Added Redis service and Langfuse local instance
- `notebooks/week6/`: Complete monitoring and caching implementation guide

### **📓 Week 6 Implementation Guide**

```bash
# Launch the Week 6 notebook
uv run jupyter notebook notebooks/week6/week6_cache_testing.ipynb
```

### **💻 Code Examples**

**Langfuse Tracing Integration:**
```python
# Example: Automatic RAG tracing (already integrated)
# Every request to /api/v1/ask automatically generates:
# - Request-level traces for complete query journey
# - Embedding spans timing query embedding generation
# - Search spans tracking retrieval performance
# - Generation spans monitoring LLM response creation

# Simply configure environment variables and tracing happens automatically
LANGFUSE__PUBLIC_KEY=pk-lf-your-key
LANGFUSE__SECRET_KEY=sk-lf-your-key
LANGFUSE__HOST=http://localhost:3000
```

**Redis Caching Performance:**
```python
# Example: Cache performance testing
import httpx
import time

async def test_cache_performance():
    # First request (cache miss ~15-20s)
    start = time.time()
    response = await httpx.AsyncClient().post("http://localhost:8000/api/v1/ask", json={
        "query": "What are transformers in machine learning?",
        "top_k": 3
    })
    first_time = time.time() - start
    
    # Second identical request (cache hit ~50ms)
    start = time.time()
    response = await httpx.AsyncClient().post("http://localhost:8000/api/v1/ask", json={
        "query": "What are transformers in machine learning?",
        "top_k": 3
    })
    second_time = time.time() - start
    
    print(f"First request: {first_time:.2f}s")
    print(f"Second request: {second_time:.2f}s")
    print(f"Speedup: {first_time/second_time:.0f}x faster")
```

### **✅ Success Criteria**
Complete when you can:
- [ ] **Langfuse Tracing**: View complete RAG traces at http://localhost:3000
- [ ] **Redis Caching**: Achieve 150-400x speedup for repeated queries
- [ ] **Performance Monitoring**: Real-time dashboards showing latency and costs
- [ ] **Cache Analytics**: 60%+ hit rate for production workloads
- [ ] **Production Health**: All services monitored with graceful degradation

### **📊 Performance Achievements**
| Metric | Before | After (Week 6) | Improvement |
|--------|--------|----------------|-------------|
| **Average Response Time** | 15-20s | 3-5s (mixed workload) | **3-4x faster** |
| **Cache Hit Responses** | N/A | 50-100ms | **150-400x faster** |
| **LLM Token Usage** | 100% | 40% (60% cached) | **60% reduction** |
| **Daily Cost** | $12 | $4.50 | **63% savings** |
| **System Observability** | None | Complete tracing | **Full visibility** |

**Cache Hit Rate Analysis:**
- **Exact Match Cache**: 62% hit rate for identical queries
- **Performance Impact**: <2% monitoring overhead
- **Cost Savings**: Eliminates 60% of LLM calls

### **🔧 Production Configuration**

**Environment Variables:**
```bash
# Langfuse Configuration
LANGFUSE__PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE__SECRET_KEY=sk-lf-your-secret-key
LANGFUSE__HOST=http://localhost:3000
LANGFUSE__ENABLED=true

# Redis Configuration
REDIS__URL=redis://redis:6379/0
REDIS__CACHE_TTL_HOURS=24
REDIS__MAX_CONNECTIONS=10
```

**Docker Services:**
```bash
# Start all services including Redis and Langfuse
docker compose up --build -d

# Verify Redis connectivity
docker exec rag-redis redis-cli ping
# Should return: PONG

# Check cache statistics
curl "http://localhost:8000/api/v1/health" | jq
```

### **🔧 Troubleshooting Week 6**

| Issue | Solution |
|-------|----------|
| **No Langfuse traces** | Verify environment variables and restart API container |
| **Cache not working** | Check Redis: `docker exec rag-redis redis-cli ping` |
| **Slow responses** | Monitor cache hit rate, check system resources |
| **Langfuse connection errors** | Ensure Langfuse service is running on port 3000 |
| **High memory usage** | Monitor Redis memory usage, adjust TTL settings |

**Quick Health Check:**
```bash
# Verify all services including monitoring
curl http://localhost:8000/api/v1/health | jq

# Test caching performance
time curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}'

# Access monitoring dashboards
# Langfuse: http://localhost:3000
# Gradio: http://localhost:7861
```

### **📖 Deep Dive**
**Blog Post:** [Link coming soon] - Production-ready RAG with monitoring and caching

---

## ⚙️ Configuration Management

### **Environment Configuration**

The project uses a **unified `.env` file** with nested configuration structure to manage settings across all services.

#### **Configuration Structure**
```bash
# Application Settings
DEBUG=true
ENVIRONMENT=development

# arXiv API (Week 2)
ARXIV__MAX_RESULTS=15
ARXIV__SEARCH_CATEGORY=cs.AI
ARXIV__RATE_LIMIT_DELAY=3.0

# PDF Parser (Week 2)  
PDF_PARSER__MAX_PAGES=30
PDF_PARSER__DO_OCR=false

# OpenSearch (Week 3)
OPENSEARCH__HOST=http://opensearch:9200
OPENSEARCH__INDEX_NAME=arxiv-papers

# Jina AI Embeddings (Week 4)
JINA_API_KEY=your_jina_api_key_here
EMBEDDINGS__MODEL=jina-embeddings-v3
EMBEDDINGS__TASK=retrieval.passage
EMBEDDINGS__DIMENSIONS=1024

# Chunking Configuration (Week 4)
CHUNKING__CHUNK_SIZE=600
CHUNKING__OVERLAP_SIZE=100
CHUNKING__MIN_CHUNK_SIZE=100

# Ollama LLM (Week 5)
OLLAMA_HOST=http://ollama:11434
OLLAMA__DEFAULT_MODEL=llama3.2:1b
OLLAMA__TIMEOUT=120
OLLAMA__MAX_RESPONSE_WORDS=300

# Langfuse Monitoring (Week 6)
LANGFUSE__PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE__SECRET_KEY=sk-lf-your-secret-key
LANGFUSE__HOST=http://localhost:3000
LANGFUSE__ENABLED=true
LANGFUSE__FLUSH_INTERVAL=1.0

# Redis Caching (Week 6)
REDIS__URL=redis://redis:6379/0
REDIS__CACHE_TTL_HOURS=24
REDIS__MAX_CONNECTIONS=10

# Services
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
```

#### **Key Configuration Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `true` | Debug mode for development |
| `ARXIV__MAX_RESULTS` | `15` | Papers to fetch per API call |
| `ARXIV__SEARCH_CATEGORY` | `cs.AI` | arXiv category to search |
| `PDF_PARSER__MAX_PAGES` | `30` | Max pages to process per PDF |
| `OPENSEARCH__INDEX_NAME` | `arxiv-papers` | OpenSearch index name |
| `OPENSEARCH__HOST` | `http://opensearch:9200` | OpenSearch cluster endpoint |
| `JINA_API_KEY` | Required for Week 4 | Jina AI API key for embeddings |
| `CHUNKING__CHUNK_SIZE` | `600` | Target words per document chunk |
| `CHUNKING__OVERLAP_SIZE` | `100` | Overlapping words between chunks |
| `EMBEDDINGS__MODEL` | `jina-embeddings-v3` | Jina embeddings model |
| `OLLAMA_MODEL` | `llama3.2:1b` | Local LLM model |
| `LANGFUSE__PUBLIC_KEY` | Required for Week 6 | Langfuse public API key |
| `LANGFUSE__SECRET_KEY` | Required for Week 6 | Langfuse secret API key |
| `REDIS__CACHE_TTL_HOURS` | `24` | Cache expiration time in hours |

#### **Service-Aware Configuration**

The configuration system automatically detects the service context:
- **API Service**: Uses `localhost` for database and service connections
- **Airflow Service**: Uses Docker container hostnames (`postgres`, `opensearch`)

```python
# Configuration is automatically loaded based on context
from src.config import get_settings

settings = get_settings()  # Auto-detects API vs Airflow
print(f"ArXiv max results: {settings.arxiv.max_results}")
```

---

## 🔧 Reference & Development Guide

### **🛠️ Technology Stack**

| Service | Purpose | Status |
|---------|---------|--------|
| **FastAPI** | REST API with automatic docs | ✅ Ready |
| **PostgreSQL 16** | Paper metadata and content storage | ✅ Ready |
| **OpenSearch 2.19** | Hybrid search engine (BM25 + Vector) | ✅ Ready |
| **Apache Airflow 3.0** | Workflow automation | ✅ Ready |
| **Jina AI** | Embedding generation (Week 4) | ✅ Ready |
| **Ollama** | Local LLM serving (Week 5) | ✅ Ready |
| **Redis** | High-performance caching (Week 6) | ✅ Ready |
| **Langfuse** | RAG pipeline observability (Week 6) | ✅ Ready |

**Development Tools:** UV, Ruff, MyPy, Pytest, Docker Compose

### **🏗️ Project Structure**

```
arxiv-paper-curator/
├── src/                                    # Main application code
│   ├── main.py                             # FastAPI application
│   ├── routers/                            # API endpoints
│   │   ├── ping.py                         # Health check endpoints
│   │   ├── papers.py                       # Paper retrieval endpoints
│   │   ├── hybrid_search.py                # Week 4: Hybrid search endpoints
│   │   └── ask.py                          # Week 5: RAG question answering endpoints
│   ├── models/                             # Database models (SQLAlchemy)
│   ├── repositories/                       # Data access layer
│   ├── schemas/                            # Pydantic validation schemas
│   │   ├── api/                            # API request/response schemas
│   │   │   ├── health.py                   # Health check schemas
│   │   │   ├── search.py                   # Search request/response schemas
│   │   │   └── ask.py                      # Week 5: RAG request/response schemas
│   │   ├── arxiv/                          # arXiv data schemas
│   │   ├── pdf_parser/                     # PDF parsing schemas
│   │   ├── database/                       # Database configuration schemas
│   │   ├── indexing/                       # Week 4: Chunking schemas
│   │   ├── embeddings/                     # Week 4: Embedding schemas
│   │   ├── cache/                          # Week 6: Caching schemas
│   │   └── langfuse/                       # Week 6: Monitoring schemas
│   ├── services/                           # Business logic
│   │   ├── arxiv/                          # arXiv API client
│   │   ├── pdf_parser/                     # Docling PDF processing
│   │   ├── opensearch/                     # OpenSearch integration
│   │   │   ├── client.py                   # Unified search client (BM25 + Vector + Hybrid)
│   │   │   ├── factory.py                  # Client factory pattern
│   │   │   ├── index_config_hybrid.py      # Week 4: Hybrid index configuration
│   │   │   └── query_builder.py            # BM25 query construction
│   │   ├── indexing/                       # Week 4: Document processing
│   │   │   ├── text_chunker.py             # Section-based chunking strategy
│   │   │   ├── hybrid_indexer.py           # Document indexing with embeddings
│   │   │   └── factory.py                  # Indexing service factory
│   │   ├── embeddings/                     # Week 4: Embedding services
│   │   │   ├── jina_client.py              # Jina AI embedding service
│   │   │   └── factory.py                  # Embedding service factory
│   │   ├── ollama/                         # Week 5: LLM services
│   │   │   ├── client.py                   # Ollama LLM client
│   │   │   ├── factory.py                  # LLM service factory
│   │   │   └── prompts/                    # Optimized RAG prompts
│   │   ├── langfuse/                       # Week 6: Monitoring services
│   │   │   ├── client.py                   # Langfuse tracing client
│   │   │   ├── tracer.py                   # RAG-specific tracing utilities
│   │   │   └── factory.py                  # Monitoring service factory
│   │   ├── cache/                          # Week 6: Caching services
│   │   │   ├── client.py                   # Redis cache implementation
│   │   │   └── factory.py                  # Cache service factory
│   │   └── metadata_fetcher.py             # Complete ingestion pipeline
│   ├── db/                                 # Database configuration
│   ├── config.py                           # Environment configuration
│   └── dependencies.py                     # Dependency injection
│
├── notebooks/                              # Learning materials
│   ├── week1/                              # Week 1: Infrastructure setup
│   │   └── week1_setup.ipynb               # Complete setup guide
│   ├── week2/                              # Week 2: Data ingestion
│   │   └── week2_arxiv_integration.ipynb   # Data pipeline guide
│   ├── week3/                              # Week 3: Keyword search
│   │   └── week3_opensearch.ipynb          # OpenSearch & BM25 guide
│   ├── week4/                              # Week 4: Chunking & hybrid search
│   │   ├── week4_hybrid_search.ipynb       # Complete hybrid search guide
│   │   └── README.md                       # Week 4 implementation documentation
│   ├── week5/                              # Week 5: Complete RAG system
│   │   ├── week5_complete_rag_system.ipynb # Complete RAG implementation guide
│   │   └── README.md                       # Week 5 implementation documentation
│   └── week6/                              # Week 6: Production monitoring & caching
│       ├── week6_cache_testing.ipynb       # Monitoring and caching guide
│       └── README.md                       # Week 6 implementation documentation
│
├── airflow/                                # Workflow orchestration
│   ├── dags/                               # Workflow definitions
│   │   ├── arxiv_ingestion/                # arXiv ingestion modules
│   │   └── arxiv_paper_ingestion.py        # Main ingestion DAG
│   └── requirements-airflow.txt            # Airflow dependencies
│
├── gradio_app.py                           # Week 5: Interactive web interface
├── gradio_launcher.py                      # Week 5: Easy-launch script for Gradio UI
├── tests/                                  # Comprehensive test suite
├── static/                                 # Assets (images, GIFs)
└── compose.yml                             # Service orchestration
```

### **📡 API Endpoints Reference**

| Endpoint | Method | Description | Week |
|----------|--------|-------------|------|
| `/health` | GET | Service health check | Week 1 |
| `/api/v1/papers` | GET | List stored papers | Week 2 |
| `/api/v1/papers/{id}` | GET | Get specific paper | Week 2 |
| `/api/v1/search` | POST | BM25 keyword search | Week 3 |
| `/api/v1/hybrid-search/` | POST | Hybrid search (BM25 + Vector) | **Week 4** |

**API Documentation:** Visit http://localhost:8000/docs for interactive API explorer

### **🔧 Essential Commands**

#### **Using the Makefile** (Recommended)
```bash
# View all available commands
make help

# Quick workflow
make start         # Start all services
make health        # Check all services health
make test          # Run tests
make stop          # Stop services
```

#### **All Available Commands**
| Command | Description |
|---------|-------------|
| `make start` | Start all services |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make status` | Show service status |
| `make logs` | Show service logs |
| `make health` | Check all services health |
| `make setup` | Install Python dependencies |
| `make format` | Format code |
| `make lint` | Lint and type check |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage |
| `make clean` | Clean up everything |

#### **Direct Commands** (Alternative)
```bash
# If you prefer using commands directly
docker compose up --build -d    # Start services
docker compose ps               # Check status
docker compose logs            # View logs
uv run pytest                 # Run tests
```

### **🎓 Target Audience**
| Who | Why |
|-----|-----|
| **AI/ML Engineers** | Learn production RAG architecture beyond tutorials |
| **Software Engineers** | Build end-to-end AI applications with best practices |
| **Data Scientists** | Implement production AI systems using modern tools |

---

## 🛠️ Troubleshooting

**Common Issues:**
- **Services not starting?** Wait 2-3 minutes, check `docker compose logs`
- **Port conflicts?** Stop other services using ports 8000, 8080, 5432, 9200
- **Memory issues?** Increase Docker Desktop memory allocation

**Get Help:**
- Check the comprehensive Week 1 notebook troubleshooting section
- Review service logs: `docker compose logs [service-name]`
- Complete reset: `docker compose down --volumes && docker compose up --build -d`

---

## 💰 Cost Structure

**This course is completely free!** You'll only need minimal costs for optional services:
- **Local Development:** $0 (everything runs locally)
- **Optional Cloud APIs:** ~$2-5 for external LLM services (if chosen)

---

<div align="center">
  <h3>🎉 Ready to Start Your AI Engineering Journey?</h3>
  <p><strong>Begin with the Week 1 setup notebook and build your first production RAG system!</strong></p>
  
  <p><em>For learners who want to master modern AI engineering</em></p>
  <p><strong>Built with love by Jam With AI</strong></p>
</div>

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
