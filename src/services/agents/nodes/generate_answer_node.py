import logging
import time
from typing import Dict, List

from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from ..context import Context
from ..prompts import GENERATE_ANSWER_PROMPT
from ..state import AgentState
from .utils import get_latest_context, get_latest_query

logger = logging.getLogger(__name__)


async def ainvoke_generate_answer_step(
    state: AgentState,
    runtime: Runtime[Context],
) -> Dict[str, List[AIMessage]]:
    """Generate final answer using retrieved documents.

    This node generates a comprehensive answer to the
    user's question based on the retrieved context using an LLM.

    :param state: Current agent state
    :param runtime: Runtime context
    :returns: Dictionary with messages containing the generated answer
    """
    logger.info("NODE: generate_answer")
    start_time = time.time()

    # Get question and context
    question = get_latest_query(state["messages"])
    context = get_latest_context(state["messages"])

    # Count sources from relevant_sources
    sources_count = len(state.get("relevant_sources", []))

    if not context:
        context = "No relevant documents found."
        logger.warning("No context available for answer generation")

    logger.debug(f"Generating answer for query: {question[:100]}...")
    logger.debug(f"Using context of length: {len(context)} characters")

    # Extract document chunks preview for logging
    chunks_preview = []
    if context:
        context_preview = context[:1000] + "..." if len(context) > 1000 else context
        chunks_preview = [{"text_preview": context_preview, "length": len(context)}]

    # Create span for answer generation
    span = None
    if runtime.context.langfuse_enabled and runtime.context.trace:
        try:
            span = runtime.context.langfuse_tracer.create_span(
                trace=runtime.context.trace,
                name="answer_generation",
                input_data={
                    "query": question,
                    "context_length": len(context),
                    "sources_count": sources_count,
                    "chunks_used": chunks_preview,
                },
                metadata={
                    "node": "generate_answer",
                    "model": runtime.context.model_name,
                    "temperature": runtime.context.temperature,
                },
            )
            logger.debug("Created Langfuse span for answer generation")
        except Exception as e:
            logger.warning(f"Failed to create span for generate_answer node: {e}")

    try:
        # Create answer generation prompt from template
        answer_prompt = GENERATE_ANSWER_PROMPT.format(
            context=context,
            question=question,
        )

        # Get LLM from runtime context
        llm = runtime.context.llm_client.get_langchain_model(
            model=runtime.context.model_name,
            temperature=runtime.context.temperature,
        )

        # Invoke LLM for answer generation
        logger.info("Invoking LLM for answer generation")
        response = await llm.ainvoke(answer_prompt)

        # Extract content from response
        answer = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"Generated answer of length: {len(answer)} characters")

        # Update span with successful result
        if span:
            execution_time = (time.time() - start_time) * 1000
            runtime.context.langfuse_tracer.end_span(
                span,
                output={
                    "answer_length": len(answer),
                    "sources_used": sources_count,
                },
                metadata={
                    "execution_time_ms": execution_time,
                    "context_length": len(context),
                },
            )

    except Exception as e:
        logger.error(f"LLM answer generation failed: {e}, falling back to error message")

        # Fallback to error message if LLM fails
        answer = f"I apologize, but I encountered an error while generating the answer: {str(e)}\n\nPlease try again or rephrase your question."

        # Update span with error
        if span:
            execution_time = (time.time() - start_time) * 1000
            runtime.context.langfuse_tracer.update_span(
                span,
                output={"error": str(e), "fallback": True},
                metadata={"execution_time_ms": execution_time},
                level="ERROR",
            )
            runtime.context.langfuse_tracer.end_span(span)

    return {"messages": [AIMessage(content=answer)]}
