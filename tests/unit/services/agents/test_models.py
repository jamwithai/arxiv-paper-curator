import pytest
from pydantic import ValidationError
from src.services.agents.models import (
    GradeDocuments,
    GradingResult,
    GuardrailScoring,
    ReasoningStep,
    RoutingDecision,
    SourceItem,
    ToolArtefact,
)


class TestGuardrailScoring:
    """Tests for GuardrailScoring model."""

    def test_valid_scoring(self):
        """Test creating valid guardrail scoring."""
        scoring = GuardrailScoring(score=75, reason="Query is relevant to AI research papers")
        assert scoring.score == 75
        assert scoring.reason == "Query is relevant to AI research papers"

    def test_score_boundaries(self):
        """Test score boundary validation."""
        # Valid boundaries
        GuardrailScoring(score=0, reason="Minimum score")
        GuardrailScoring(score=100, reason="Maximum score")
        GuardrailScoring(score=50, reason="Middle score")

    def test_invalid_score_too_low(self):
        """Test score below minimum."""
        with pytest.raises(ValidationError):
            GuardrailScoring(score=-1, reason="Invalid")

    def test_invalid_score_too_high(self):
        """Test score above maximum."""
        with pytest.raises(ValidationError):
            GuardrailScoring(score=101, reason="Invalid")


class TestGradeDocuments:
    """Tests for GradeDocuments model."""

    def test_valid_yes_grade(self):
        """Test creating valid 'yes' grade."""
        grade = GradeDocuments(binary_score="yes", reasoning="Document is highly relevant")
        assert grade.binary_score == "yes"
        assert grade.reasoning == "Document is highly relevant"

    def test_valid_no_grade(self):
        """Test creating valid 'no' grade."""
        grade = GradeDocuments(binary_score="no", reasoning="Document is off-topic")
        assert grade.binary_score == "no"
        assert grade.reasoning == "Document is off-topic"

    def test_default_reasoning(self):
        """Test default empty reasoning."""
        grade = GradeDocuments(binary_score="yes")
        assert grade.reasoning == ""

    def test_invalid_binary_score(self):
        """Test invalid binary score value."""
        with pytest.raises(ValidationError):
            GradeDocuments(binary_score="maybe")


class TestSourceItem:
    """Tests for SourceItem model."""

    def test_valid_source_item(self):
        """Test creating valid source item."""
        source = SourceItem(
            arxiv_id="1706.03762",
            title="Attention Is All You Need",
            authors=["Vaswani, A.", "Shazeer, N."],
            url="https://arxiv.org/abs/1706.03762",
            relevance_score=0.95,
        )
        assert source.arxiv_id == "1706.03762"
        assert source.title == "Attention Is All You Need"
        assert len(source.authors) == 2
        assert source.url == "https://arxiv.org/abs/1706.03762"
        assert source.relevance_score == 0.95

    def test_default_values(self):
        """Test default field values."""
        source = SourceItem(arxiv_id="1234.5678", title="Test Paper", url="https://arxiv.org/abs/1234.5678")
        assert source.authors == []
        assert source.relevance_score == 0.0

    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        source = SourceItem(
            arxiv_id="1706.03762",
            title="Attention Is All You Need",
            authors=["Vaswani, A."],
            url="https://arxiv.org/abs/1706.03762",
            relevance_score=0.95,
        )
        source_dict = source.to_dict()

        assert isinstance(source_dict, dict)
        assert source_dict["arxiv_id"] == "1706.03762"
        assert source_dict["title"] == "Attention Is All You Need"
        assert source_dict["authors"] == ["Vaswani, A."]
        assert source_dict["url"] == "https://arxiv.org/abs/1706.03762"
        assert source_dict["relevance_score"] == 0.95


class TestToolArtefact:
    """Tests for ToolArtefact model."""

    def test_valid_tool_artefact(self):
        """Test creating valid tool artefact."""
        artefact = ToolArtefact(
            tool_name="retrieve_papers",
            tool_call_id="call_123",
            content="Retrieved 3 papers",
            metadata={"count": 3, "source": "opensearch"},
        )
        assert artefact.tool_name == "retrieve_papers"
        assert artefact.tool_call_id == "call_123"
        assert artefact.content == "Retrieved 3 papers"
        assert artefact.metadata["count"] == 3

    def test_default_metadata(self):
        """Test default empty metadata."""
        artefact = ToolArtefact(tool_name="test_tool", tool_call_id="call_456", content="Test content")
        assert artefact.metadata == {}


class TestRoutingDecision:
    """Tests for RoutingDecision model."""

    def test_valid_routing_decisions(self):
        """Test all valid routing options."""
        routes = ["retrieve", "out_of_scope", "generate_answer", "rewrite_query"]

        for route in routes:
            decision = RoutingDecision(route=route, reason=f"Testing {route}")
            assert decision.route == route
            assert decision.reason == f"Testing {route}"

    def test_default_reason(self):
        """Test default empty reason."""
        decision = RoutingDecision(route="retrieve")
        assert decision.reason == ""

    def test_invalid_route(self):
        """Test invalid routing option."""
        with pytest.raises(ValidationError):
            RoutingDecision(route="invalid_route")


class TestGradingResult:
    """Tests for GradingResult model."""

    def test_valid_grading_result(self):
        """Test creating valid grading result."""
        result = GradingResult(
            document_id="doc_123", is_relevant=True, score=0.87, reasoning="Contains relevant information about transformers"
        )
        assert result.document_id == "doc_123"
        assert result.is_relevant is True
        assert result.score == 0.87
        assert "transformers" in result.reasoning

    def test_default_values(self):
        """Test default field values."""
        result = GradingResult(document_id="doc_456", is_relevant=False)
        assert result.score == 0.0
        assert result.reasoning == ""


class TestReasoningStep:
    """Tests for ReasoningStep model."""

    def test_valid_reasoning_step(self):
        """Test creating valid reasoning step."""
        step = ReasoningStep(
            step_name="retrieve",
            description="Retrieved 3 relevant papers from OpenSearch",
            metadata={"num_docs": 3, "retrieval_time_ms": 150},
        )
        assert step.step_name == "retrieve"
        assert step.description == "Retrieved 3 relevant papers from OpenSearch"
        assert step.metadata["num_docs"] == 3
        assert step.metadata["retrieval_time_ms"] == 150

    def test_default_metadata(self):
        """Test default empty metadata."""
        step = ReasoningStep(step_name="generate", description="Generated final answer")
        assert step.metadata == {}
