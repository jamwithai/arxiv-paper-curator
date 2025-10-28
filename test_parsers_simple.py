#!/usr/bin/env python3
"""Simple test to compare Docling parser output on actual PDFs."""

import asyncio
import sys
from pathlib import Path

# Test just Docling first to verify basic functionality
from src.services.pdf_parser.docling import DoclingParser


async def test_docling_only(pdf_path: Path):
    """Test Docling parser and show section extraction."""
    print(f"\n{'='*80}")
    print(f"Testing Docling Parser on: {pdf_path.name}")
    print(f"{'='*80}\n")

    parser = DoclingParser(
        max_pages=30,
        max_file_size_mb=20,
        do_ocr=False,
        do_table_structure=True,
    )

    try:
        result = await parser.parse_pdf(pdf_path)

        if result:
            print(f"✅ SUCCESS!")
            print(f"\nMetrics:")
            print(f"  - Sections extracted: {len(result.sections)}")
            print(f"  - Total text length: {len(result.raw_text):,} characters")
            print(f"  - Parser used: {result.parser_used}")

            print(f"\n📑 Extracted Sections:")
            print(f"{'-'*80}")
            for i, section in enumerate(result.sections, 1):
                print(f"{i}. '{section.title}'")
                print(f"   - Content length: {len(section.content):,} chars")
                print(f"   - First 100 chars: {section.content[:100].strip()}...")
                print()

            # Show sample of raw text
            print(f"\n📄 Raw Text Sample (first 500 chars):")
            print(f"{'-'*80}")
            print(result.raw_text[:500])
            print("...")

            return True
        else:
            print(f"❌ Parser returned None")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_parsers_simple.py <path_to_pdf>")
        print("\nExample:")
        print("  python3 test_parsers_simple.py pdfs/2005.11401v4.pdf")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])

    if not pdf_path.exists():
        print(f"❌ Error: PDF not found: {pdf_path}")
        sys.exit(1)

    success = asyncio.run(test_docling_only(pdf_path))
    sys.exit(0 if success else 1)
