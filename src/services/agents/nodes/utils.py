import logging
from typing import Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from ..models import ReasoningStep, SourceItem, ToolArtefact

logger = logging.getLogger(__name__)


def extract_sources_from_tool_messages(messages: List) -> List[SourceItem]:
    """Extract sources from the retriever tool's artifact.

    `retrieve_papers` (see `..tools.create_retriever_tool`) is a
    `response_format="content_and_artifact"` tool: `msg.content` is the
    LLM-facing text, and `msg.artifact` carries the retrieved `Document`
    objects with structured metadata (arxiv_id, title, authors, url, score) -
    that's what we build `SourceItem`s from, rather than parsing `msg.content`.

    :param messages: List of messages from graph state
    :returns: List of SourceItem objects
    """
    sources = []

    for msg in messages:
        if isinstance(msg, ToolMessage) and getattr(msg, "name", None) == "retrieve_papers":
            for doc in getattr(msg, "artifact", None) or []:
                metadata = doc.metadata
                sources.append(
                    SourceItem(
                        arxiv_id=metadata.get("arxiv_id", ""),
                        title=metadata.get("title", ""),
                        authors=[a.strip() for a in metadata.get("authors", "").split(",") if a.strip()],
                        url=metadata.get("source", ""),
                        relevance_score=metadata.get("score", 0.0),
                    )
                )

    return sources


def extract_tool_artefacts(messages: List) -> List[ToolArtefact]:
    """Extract tool artifacts from messages.

    :param messages: List of messages from graph state
    :returns: List of ToolArtefact objects
    """
    artefacts = []

    for msg in messages:
        if isinstance(msg, ToolMessage):
            artefact = ToolArtefact(
                tool_name=getattr(msg, "name", "unknown"),
                tool_call_id=getattr(msg, "tool_call_id", ""),
                content=msg.content,
                metadata={},
            )
            artefacts.append(artefact)

    return artefacts


def create_reasoning_step(
    step_name: str,
    description: str,
    metadata: Optional[Dict] = None,
) -> ReasoningStep:
    """Create a reasoning step record.

    :param step_name: Name of the step/node
    :param description: Human-readable description
    :param metadata: Additional metadata
    :returns: ReasoningStep object
    """
    return ReasoningStep(
        step_name=step_name,
        description=description,
        metadata=metadata or {},
    )


def filter_messages(messages: List) -> List[AIMessage | HumanMessage]:
    """Filter messages to include only HumanMessage and AIMessage types.

    Excludes tool messages and other internal message types.

    :param messages: List of messages to filter
    :returns: Filtered list of messages
    """
    return [msg for msg in messages if isinstance(msg, (HumanMessage, AIMessage))]


def get_latest_query(messages: List) -> str:
    """Get the latest user query from messages.

    :param messages: List of messages
    :returns: Latest query text
    :raises ValueError: If no user query found
    """
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content

    raise ValueError("No user query found in messages")


def get_latest_context(messages: List) -> str:
    """Get the latest context from tool messages.

    :param messages: List of messages
    :returns: Latest context text or empty string
    """
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            return msg.content if hasattr(msg, "content") else ""

    return ""
