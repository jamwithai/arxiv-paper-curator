import logging
from typing import Dict, List

from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from ..context import Context
from ..domain_config import get_domain_profile
from ..state import AgentState
from .utils import get_latest_query

logger = logging.getLogger(__name__)


async def ainvoke_out_of_scope_step(
    state: AgentState,
    runtime: Runtime[Context],
) -> Dict[str, List[AIMessage]]:
    """Handle out-of-scope queries with a helpful message.

    This node responds to queries that are outside the domain of
    CS/AI/ML research papers with a polite, informative message.

    :param state: Current agent state
    :param runtime: Runtime context (not used in this node)
    :returns: Dictionary with messages containing the out-of-scope response
    """
    logger.info("NODE: out_of_scope")

    question = get_latest_query(state["messages"])
    domain_profile = get_domain_profile(runtime.context.domain)

    # Generate helpful response message, scoped to the active domain
    response_text = (
        f"I apologize, but I can only help with questions about {domain_profile.label}.\n\n"
        f"Your question: '{question}'\n\n"
        "This appears to be outside my domain of expertise. For questions like this, you might want to try "
        f"{domain_profile.out_of_scope_suggestion}.\n\n"
        "If you have a question within this corpus's domain, I'd be happy to help!"
    )

    logger.info("Responding with out-of-scope message")

    return {"messages": [AIMessage(content=response_text)]}
