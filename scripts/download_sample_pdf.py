"""
Download a sample arXiv PDF for testing parsers.
"""

import requests
from pathlib import Path


def download_arxiv_pdf(arxiv_id: str, output_dir: Path = Path("./test_pdfs")) -> Path:
    """Download a PDF from arXiv.

    :param arxiv_id: arXiv ID (e.g., "2501.12345" or just "2501.12345")
    :param output_dir: Directory to save the PDF
    :returns: Path to downloaded PDF
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean arxiv_id (remove version if present)
    arxiv_id = arxiv_id.split("v")[0]

    # Construct URL
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    # Output file path
    output_path = output_dir / f"{arxiv_id}.pdf"

    if output_path.exists():
        print(f"✅ PDF already exists: {output_path}")
        return output_path

    print(f"📥 Downloading from {pdf_url}...")

    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Downloaded successfully: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")

        return output_path

    except Exception as e:
        print(f"❌ Error downloading PDF: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download a sample arXiv PDF for testing")
    parser.add_argument(
        "--arxiv-id",
        type=str,
        default="2501.10234",  # DeepSeek-OCR paper itself!
        help="arXiv ID to download (default: DeepSeek-OCR paper)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./test_pdfs"),
        help="Output directory for PDFs",
    )

    args = parser.parse_args()

    pdf_path = download_arxiv_pdf(args.arxiv_id, args.output_dir)
    print(f"\n✅ Ready to test!")
    print(f"\nRun the comparison test:")
    print(f"  python tests/test_parser_comparison.py {pdf_path}")
