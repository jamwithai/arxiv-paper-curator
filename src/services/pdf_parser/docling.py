import logging
from pathlib import Path
from typing import Optional

import pypdfium2 as pdfium
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from src.exceptions import PDFParsingException, PDFValidationError
from src.schemas.pdf_parser.models import PaperFigure, PaperSection, PaperTable, ParserType, PdfContent

logger = logging.getLogger(__name__)


class DoclingParser:
    """Docling PDF parser for scientific document processing."""

    def __init__(self, max_pages: int, max_file_size_mb: int, do_ocr: bool = False, do_table_structure: bool = True):
        """Initialize DocumentConverter with optimized pipeline options.

        :param max_pages: Maximum number of pages to process
        :param max_file_size_mb: Maximum file size in MB
        :param do_ocr: Enable OCR for scanned PDFs (default: False, very slow)
        :param do_table_structure: Extract table structures (default: True)
        """
        # Configure pipeline options
        pipeline_options = PdfPipelineOptions(
            do_table_structure=do_table_structure,
            do_ocr=do_ocr,  # Usually disabled for speed
        )

        self._converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
        self._warmed_up = False
        self.max_pages = max_pages
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    def _warm_up_models(self):
        """Pre-warm the models with a small dummy document to avoid cold start."""
        if not self._warmed_up:
            # This happens only once per DoclingParser instance
            self._warmed_up = True

    def _validate_pdf(self, pdf_path: Path) -> bool:
        """Comprehensive PDF validation including size and page limits.

        :param pdf_path: Path to PDF file
        :returns: True if PDF appears valid and within limits, False otherwise
        """
        try:
            # Check file exists and is not empty
            if pdf_path.stat().st_size == 0:
                logger.error(f"PDF file is empty: {pdf_path}")
                raise PDFValidationError(f"PDF file is empty: {pdf_path}")

            # Check file size limit
            file_size = pdf_path.stat().st_size
            if file_size > self.max_file_size_bytes:
                logger.warning(
                    f"PDF file size ({file_size / 1024 / 1024:.1f}MB) exceeds limit ({self.max_file_size_bytes / 1024 / 1024:.1f}MB), skipping processing"
                )
                raise PDFValidationError(
                    f"PDF file too large: {file_size / 1024 / 1024:.1f}MB > {self.max_file_size_bytes / 1024 / 1024:.1f}MB"
                )

            # Check if file starts with PDF header
            with open(pdf_path, "rb") as f:
                header = f.read(8)
                if not header.startswith(b"%PDF-"):
                    logger.error(f"File does not have PDF header: {pdf_path}")
                    raise PDFValidationError(f"File does not have PDF header: {pdf_path}")

            # Check page count limit
            pdf_doc = pdfium.PdfDocument(str(pdf_path))
            actual_pages = len(pdf_doc)
            pdf_doc.close()

            if actual_pages > self.max_pages:
                logger.warning(
                    f"PDF has {actual_pages} pages, exceeding limit of {self.max_pages} pages. Skipping processing to avoid performance issues."
                )
                raise PDFValidationError(f"PDF has too many pages: {actual_pages} > {self.max_pages}")

            return True

        except PDFValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating PDF {pdf_path}: {e}")
            raise PDFValidationError(f"Error validating PDF {pdf_path}: {e}")

    async def parse_pdf(self, pdf_path: Path) -> Optional[PdfContent]:
        """Parse PDF using Docling parser.
        Limited to 20 pages to avoid memory issues with large papers.

        :param pdf_path: Path to PDF file
        :returns: PdfContent object or None if parsing failed
        """
        try:
            # Validate PDF first (includes size and page limits)
            self._validate_pdf(pdf_path)

            # Warm up models on first use
            self._warm_up_models()

            # Convert PDF using the modern API
            # Limit processing to avoid memory issues with large papers
            result = self._converter.convert(str(pdf_path), max_num_pages=self.max_pages, max_file_size=self.max_file_size_bytes)

            # Extract structured content
            doc = result.document

            # Extract sections from document structure
            sections = []
            current_section = {"title": "Content", "content": ""}

            for element in doc.texts:
                if hasattr(element, "label") and element.label in ["title", "section_header"]:
                    # Save previous section if it has content
                    if current_section["content"].strip():
                        sections.append(PaperSection(title=current_section["title"], content=current_section["content"].strip()))
                    # Start new section
                    current_section = {"title": element.text.strip(), "content": ""}
                else:
                    # Add content to current section
                    if hasattr(element, "text") and element.text:
                        current_section["content"] += element.text + "\n"

            # Add final section
            if current_section["content"].strip():
                sections.append(PaperSection(title=current_section["title"], content=current_section["content"].strip()))

            # Focus on what arXiv API doesn't provide: structured full text content only
            return PdfContent(
                sections=sections,
                figures=[],  # Removed: basic metadata not useful
                tables=[],  # Removed: basic metadata not useful
                raw_text=doc.export_to_text(),
                references=[],
                parser_used=ParserType.DOCLING,
                metadata={"source": "docling", "note": "Content extracted from PDF, metadata comes from arXiv API"},
            )

        except PDFValidationError as e:
            # Handle size/page limit validation errors gracefully by returning None
            error_msg = str(e).lower()
            if "too large" in error_msg or "too many pages" in error_msg:
                logger.info(f"Skipping PDF processing due to size/page limits: {e}")
                return None
            else:
                # Re-raise other validation errors (corrupted files, etc.)
                raise
        except Exception as e:
            logger.error(f"Failed to parse PDF with Docling: {e}")
            logger.error(f"PDF path: {pdf_path}")
            logger.error(f"PDF size: {pdf_path.stat().st_size} bytes")
            logger.error(f"Error type: {type(e).__name__}")

            # Add specific handling for common issues
            error_msg = str(e).lower()

            # Note: Page and size limit checks are now handled in _validate_pdf method

            if "not valid" in error_msg:
                logger.error("PDF appears to be corrupted or not a valid PDF file")
                raise PDFParsingException(f"PDF appears to be corrupted or invalid: {pdf_path}")
            elif "timeout" in error_msg:
                logger.error("PDF processing timed out - file may be too complex")
                raise PDFParsingException(f"PDF processing timed out: {pdf_path}")
            elif "memory" in error_msg or "ram" in error_msg:
                logger.error("Out of memory - PDF may be too large or complex")
                raise PDFParsingException(f"Out of memory processing PDF: {pdf_path}")
            elif "max_num_pages" in error_msg or "page" in error_msg:
                logger.error(f"PDF processing issue likely related to page limits (current limit: {self.max_pages} pages)")
                raise PDFParsingException(
                    f"PDF processing failed, possibly due to page limit ({self.max_pages} pages). Error: {e}"
                )
            else:
                raise PDFParsingException(f"Failed to parse PDF with Docling: {e}")
