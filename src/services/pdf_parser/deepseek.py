import logging
import re
from pathlib import Path
from typing import Optional

import pypdfium2 as pdfium
import torch
from transformers import AutoModel, AutoTokenizer
from src.exceptions import PDFParsingException, PDFValidationError
from src.schemas.pdf_parser.models import PaperSection, ParserType, PdfContent

logger = logging.getLogger(__name__)


class DeepSeekParser:
    """DeepSeek OCR parser for scientific document processing.

    Uses DeepSeek-OCR vision model to extract text and structure from PDFs.
    Significantly faster than Docling when GPU is available.
    """

    def __init__(
        self,
        max_pages: int,
        max_file_size_mb: int,
        model_name: str = "deepseek-ai/DeepSeek-OCR",
        resolution: str = "base",
    ):
        """Initialize DeepSeek OCR parser.

        :param max_pages: Maximum number of pages to process
        :param max_file_size_mb: Maximum file size in MB
        :param model_name: DeepSeek model identifier
        :param resolution: Resolution mode (tiny|small|base|large)
        """
        self.max_pages = max_pages
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.model_name = model_name

        # Resolution to size mapping (from official docs)
        self.resolution_config = {
            "tiny": {"base_size": 512, "image_size": 512},
            "small": {"base_size": 640, "image_size": 640},
            "base": {"base_size": 1024, "image_size": 640},
            "large": {"base_size": 1280, "image_size": 640},
        }

        if resolution not in self.resolution_config:
            raise ValueError(f"Invalid resolution: {resolution}. Must be one of {list(self.resolution_config.keys())}")

        self.resolution = resolution
        self._model = None
        self._tokenizer = None

    def _lazy_load_model(self):
        """Lazy load the DeepSeek model and tokenizer (matches official docs exactly)."""
        if self._model is None:
            logger.info(f"Loading DeepSeek OCR model: {self.model_name}")

            # Official transformers usage from docs
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )

            self._model = AutoModel.from_pretrained(
                self.model_name,
                _attn_implementation='flash_attention_2',
                trust_remote_code=True
            )

            # Move to GPU (as per docs: model.eval().cuda().to(torch.bfloat16))
            if torch.cuda.is_available():
                self._model = self._model.eval().cuda().to(torch.bfloat16)
                logger.info(f"DeepSeek model loaded on GPU: {torch.cuda.get_device_name(0)}")
            else:
                logger.warning("GPU not available, using CPU (will be VERY slow)")
                self._model = self._model.eval().to(torch.bfloat16)

    def _validate_pdf(self, pdf_path: Path) -> bool:
        """Comprehensive PDF validation including size and page limits.

        :param pdf_path: Path to PDF file
        :returns: True if PDF appears valid and within limits
        :raises: PDFValidationError if validation fails
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
                    f"PDF file size ({file_size / 1024 / 1024:.1f}MB) exceeds limit ({self.max_file_size_bytes / 1024 / 1024:.1f}MB)"
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
                    f"PDF has {actual_pages} pages, exceeding limit of {self.max_pages} pages"
                )
                raise PDFValidationError(f"PDF has too many pages: {actual_pages} > {self.max_pages}")

            return True

        except PDFValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating PDF {pdf_path}: {e}")
            raise PDFValidationError(f"Error validating PDF {pdf_path}: {e}")

    def _extract_pages_as_images(self, pdf_path: Path, output_dir: Path) -> list[Path]:
        """Convert PDF pages to image files (required for DeepSeek API).

        :param pdf_path: Path to PDF file
        :param output_dir: Directory to save page images
        :returns: List of paths to saved image files
        """
        image_paths = []
        pdf_doc = pdfium.PdfDocument(str(pdf_path))

        try:
            num_pages = min(len(pdf_doc), self.max_pages)
            logger.info(f"Converting {num_pages} pages to images")

            # Create temp directory for page images
            output_dir.mkdir(parents=True, exist_ok=True)

            for page_num in range(num_pages):
                page = pdf_doc[page_num]
                pil_image = page.render(scale=2.0).to_pil()

                # Save as image file (DeepSeek API expects file paths)
                image_path = output_dir / f"page_{page_num:04d}.png"
                pil_image.save(image_path)
                image_paths.append(image_path)

        finally:
            pdf_doc.close()

        return image_paths

    def _extract_text_from_image_file(self, image_path: Path) -> str:
        """Extract text from an image file using DeepSeek OCR (matches official API).

        :param image_path: Path to image file
        :returns: Extracted markdown text
        """
        config = self.resolution_config[self.resolution]

        # Official prompt from docs for document conversion
        prompt = "<image>\n<|grounding|>Convert the document to markdown."

        try:
            # Official API usage from transformers docs
            result = self._model.infer(
                self._tokenizer,
                prompt=prompt,
                image_file=str(image_path),  # API expects file path string
                base_size=config["base_size"],
                image_size=config["image_size"],
                crop_mode=True,
                save_results=False,  # Don't save intermediate files
            )

            logger.debug(f"Extracted text from {image_path.name}")
            return result

        except Exception as e:
            logger.error(f"Error extracting text from {image_path.name}: {e}")
            return ""

    def _parse_markdown_to_sections(self, markdown_text: str) -> list[PaperSection]:
        """Parse markdown text into paper sections.

        Extracts sections based on markdown headers (# and ##).

        :param markdown_text: Markdown formatted text
        :returns: List of PaperSection objects
        """
        sections = []

        # Split by headers (# or ##)
        # Match lines starting with # or ##
        lines = markdown_text.split('\n')
        current_section = {"title": "Content", "content": ""}

        for line in lines:
            # Check if line is a header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(
                        PaperSection(
                            title=current_section["title"],
                            content=current_section["content"].strip(),
                            level=1
                        )
                    )

                # Start new section
                header_level = len(header_match.group(1))
                section_title = header_match.group(2).strip()
                current_section = {
                    "title": section_title,
                    "content": "",
                    "level": header_level
                }
            else:
                # Add content to current section
                if line.strip():
                    current_section["content"] += line + "\n"

        # Add final section
        if current_section["content"].strip():
            sections.append(
                PaperSection(
                    title=current_section["title"],
                    content=current_section["content"].strip(),
                    level=current_section.get("level", 1)
                )
            )

        return sections

    async def parse_pdf(self, pdf_path: Path) -> Optional[PdfContent]:
        """Parse PDF using DeepSeek OCR.

        :param pdf_path: Path to PDF file
        :returns: PdfContent object or None if parsing failed
        """
        import tempfile
        import shutil

        temp_dir = None
        try:
            # Validate PDF first
            self._validate_pdf(pdf_path)

            # Lazy load model
            self._lazy_load_model()

            # Create temporary directory for page images
            temp_dir = Path(tempfile.mkdtemp(prefix="deepseek_ocr_"))

            # Convert PDF pages to image files
            logger.info(f"Processing PDF with DeepSeek OCR: {pdf_path.name}")
            image_paths = self._extract_pages_as_images(pdf_path, temp_dir)

            if not image_paths:
                logger.error(f"No images extracted from PDF: {pdf_path}")
                raise PDFParsingException(f"No images extracted from PDF: {pdf_path}")

            # Extract text from each page image
            all_text = []
            for image_path in image_paths:
                page_text = self._extract_text_from_image_file(image_path)
                all_text.append(page_text)

            # Combine all pages
            full_markdown = "\n\n".join(all_text)

            # Parse markdown into sections
            sections = self._parse_markdown_to_sections(full_markdown)

            logger.info(f"Successfully parsed {pdf_path.name} with DeepSeek OCR - {len(sections)} sections found")

            return PdfContent(
                sections=sections,
                figures=[],  # Keep consistent with Docling
                tables=[],  # Keep consistent with Docling
                raw_text=full_markdown,
                references=[],
                parser_used=ParserType.DEEPSEEK,
                metadata={
                    "source": "deepseek-ocr",
                    "model": self.model_name,
                    "resolution": self.resolution,
                    "pages_processed": len(image_paths),
                },
            )

        except PDFValidationError as e:
            # Handle size/page limit validation errors gracefully
            error_msg = str(e).lower()
            if "too large" in error_msg or "too many pages" in error_msg:
                logger.info(f"Skipping PDF processing due to size/page limits: {e}")
                return None
            else:
                raise

        except Exception as e:
            logger.error(f"Failed to parse PDF with DeepSeek OCR: {e}")
            logger.error(f"PDF path: {pdf_path}")
            logger.error(f"Error type: {type(e).__name__}")
            raise PDFParsingException(f"Failed to parse PDF with DeepSeek OCR: {e}")

        finally:
            # Cleanup temporary directory
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")
