# Week 3: Keyword Search First - The Critical Foundation

> **🚨 The 90% Problem:** Most RAG systems jump straight to vector search and miss the foundation that powers the best retrieval systems. We're doing it right!

This folder contains the materials for Week 3 of the arXiv Paper Curator project, where we implement the **keyword search foundation** that professional RAG systems rely on using OpenSearch and BM25 scoring.

## 🎯 Why Keyword Search First?

**The Professional Path:** Unlike tutorials that jump straight to vector embeddings, we build the foundation that successful companies use:

1. **🔍 Exact Match Power:** Keywords excel at finding specific technical terms, paper IDs, and precise phrases
2. **📊 Interpretable Results:** You can understand exactly why a paper was retrieved 
3. **⚡ Speed & Efficiency:** BM25 is computationally fast and doesn't require expensive embedding models
4. **📈 Production Reality:** Companies like Elasticsearch, Algolia, and enterprise search use keyword search as their foundation

**The Learning Path:**
```
Week 3: Master BM25 keyword search    ← YOU ARE HERE
Week 4: Add intelligent chunking
Week 5: Introduce vector embeddings for hybrid retrieval  
Week 6: Optimize the complete system
```

## 🚀 Before You Start

**Essential Environment Setup:**
```bash
# 1. Ensure you have the correct environment configuration
cp .env.example .env

# 2. Verify OpenSearch settings are properly configured
# Your .env should contain these critical Week 3 settings:
# OPENSEARCH__HOST=http://opensearch:9200
# OPENSEARCH__INDEX_NAME=arxiv-papers
```

**Important:** Week 3 requires the `.env` file to be properly configured for OpenSearch connectivity and indexing. The defaults in `.env.example` work out of the box.

## Contents

### `week3_opensearch.ipynb`
A comprehensive Jupyter notebook that guides you through building the keyword search foundation:

1. **Infrastructure Validation**
   - Verify all Week 1-2 services are running correctly
   - OpenSearch cluster health and connectivity testing
   - Environment setup for Week 3 search components

2. **OpenSearch Service Integration**
   - Building a production-grade search client with factory patterns
   - Implementing dependency injection with FastAPI lifespan management
   - Creating JSON-based index configurations with proper analyzers

## 🔍 OpenSearch Dashboard in Action

*You'll add your OpenSearch dashboard screenshot here showing real paper searches with BM25 scoring and result rankings.*

<p align="center">
  <img src="../../static/week3_opensearch_dashboard.png" alt="OpenSearch Dashboard Retrieving Papers" width="800">
  <br>
  <em>OpenSearch Dashboards showing keyword search results with BM25 relevance scoring</em>
</p>

**Search Architecture Overview:**
- **OpenSearch Client**: Factory-pattern service with health monitoring and CRUD operations
- **Query Builder**: Advanced search query construction with field boosting and filtering
- **Index Management**: JSON-based schema with English analyzers and strict mapping
- **Search API**: RESTful endpoints (`/search`) with GET/POST methods for different query types
- **BM25 Algorithm**: Industry-standard text relevance scoring with multi-field search

3. **Index Management & Schema Design**
   - Creating indexes with proper field mappings for academic papers
   - Implementing English language analyzers for improved search relevance
   - Testing index health, statistics, and document management operations

4. **Document Indexing Pipeline**
   - Migrating paper data from PostgreSQL to OpenSearch
   - Bulk indexing operations with error handling and validation
   - Real-time indexing verification and performance monitoring

5. **BM25 Search Implementation**
   - Multi-field search across title, abstract, and content with field boosting
   - Advanced query features: highlighting, pagination, category filtering
   - Testing two-letter queries (AI, ML, NN, CV) as specifically requested
   - Fuzzy matching and typo tolerance configuration

6. **Search API Development**
   - FastAPI integration with OpenSearch dependency injection
   - RESTful endpoints: `GET /search` for simple queries, `POST /search` for advanced search
   - Response formatting with pagination, metadata, and highlighted snippets
   - Error handling and service health monitoring endpoints

7. **Airflow Pipeline Updates**
   - Sequential task execution: setup → fetch → opensearch → report → cleanup
   - Real OpenSearch indexing replacing placeholder operations
   - Updated daily reporting with search statistics and health metrics
   - Graceful handling of PDF processing limits (>20MB or >30 pages)

8. **End-to-End Pipeline Verification**
   - Complete flow testing: arXiv API → PostgreSQL → OpenSearch → Search API
   - Performance benchmarking and response time measurement
   - Production readiness assessment with monitoring and alerting

**Week 3 Architecture:**

<p align="center">
  <img src="../../static/week3_opensearch_flow.png" alt="Week 3 OpenSearch Flow Architecture" width="800">
  <br>
  <em>Complete Week 3 architecture showing the OpenSearch integration flow</em>
</p>


## Key Features Implemented

### 🔍 **Production-Grade Search System**
- **BM25 Scoring**: Industry-standard relevance ranking algorithm
- **Multi-field Search**: Query across title (3x boost), abstract (2x boost), and content (1x boost)
- **Advanced Filtering**: Category filtering, date ranges, and custom field queries
- **Real-time Highlighting**: Search term highlighting in results with HTML markup
- **Pagination Support**: Efficient large result set handling with size/from parameters

### 🏗️ **Clean Architecture Implementation**
- **Factory Pattern**: Consistent service creation across all components
- **Dependency Injection**: Proper service lifecycle management with FastAPI lifespan
- **Query Builder Pattern**: Flexible search query construction for complex operations
- **Error Handling**: Comprehensive exception management with graceful degradation

### 📊 **Performance & Monitoring**
- **Sub-100ms Search**: Optimized query performance for real-time applications
- **Health Monitoring**: Cluster status, index statistics, and service availability
- **Resource Limits**: PDF processing constraints to prevent memory issues
- **Scalability**: Design patterns supporting horizontal scaling

### 🔧 **Development Best Practices**
- **Type Safety**: Full type hints throughout the codebase
- **Testing**: End-to-end verification with realistic data scenarios
- **Documentation**: Comprehensive docstrings and architectural explanations
- **Code Quality**: Following established patterns from Week 1-2 implementations

## Expected Outcomes

By completing Week 3, students will have:

1. **Working Search System**: Fully functional OpenSearch BM25 search with 28+ indexed papers
2. **RESTful API**: Complete search API with both simple and advanced query capabilities  
3. **Production Architecture**: Clean, scalable code following industry best practices
4. **Performance Insights**: Understanding of search optimization and monitoring strategies
5. **End-to-End Pipeline**: Complete RAG system foundation ready for Week 4 development

## Success Criteria

- ✅ **OpenSearch Integration**: Factory pattern service with health checks operational
- ✅ **BM25 Search**: Relevance scoring with multi-field queries returning relevant results
- ✅ **Advanced Features**: Filtering, highlighting, pagination, and fuzzy search working
- ✅ **API Endpoints**: RESTful search with both GET and POST methods functional
- ✅ **Two-Letter Queries**: AI, ML, NN, CV queries working as specifically requested
- ✅ **Pipeline Integration**: Airflow DAGs updated for OpenSearch indexing
- ✅ **Performance**: Sub-100ms search response times with proper error handling

## What's Next?

**Week 4 Preview**: Chunking Strategies and Hybrid Retrieval
- Intelligent document chunking strategies for better context preservation
- Combining keyword search (BM25) with vector embeddings for hybrid retrieval
- Building the complete foundation for modern RAG systems
- Evaluation metrics to measure retrieval quality

---

**Ready to build production-grade search? Let's get started with Week 3!** 🔍✨