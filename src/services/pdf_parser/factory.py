from functools import lru_cache

from src.config import get_settings

from .parser import PDFParserService


@lru_cache(maxsize=1)
def make_pdf_parser_service() -> PDFParserService:
    """Create cached PDF parser service with configured parser type."""
    settings = get_settings()
    return PDFParserService(
        parser_type=settings.pdf_parser.parser_type,
        max_pages=settings.pdf_parser.max_pages,
        max_file_size_mb=settings.pdf_parser.max_file_size_mb,
        do_ocr=settings.pdf_parser.do_ocr,
        do_table_structure=settings.pdf_parser.do_table_structure,
        deepseek_model=settings.pdf_parser.deepseek_model,
        deepseek_resolution=settings.pdf_parser.deepseek_resolution,
    )
