"""Tests for agentic RAG node functions using Runtime[Context] pattern."""

import pytest
from unittest.mock import AsyncMock, Mock
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.runtime import Runtime

from src.domain_profiles import get_domain_profile
from src.services.agents.nodes import (
    ainvoke_guardrail_step,
    ainvoke_retrieve_step,
    ainvoke_grade_documents_step,
    ainvoke_rewrite_query_step,
    ainvoke_generate_answer_step,
    ainvoke_out_of_scope_step,
    continue_after_guardrail,
)
from src.services.agents.nodes.utils import extract_sources_from_tool_messages, get_latest_query, get_latest_context
from src.services.agents.nodes.rewrite_query_node import QueryRewriteOutput
from src.services.agents.models import GuardrailScoring, GradeDocuments
from src.services.agents.state import AgentState


class TestGuardrailNode:
    """Tests for guardrail validation node."""

    def test_continue_after_guardrail_pass(self, test_context):
        """Test routing decision after guardrail pass."""
        state: AgentState = {
            "messages": [],
            "retrieval_attempts": 0,
            "guardrail_result": GuardrailScoring(score=75, reason="Pass"),
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = continue_after_guardrail(state, runtime)

        assert result == "continue"

    def test_continue_after_guardrail_fail(self, test_context):
        """Test routing decision after guardrail fail."""
        state: AgentState = {
            "messages": [],
            "retrieval_attempts": 0,
            "guardrail_result": GuardrailScoring(score=30, reason="Fail"),
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = continue_after_guardrail(state, runtime)

        assert result == "out_of_scope"

    @pytest.mark.asyncio
    async def test_guardrail_prompt_is_scoped_to_active_domain(self, test_context, sample_human_message):
        """Guardrail prompt must describe the active domain, not always arXiv (Stage 2)."""
        test_context.domain = "education"
        structured_llm = test_context.llm_client.get_langchain_model.return_value.with_structured_output.return_value
        structured_llm.ainvoke = AsyncMock(return_value=GuardrailScoring(score=90, reason="On topic"))

        state: AgentState = {"messages": [sample_human_message], "retrieval_attempts": 0}
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        await ainvoke_guardrail_step(state, runtime)

        sent_prompt = structured_llm.ainvoke.call_args[0][0]
        assert get_domain_profile("education").label in sent_prompt
        assert "arXiv" not in sent_prompt


class TestRetrieveNode:
    """Tests for document retrieval node."""

    @pytest.mark.asyncio
    async def test_retrieve_creates_tool_call(self, test_context, sample_human_message):
        """Test retrieve node creates tool call."""
        state: AgentState = {
            "messages": [sample_human_message],
            "retrieval_attempts": 0,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_retrieve_step(state, runtime)

        assert "retrieval_attempts" in result
        assert result["retrieval_attempts"] == 1
        assert "messages" in result
        assert isinstance(result["messages"][0], AIMessage)
        assert len(result["messages"][0].tool_calls) > 0
        assert result["messages"][0].tool_calls[0]["name"] == "retrieve_papers"

    @pytest.mark.asyncio
    async def test_retrieve_max_attempts_reached(self, test_context, sample_human_message):
        """Test retrieve node when max attempts reached."""
        state: AgentState = {
            "messages": [sample_human_message],
            "retrieval_attempts": 2,  # Already at max
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_retrieve_step(state, runtime)

        assert "messages" in result
        assert isinstance(result["messages"][0], AIMessage)
        # Check that message indicates failure to find papers
        content_lower = result["messages"][0].content.lower()
        assert "apologize" in content_lower or "unable" in content_lower or "couldn't find" in content_lower


class TestGradeDocumentsNode:
    """Tests for document grading node."""

    @pytest.mark.asyncio
    async def test_grade_documents_relevant(self, test_context, sample_human_message, sample_tool_message):
        """Test grading node with relevant documents."""
        structured_llm = test_context.llm_client.get_langchain_model.return_value.with_structured_output.return_value
        structured_llm.ainvoke = AsyncMock(return_value=GradeDocuments(
            binary_score="yes",
            reasoning="Document discusses transformers which is relevant"
        ))

        state: AgentState = {
            "messages": [sample_human_message, sample_tool_message],
            "retrieval_attempts": 1,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_grade_documents_step(state, runtime)

        assert "grading_results" in result

    @pytest.mark.asyncio
    async def test_grade_documents_not_relevant(self, test_context, sample_human_message, sample_tool_message):
        """Test grading node with irrelevant documents."""
        structured_llm = test_context.llm_client.get_langchain_model.return_value.with_structured_output.return_value
        structured_llm.ainvoke = AsyncMock(return_value=GradeDocuments(
            binary_score="no",
            reasoning="Document is not relevant to the query"
        ))

        state: AgentState = {
            "messages": [sample_human_message, sample_tool_message],
            "retrieval_attempts": 1,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_grade_documents_step(state, runtime)

        assert "grading_results" in result

    @pytest.mark.asyncio
    async def test_grade_documents_populates_relevant_sources_from_retriever_artifact(
        self, test_context, sample_human_message
    ):
        """relevant_sources must come from the retriever tool's artifact (structured
        Document metadata), not stay empty - see AgenticRAGService._extract_sources,
        which is what /ask-agentic actually returns to the client."""
        structured_llm = test_context.llm_client.get_langchain_model.return_value.with_structured_output.return_value
        structured_llm.ainvoke = AsyncMock(return_value=GradeDocuments(binary_score="yes", reasoning="Relevant"))

        retriever_message = ToolMessage(
            content="[1. 1706.03762]\nTransformers use self-attention.",
            tool_call_id="retrieve_1",
            name="retrieve_papers",
            artifact=[
                Document(
                    page_content="Transformers use self-attention.",
                    metadata={
                        "arxiv_id": "1706.03762",
                        "title": "Attention Is All You Need",
                        "authors": "Vaswani et al.",
                        "score": 0.95,
                        "source": "https://arxiv.org/pdf/1706.03762.pdf",
                    },
                )
            ],
        )

        state: AgentState = {
            "messages": [sample_human_message, retriever_message],
            "retrieval_attempts": 1,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_grade_documents_step(state, runtime)

        assert "relevant_sources" in result
        assert len(result["relevant_sources"]) == 1
        source = result["relevant_sources"][0]
        assert source.arxiv_id == "1706.03762"
        assert source.url == "https://arxiv.org/pdf/1706.03762.pdf"


class TestRewriteQueryNode:
    """Tests for query rewriting node."""

    @pytest.mark.asyncio
    async def test_rewrite_query_success(self, test_context, sample_human_message):
        """Test query rewriting with LLM."""
        structured_llm = test_context.llm_client.get_langchain_model.return_value.with_structured_output.return_value
        structured_llm.ainvoke = AsyncMock(return_value=QueryRewriteOutput(
            rewritten_query="What are the key concepts in transformer neural network architectures?",
            reasoning="Expanded query with technical terms",
        ))

        state: AgentState = {
            "messages": [sample_human_message],
            "retrieval_attempts": 1,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_rewrite_query_step(state, runtime)

        assert "messages" in result
        assert isinstance(result["messages"][0], HumanMessage)
        assert len(result["messages"][0].content) > 0
        assert "rewritten_query" in result


class TestGenerateAnswerNode:
    """Tests for answer generation node."""

    @pytest.mark.asyncio
    async def test_generate_answer_success(self, test_context, sample_human_message, sample_tool_message):
        """Test answer generation with context."""
        llm = test_context.llm_client.get_langchain_model.return_value
        llm.ainvoke = AsyncMock(return_value=AIMessage(
            content="Based on the papers, transformers are neural network architectures."
        ))

        state: AgentState = {
            "messages": [sample_human_message, sample_tool_message],
            "retrieval_attempts": 1,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_generate_answer_step(state, runtime)

        assert "messages" in result
        assert isinstance(result["messages"][0], AIMessage)
        assert len(result["messages"][0].content) > 0

    @pytest.mark.asyncio
    async def test_generate_answer_prompt_is_scoped_to_active_domain(
        self, test_context, sample_human_message, sample_tool_message
    ):
        """Answer prompt must cite sources per the active domain, not always arXiv IDs (Stage 2)."""
        test_context.domain = "accounting"
        llm = test_context.llm_client.get_langchain_model.return_value
        llm.ainvoke = AsyncMock(return_value=AIMessage(content="Per IFRS 16..."))

        state: AgentState = {
            "messages": [sample_human_message, sample_tool_message],
            "retrieval_attempts": 1,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        await ainvoke_generate_answer_step(state, runtime)

        sent_prompt = llm.ainvoke.call_args[0][0]
        profile = get_domain_profile("accounting")
        assert profile.label in sent_prompt
        assert profile.citation_style in sent_prompt


class TestOutOfScopeNode:
    """Tests for out-of-scope handling node."""

    @pytest.mark.asyncio
    async def test_out_of_scope_response(self, test_context, sample_human_message):
        """Test out-of-scope helpful rejection (static response, no LLM call)."""
        state: AgentState = {
            "messages": [sample_human_message],
            "retrieval_attempts": 0,
        }
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_out_of_scope_step(state, runtime)

        assert "messages" in result
        assert isinstance(result["messages"][0], AIMessage)

    @pytest.mark.asyncio
    async def test_out_of_scope_message_is_scoped_to_active_domain(self, test_context, sample_human_message):
        """Rejection message must describe the active domain, not always arXiv/CS/AI/ML (Stage 2)."""
        test_context.domain = "education"
        state: AgentState = {"messages": [sample_human_message], "retrieval_attempts": 0}
        runtime = Mock(spec=Runtime)
        runtime.context = test_context

        result = await ainvoke_out_of_scope_step(state, runtime)

        message = result["messages"][0].content
        assert get_domain_profile("education").label in message
        assert "arXiv" not in message


class TestExtractSourcesFromToolMessages:
    """Tests for extract_sources_from_tool_messages (see nodes/utils.py)."""

    def test_builds_source_items_from_retriever_artifact(self):
        message = ToolMessage(
            content="irrelevant for this test",
            tool_call_id="call_1",
            name="retrieve_papers",
            artifact=[
                Document(
                    page_content="text",
                    metadata={
                        "arxiv_id": "1706.03762",
                        "title": "Attention Is All You Need",
                        "authors": "Vaswani et al., Shazeer et al.",
                        "score": 0.95,
                        "source": "https://arxiv.org/pdf/1706.03762.pdf",
                    },
                )
            ],
        )

        sources = extract_sources_from_tool_messages([message])

        assert len(sources) == 1
        assert sources[0].arxiv_id == "1706.03762"
        assert sources[0].title == "Attention Is All You Need"
        assert sources[0].authors == ["Vaswani et al.", "Shazeer et al."]
        assert sources[0].url == "https://arxiv.org/pdf/1706.03762.pdf"
        assert sources[0].relevance_score == 0.95

    def test_ignores_tool_messages_from_other_tools(self):
        message = ToolMessage(content="some other tool result", tool_call_id="call_1", name="some_other_tool")

        assert extract_sources_from_tool_messages([message]) == []

    def test_returns_empty_list_when_no_tool_messages(self, sample_human_message, sample_ai_message):
        assert extract_sources_from_tool_messages([sample_human_message, sample_ai_message]) == []

    def test_handles_missing_artifact_gracefully(self):
        """A retrieve_papers ToolMessage invoked outside ToolNode (e.g. directly via
        {"query": ...}) has no .artifact - must not crash."""
        message = ToolMessage(content="text only", tool_call_id="call_1", name="retrieve_papers")

        assert extract_sources_from_tool_messages([message]) == []


class TestNodeUtils:
    """Tests for node utility functions."""

    def test_get_latest_query(self, sample_human_message, sample_ai_message):
        """Test extracting latest query from messages."""
        messages = [sample_human_message, sample_ai_message]
        query = get_latest_query(messages)

        assert query == "What is machine learning?"

    def test_get_latest_query_with_multiple_human_messages(self):
        """Test extracting latest query with multiple human messages."""
        messages = [
            HumanMessage(content="First query"),
            AIMessage(content="First response"),
            HumanMessage(content="Second query"),
        ]
        query = get_latest_query(messages)

        assert query == "Second query"

    def test_get_latest_context(self, sample_tool_message):
        """Test extracting tool message context."""
        messages = [HumanMessage(content="Query"), sample_tool_message]
        context = get_latest_context(messages)

        assert context is not None
        assert "Transformers" in context

    def test_get_latest_context_no_tool_messages(self, sample_human_message):
        """Test extracting context when no tool messages exist."""
        messages = [sample_human_message]
        context = get_latest_context(messages)

        assert context == ""
