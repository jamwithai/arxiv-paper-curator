import logging
from contextlib import contextmanager
from typing import Any, Dict, Optional

from langfuse import Langfuse
from src.config import Settings

logger = logging.getLogger(__name__)


class LangfuseTracer:
    """Wrapper for Langfuse v3 tracing client with CallbackHandler support."""

    def __init__(self, settings: Settings):
        self.settings = settings.langfuse
        self.client: Optional[Langfuse] = None

        if self.settings.enabled and self.settings.public_key and self.settings.secret_key:
            try:
                # Initialize Langfuse v3 singleton client
                # Configuration moved to client initialization (not handler)
                self.client = Langfuse(
                    public_key=self.settings.public_key,
                    secret_key=self.settings.secret_key,
                    host=self.settings.host,
                    flush_at=self.settings.flush_at,
                    flush_interval=self.settings.flush_interval,
                    debug=self.settings.debug,
                )
                logger.info(f"Langfuse v3 tracing initialized (host: {self.settings.host})")
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse: {e}")
                self.client = None
        else:
            logger.info("Langfuse tracing disabled or missing credentials")

    def get_callback_handler(
        self,
        trace_name: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ):
        """
        Get a CallbackHandler for LangChain/LangGraph integration.

        This is the v3 recommended approach - all LLM calls are automatically traced.

        Args:
            trace_name: Optional name for the trace
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Additional metadata to attach to the trace
            tags: Optional tags for the trace

        Returns:
            CallbackHandler instance if Langfuse is enabled, None otherwise
        """
        if not self.client:
            return None

        try:
            # Import v3 CallbackHandler (new path)
            from langfuse.langchain import CallbackHandler

            # Create handler with trace metadata
            # Note: flush settings are now on the client, not the handler
            handler = CallbackHandler(
                trace_name=trace_name,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
                tags=tags,
            )
            return handler
        except Exception as e:
            logger.error(f"Error creating CallbackHandler: {e}")
            return None

    @contextmanager
    def trace_langgraph_agent(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ):
        """
        Context manager to wrap LangGraph agent execution with a top-level trace span.

        This follows the Langfuse LangGraph cookbook pattern of wrapping the entire
        graph invocation in a span for better observability.

        Usage:
            with tracer.trace_langgraph_agent(name="agentic_rag", ...) as (trace_ctx, handler):
                result = graph.invoke(input, config={"callbacks": [handler]})
                trace_ctx.update(output=result)

        Args:
            name: Name for the trace span (e.g., "agentic_rag_graph")
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Additional metadata to attach
            tags: Optional tags for the trace

        Yields:
            Tuple of (trace_context, callback_handler) for graph execution
        """
        if not self.client:
            # Return no-op context if Langfuse is disabled
            yield (None, None)
            return

        # Create callback handler for LangChain/LangGraph integration
        # The handler will automatically create traces
        handler = self.get_callback_handler(
            trace_name=name,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            tags=tags,
        )

        # In Langfuse v3, the CallbackHandler manages tracing automatically
        # We just need to return the handler and a placeholder trace context
        # The actual trace will be created by the handler
        yield (None, handler)

    def get_trace_id(self, trace=None) -> Optional[str]:
        """
        Get the current trace ID from Langfuse context.

        In Langfuse v3, the CallbackHandler manages traces automatically.
        We can get the current trace ID using get_current_trace_id().

        Args:
            trace: Deprecated, not used in v3

        Returns:
            Trace ID string or None if trace is disabled
        """
        if not self.client:
            return None

        try:
            # In Langfuse v3, use get_current_trace_id()
            trace_id = self.client.get_current_trace_id()
            return trace_id
        except Exception as e:
            logger.error(f"Error getting trace ID: {e}")
            return None

    def submit_feedback(
        self,
        trace_id: str,
        score: float,
        name: str = "user-feedback",
        comment: Optional[str] = None,
    ) -> bool:
        """
        Submit user feedback for a trace (following Langfuse cookbook pattern).

        Args:
            trace_id: Trace ID from get_trace_id()
            score: Feedback score (0-1 or -1 to 1)
            name: Name of the score (default: "user-feedback")
            comment: Optional feedback comment

        Returns:
            True if feedback was submitted successfully, False otherwise
        """
        if not self.client:
            logger.warning("Cannot submit feedback: Langfuse is disabled")
            return False

        try:
            self.client.score(
                trace_id=trace_id,
                name=name,
                value=score,
                comment=comment,
            )
            logger.info(f"Submitted feedback for trace {trace_id}: score={score}")
            return True
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return False

    def flush(self):
        """Flush any pending traces."""
        if self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Error flushing Langfuse: {e}")

    def shutdown(self):
        """Shutdown the Langfuse client."""
        if self.client:
            try:
                self.client.flush()
                self.client.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down Langfuse: {e}")

    @contextmanager
    def start_generation(
        self,
        name: str,
        model: str,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Start a generation span for LLM calls (following Langfuse cookbook pattern).

        This creates a generation observation that tracks:
        - Model name and parameters
        - Input prompt/messages
        - Output completion
        - Token usage
        - Latency

        Usage:
            with tracer.start_generation(name="decision_llm", model="llama3.2", input_data=prompt) as gen:
                response = await llm.generate(...)
                gen.update(output=response, usage_metadata={...})

        Args:
            name: Name for this generation (e.g., "decision_llm", "grading_llm")
            model: Model identifier (e.g., "llama3.2:1b", "gpt-4o")
            input_data: Input to the LLM (prompt or messages)
            metadata: Additional metadata (temperature, max_tokens, etc.)

        Yields:
            Generation context object for updates
        """
        if not self.client:
            # No-op context when disabled
            yield None
            return

        try:
            generation = self.client.generation(
                name=name,
                model=model,
                input=input_data,
                metadata=metadata or {},
            )
            yield generation
        except Exception as e:
            logger.error(f"Error creating generation span: {e}")
            yield None

    @contextmanager
    def trace_rag_request(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Start a top-level span for a RAG request (v3 SDK).

        This is the root observation for a single `/ask` request, under which
        embedding, search, prompt construction, and generation spans are nested.

        Args:
            query: The user's question
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Additional metadata to attach to the root span

        Yields:
            Root span object, or None if Langfuse is disabled
        """
        if not self.client:
            yield None
            return

        span = None
        try:
            span = self.client.start_span(
                name="rag_request",
                input={"query": query},
                metadata={**(metadata or {}), "user_id": user_id, "session_id": session_id},
            )
        except Exception as e:
            logger.error(f"Error creating RAG request trace: {e}")
            span = None

        try:
            yield span
        finally:
            if span:
                span.end()

    def create_span(
        self,
        trace: Optional[Any] = None,
        name: str = "span",
        input_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a child span nested under `trace` (or a root span if `trace` is None).

        Unlike `start_span`, this is not a context manager - call `end_span()`
        explicitly when the operation completes.

        Args:
            trace: Parent span to nest under, or None for a root span
            name: Name for this span
            input_data: Input to this operation
            metadata: Additional metadata

        Returns:
            Span object, or None if Langfuse is disabled or creation failed
        """
        if not self.client:
            return None

        try:
            parent = trace if trace is not None else self.client
            return parent.start_span(name=name, input=input_data, metadata=metadata or {})
        except Exception as e:
            logger.error(f"Error creating span '{name}': {e}")
            return None

    def end_span(
        self,
        span,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        level: Optional[str] = None,
    ):
        """
        Update a span with final output/metadata and end it.

        Args:
            span: Span object from `create_span()`
            output: Operation output
            metadata: Additional metadata to attach
            level: Log level (e.g., "ERROR", "WARNING") for error tracking
        """
        if not span:
            return

        try:
            update_kwargs: Dict[str, Any] = {}
            if output is not None:
                update_kwargs["output"] = output
            if metadata:
                update_kwargs["metadata"] = metadata
            if level:
                update_kwargs["level"] = level

            if update_kwargs:
                span.update(**update_kwargs)
            span.end()
        except Exception as e:
            logger.error(f"Error ending span: {e}")

    @contextmanager
    def start_span(
        self,
        name: str,
        input_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Start a generic span for non-LLM operations (following Langfuse cookbook pattern).

        Use this for operations like:
        - Document retrieval
        - Query rewriting logic
        - Document grading logic
        - Any other processing step

        Usage:
            with tracer.start_span(name="retrieve_papers", input_data={"query": q}) as span:
                docs = retrieve(...)
                span.update(output={"docs_count": len(docs)})

        Args:
            name: Name for this span (e.g., "retrieve_papers", "grade_documents")
            input_data: Input to this operation
            metadata: Additional metadata

        Yields:
            Span context object for updates
        """
        if not self.client:
            # No-op context when disabled
            yield None
            return

        try:
            span = self.client.span(
                name=name,
                input=input_data,
                metadata=metadata or {},
            )
            yield span
        except Exception as e:
            logger.error(f"Error creating span: {e}")
            yield None

    def update_generation(
        self,
        generation,
        output: Any,
        usage_metadata: Optional[Dict[str, Any]] = None,
        completion_start_time: Optional[float] = None,
    ):
        """
        Update a generation span with output and usage metrics.

        Args:
            generation: Generation object from start_generation()
            output: LLM output/response
            usage_metadata: Token usage and timing info
                - prompt_tokens: int
                - completion_tokens: int
                - total_tokens: int
                - latency_ms: float
            completion_start_time: Optional start time for latency calculation
        """
        if not generation:
            return

        try:
            update_data = {"output": output}

            if usage_metadata:
                # Add usage metadata following Langfuse format
                if "prompt_tokens" in usage_metadata:
                    update_data["usage"] = {
                        "input": usage_metadata.get("prompt_tokens", 0),
                        "output": usage_metadata.get("completion_tokens", 0),
                        "total": usage_metadata.get("total_tokens", 0),
                    }

                # Add timing metadata
                if "latency_ms" in usage_metadata:
                    update_data["metadata"] = update_data.get("metadata", {})
                    update_data["metadata"]["latency_ms"] = usage_metadata["latency_ms"]

            generation.update(**update_data)
            generation.end()
        except Exception as e:
            logger.error(f"Error updating generation: {e}")

    def update_span(
        self,
        span,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        level: Optional[str] = None,
        status_message: Optional[str] = None,
    ):
        """
        Update a span with output and metadata.

        Args:
            span: Span object from start_span()
            output: Operation output
            metadata: Additional metadata to attach
            level: Log level (e.g., "ERROR", "WARNING") for error tracking
            status_message: Status or error message
        """
        if not span:
            return

        try:
            update_data = {}
            if output is not None:
                update_data["output"] = output
            if metadata:
                update_data["metadata"] = metadata
            if level:
                update_data["level"] = level
            if status_message:
                update_data["status_message"] = status_message

            if update_data:
                span.update(**update_data)
            span.end()
        except Exception as e:
            logger.error(f"Error updating span: {e}")
