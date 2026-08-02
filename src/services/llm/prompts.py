import json
import re
from pathlib import Path
from typing import Any, Dict, List

from pydantic import ValidationError
from src.domain_profiles import get_domain_profile
from src.schemas.ollama import RAGResponse


class RAGPromptBuilder:
    """Builder class for creating RAG prompts, scoped to a corpus domain."""

    def __init__(self, domain: str = "ai"):
        """Initialize the prompt builder.

        :param domain: Corpus domain ("ai", "education", "accounting") - controls
            how the system prompt and citations are framed (see Stage 2 plan).
        """
        self.domain_profile = get_domain_profile(domain)
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load and template the system prompt for the active domain.

        Returns:
            System prompt string
        """
        prompt_file = self.prompts_dir / "rag_system.txt"
        if not prompt_file.exists():
            # Fallback to default template if file doesn't exist
            template = (
                "You are an AI assistant specialized in answering questions about "
                "{domain_label}. Base your answer STRICTLY on the provided document excerpts."
            )
        else:
            template = prompt_file.read_text().strip()

        return template.format(
            domain_label=self.domain_profile.label,
            citation_style=self.domain_profile.citation_style,
        )

    def create_rag_prompt(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """Create a RAG prompt with query and retrieved chunks.

        Args:
            query: User's question
            chunks: List of retrieved chunks with metadata from OpenSearch

        Returns:
            Formatted prompt string
        """
        prompt = f"{self.system_prompt}\n\n"
        prompt += "### Context from Documents:\n\n"

        for i, chunk in enumerate(chunks, 1):
            # arXiv chunks use "chunk_text"; bilingual domain chunks use
            # "chunk_text_vi"/"chunk_text_en" (see LEGAL_DOCS_CHUNKS_MAPPING).
            chunk_text = (
                chunk.get("chunk_text")
                or chunk.get("content")
                or chunk.get("chunk_text_vi")
                or chunk.get("chunk_text_en")
                or ""
            )
            # arXiv chunks cite by arxiv_id; bilingual domain chunks cite by doc_number/doc_id.
            citation_id = chunk.get("arxiv_id") or chunk.get("doc_number") or chunk.get("doc_id", "")

            prompt += f"[{i}. {citation_id}]\n"
            prompt += f"{chunk_text}\n\n"

        prompt += f"### Question:\n{query}\n\n"
        prompt += (
            f"### Answer:\nProvide a natural, conversational response (not JSON) and cite sources using "
            f"{self.domain_profile.citation_style}.\n\n"
        )

        return prompt

    def create_structured_prompt(self, query: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a prompt for Ollama with structured output format.

        Args:
            query: User's question
            chunks: List of retrieved chunks

        Returns:
            Dictionary with prompt and format schema for Ollama
        """
        prompt_text = self.create_rag_prompt(query, chunks)

        # Return prompt with Pydantic model schema for structured output
        return {
            "prompt": prompt_text,
            "format": RAGResponse.model_json_schema(),
        }


class ResponseParser:
    """Parser for LLM responses."""

    @staticmethod
    def parse_structured_response(response: str) -> Dict[str, Any]:
        """Parse a structured response from Ollama.

        Args:
            response: Raw LLM response string

        Returns:
            Dictionary with parsed response
        """
        try:
            # Try to parse as JSON and validate with Pydantic
            parsed_json = json.loads(response)
            validated_response = RAGResponse(**parsed_json)
            return validated_response.model_dump()
        except (json.JSONDecodeError, ValidationError):
            # Fallback: try to extract JSON from the response
            return ResponseParser._extract_json_fallback(response)

    @staticmethod
    def _extract_json_fallback(response: str) -> Dict[str, Any]:
        """Extract JSON from response text as fallback.

        Args:
            response: Raw response text

        Returns:
            Dictionary with extracted content or fallback
        """
        # Try to find JSON in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                # Validate with Pydantic, using defaults for missing fields
                validated = RAGResponse(**parsed)
                return validated.model_dump()
            except (json.JSONDecodeError, ValidationError):
                pass

        # Final fallback: return response as plain text
        return {
            "answer": response,
            "sources": [],
            "confidence": "low",
            "citations": [],
        }
