class RepositoryException(Exception):
    """Base exception for repository-related errors."""


class PaperNotFound(RepositoryException):
    """Exception raised when paper data is not found."""


class PaperNotSaved(RepositoryException):
    """Exception raised when paper data is not saved."""


class ParsingException(Exception):
    """Base exception for parsing-related errors."""


# Week 2: PDF parsing exceptions (implemented)
class PDFParsingException(ParsingException):
    """Base exception for PDF parsing-related errors."""


class PDFValidationError(PDFParsingException):
    """Exception raised when PDF file validation fails."""


class PDFDownloadException(Exception):
    """Base exception for PDF download-related errors."""


class PDFDownloadTimeoutError(PDFDownloadException):
    """Exception raised when PDF download times out."""


class PDFCacheException(Exception):
    """Exception raised for PDF cache-related errors."""


# Week 3+: OpenSearch exceptions (placeholders for Week 1)
class OpenSearchException(Exception):
    """Base exception for OpenSearch-related errors."""


# Week 2+: ArXiv API exceptions
class ArxivAPIException(Exception):
    """Base exception for arXiv API-related errors."""


class ArxivAPITimeoutError(ArxivAPIException):
    """Exception raised when arXiv API request times out."""


class ArxivAPIRateLimitError(ArxivAPIException):
    """Exception raised when arXiv API rate limit is exceeded."""


class ArxivParseError(ArxivAPIException):
    """Exception raised when arXiv API response parsing fails."""


# Week 2+: Metadata fetching exceptions
class MetadataFetchingException(Exception):
    """Base exception for metadata fetching pipeline errors."""


class PipelineException(MetadataFetchingException):
    """Exception raised during pipeline execution."""


class LLMException(Exception):
    """Base exception for LLM-related errors."""


class OllamaException(LLMException):
    """Exception raised for Ollama service errors."""


class OllamaConnectionError(OllamaException):
    """Exception raised when cannot connect to Ollama service."""


class OllamaTimeoutError(OllamaException):
    """Exception raised when Ollama service times out."""


class MiniMaxException(LLMException):
    """Exception raised for MiniMax API errors."""


class MiniMaxConnectionError(MiniMaxException):
    """Exception raised when cannot connect to MiniMax API."""


class MiniMaxTimeoutError(MiniMaxException):
    """Exception raised when MiniMax API times out."""


# General application exceptions
class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
