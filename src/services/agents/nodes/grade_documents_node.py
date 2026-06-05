import logging
import time
from typing import Dict

from langgraph.runtime import Runtime

from ..context import Context
from ..models import GradeDocuments, GradingResult
from ..prompts import GRADE_DOCUMENTS_PROMPT
from ..state import AgentState
from .utils import get_latest_context, get_latest_query

logger = logging.getLogger(__name__)


async def ainvoke_grade_documents_step(
    state: AgentState,
    runtime: Runtime[Context],
) -> Dict[str, str | list]:
    """Grade retrieved documents for relevance using LLM.

    This function uses an LLM to evaluate whether the retrieved documents
    are relevant to the user's query and decides whether to generate an
    answer or rewrite the query for better results.

    :param state: Current agent state
    :param runtime: Runtime context
    :returns: Dictionary with routing_decision and grading_results
    """
    logger.info("NODE: grade_documents")
    start_time = time.time()

    # Get query and context
    question = get_latest_query(state["messages"])
    context = get_latest_context(state["messages"])

    # Extract document chunks from context for logging
    chunks_preview = []
    if context:
        # Context is a string containing all documents concatenated
        # Let's show a preview of what was retrieved
        context_preview = context[:500] + "..." if len(context) > 500 else context
        chunks_preview = [{"text_preview": context_preview, "length": len(context)}]

    # Create span for document grading
    span = None
    if runtime.context.langfuse_enabled and runtime.context.trace:
        try:
            span = runtime.context.langfuse_tracer.create_span(
                trace=runtime.context.trace,
                name="document_grading",
                input_data={
                    "query": question,
                    "context_length": len(context) if context else 0,
                    "has_context": context is not None,
                    "chunks_received": chunks_preview,
                },
                metadata={
                    "node": "grade_documents",
                    "model": runtime.context.model_name,
                },
            )
            logger.debug("Created Langfuse span for document grading")
        except Exception as e:
            logger.warning(f"Failed to create span for grade_documents node: {e}")

    if not context:
        logger.warning("No context found, routing to rewrite_query")

        # Update span with no context result
        if span:
            execution_time = (time.time() - start_time) * 1000
            runtime.context.langfuse_tracer.end_span(
                span,
                output={"routing_decision": "rewrite_query", "reason": "no_context"},
                metadata={"execution_time_ms": execution_time},
            )

        return {"routing_decision": "rewrite_query", "grading_results": []}

    logger.debug(f"Grading context of length {len(context)} characters")

    # Use LLM to grade document relevance
    try:
        # Create grading prompt from template
        grading_prompt = GRADE_DOCUMENTS_PROMPT.format(
            context=context,
            question=question,
        )

        # Get LLM from runtime context
        llm = runtime.context.llm_client.get_langchain_model(
            model=runtime.context.model_name,
            temperature=0.0,
        )

        # Create structured output LLM for grading
        structured_llm = llm.with_structured_output(GradeDocuments)

        # Invoke LLM grading
        logger.info("Invoking LLM for document grading")
        grading_response = await structured_llm.ainvoke(grading_prompt)

        is_relevant = grading_response.binary_score == "yes"
        score = 1.0 if is_relevant else 0.0

        logger.info(f"LLM grading: score={grading_response.binary_score}, reasoning={grading_response.reasoning}")

        # Create grading result record
        grading_result = GradingResult(
            document_id="retrieved_docs",
            is_relevant=is_relevant,
            score=score,
            reasoning=grading_response.reasoning,
        )

    except Exception as e:
        logger.error(f"LLM grading failed: {e}, falling back to heuristic")
        # Fallback to simple heuristic if LLM fails
        is_relevant = len(context.strip()) > 50
        grading_result = GradingResult(
            document_id="retrieved_docs",
            is_relevant=is_relevant,
            score=1.0 if is_relevant else 0.0,
            reasoning=f"Fallback heuristic (LLM failed): {'sufficient content' if is_relevant else 'insufficient content'}",
        )

    # Determine routing
    route = "generate_answer" if is_relevant else "rewrite_query"

    logger.info(f"Grading result: {'relevant' if is_relevant else 'not relevant'}, routing to: {route}")

    # Update span with grading result
    if span:
        execution_time = (time.time() - start_time) * 1000
        runtime.context.langfuse_tracer.end_span(
            span,
            output={
                "routing_decision": route,
                "is_relevant": is_relevant,
                "score": score,
                "reasoning": grading_result.reasoning,
            },
            metadata={
                "execution_time_ms": execution_time,
                "context_length": len(context),
            },
        )

    return {
        "routing_decision": route,
        "grading_results": [grading_result],
    }
