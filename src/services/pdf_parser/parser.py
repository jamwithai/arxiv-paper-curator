import logging
from pathlib import Path
from typing import Optional, Union

from src.exceptions import PDFParsingException, PDFValidationError
from src.schemas.pdf_parser.models import PdfContent

from .deepseek import DeepSeekParser
from .docling import DoclingParser

logger = logging.getLogger(__name__)


class PDFParserService:
    """Main PDF parsing service supporting multiple parsers."""

    def __init__(
        self,
        parser_type: str = "docling",
        max_pages: int = 30,
        max_file_size_mb: int = 20,
        do_ocr: bool = False,
        do_table_structure: bool = True,
        deepseek_model: str = "deepseek-ai/DeepSeek-OCR",
        deepseek_resolution: str = "base",
    ):
        """Initialize PDF parser service with configurable parser type.

        :param parser_type: Parser to use ("docling" or "deepseek")
        :param max_pages: Maximum number of pages to process
        :param max_file_size_mb: Maximum file size in MB
        :param do_ocr: Enable OCR for Docling (default: False)
        :param do_table_structure: Extract table structures for Docling (default: True)
        :param deepseek_model: DeepSeek model name
        :param deepseek_resolution: DeepSeek resolution mode
        """
        self.parser_type = parser_type.lower()
        self.parser: Union[DoclingParser, DeepSeekParser]

        if self.parser_type == "deepseek":
            logger.info("Initializing DeepSeek OCR parser (GPU-accelerated)")
            self.parser = DeepSeekParser(
                max_pages=max_pages,
                max_file_size_mb=max_file_size_mb,
                model_name=deepseek_model,
                resolution=deepseek_resolution,
            )
        elif self.parser_type == "docling":
            logger.info("Initializing Docling parser")
            self.parser = DoclingParser(
                max_pages=max_pages,
                max_file_size_mb=max_file_size_mb,
                do_ocr=do_ocr,
                do_table_structure=do_table_structure,
            )
        else:
            raise ValueError(f"Unknown parser type: {parser_type}. Must be 'docling' or 'deepseek'")

    async def parse_pdf(self, pdf_path: Path) -> Optional[PdfContent]:
        """Parse PDF using the configured parser.

        :param pdf_path: Path to PDF file
        :returns: PdfContent object or None if parsing failed
        """
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise PDFValidationError(f"PDF file not found: {pdf_path}")

        try:
            result = await self.parser.parse_pdf(pdf_path)
            if result:
                logger.info(f"Parsed {pdf_path.name} using {self.parser_type}")
                return result
            else:
                logger.error(f"{self.parser_type} parsing returned no result for {pdf_path.name}")
                raise PDFParsingException(f"{self.parser_type} parsing returned no result for {pdf_path.name}")

        except (PDFValidationError, PDFParsingException):
            raise
        except Exception as e:
            logger.error(f"{self.parser_type} parsing error for {pdf_path.name}: {e}")
            raise PDFParsingException(f"{self.parser_type} parsing error for {pdf_path.name}: {e}")
