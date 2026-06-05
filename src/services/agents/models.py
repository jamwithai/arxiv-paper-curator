from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class GuardrailScoring(BaseModel):
    """Scoring result of a user query for guardrail validation.

    :param score: Relevance score between 0 and 100
    :param reason: Brief explanation for the score
    """

    score: int = Field(ge=0, le=100, description="Relevance score between 0 and 100")
    reason: str = Field(description="Brief reason for the score")


class GradeDocuments(BaseModel):
    """Binary score for document relevance check.

    :param binary_score: Relevance score: 'yes' or 'no'
    :param reasoning: Explanation for the relevance decision
    """

    binary_score: Literal["yes", "no"] = Field(description="Document relevance: 'yes' or 'no'")
    reasoning: str = Field(default="", description="Explanation for the decision")


class SourceItem(BaseModel):
    """Source item from retrieved documents.

    :param arxiv_id: arXiv paper ID
    :param title: Paper title
    :param authors: List of authors
    :param url: Link to the paper
    :param relevance_score: Relevance score from retrieval
    """

    arxiv_id: str = Field(description="arXiv paper ID")
    title: str = Field(description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    url: str = Field(description="Link to paper")
    relevance_score: float = Field(default=0.0, description="Relevance score from search")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "url": self.url,
            "relevance_score": self.relevance_score,
        }


class ToolArtefact(BaseModel):
    """Artifact returned by tool calls with metadata.

    :param tool_name: Name of the tool that generated this artifact
    :param tool_call_id: Unique ID of the tool call
    :param content: The actual content/result from the tool
    :param metadata: Additional metadata about the tool execution
    """

    tool_name: str = Field(description="Name of the tool")
    tool_call_id: str = Field(description="Unique tool call ID")
    content: Any = Field(description="Tool result content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RoutingDecision(BaseModel):
    """Routing decision for graph navigation.

    :param route: The next node to route to
    :param reason: Explanation for the routing decision
    """

    route: Literal["retrieve", "out_of_scope", "generate_answer", "rewrite_query"] = Field(description="Next node to route to")
    reason: str = Field(default="", description="Reason for routing decision")


class GradingResult(BaseModel):
    """Result of document grading with details.

    :param document_id: Identifier for the graded document
    :param is_relevant: Whether document is relevant
    :param score: Relevance score
    :param reasoning: Explanation for the grade
    """

    document_id: str = Field(description="Document identifier")
    is_relevant: bool = Field(description="Relevance flag")
    score: float = Field(default=0.0, description="Relevance score")
    reasoning: str = Field(default="", description="Grading reasoning")


class ReasoningStep(BaseModel):
    """A reasoning step in the agent workflow.

    :param step_name: Name of the step/node
    :param description: Human-readable description
    :param metadata: Additional step metadata
    """

    step_name: str = Field(description="Name of the reasoning step")
    description: str = Field(description="Human-readable description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Step metadata")
