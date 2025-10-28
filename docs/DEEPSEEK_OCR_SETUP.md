# DeepSeek OCR Integration Guide

This guide explains how to use DeepSeek OCR as an alternative to Docling for faster PDF processing.

## Overview

The arXiv Paper Curator now supports two PDF parsers:

| Parser | Speed | Hardware | Best For |
|--------|-------|----------|----------|
| **Docling** | Slower | CPU | No GPU available, high accuracy needed |
| **DeepSeek OCR** | ~2500 tokens/s | **GPU Required** | Fast processing, GPU available |

DeepSeek OCR uses a vision-based approach to convert PDF pages to markdown, achieving 97% OCR precision with significantly faster processing when GPU is available.

## Requirements

### Hardware
- **NVIDIA GPU** (A100, H100, or similar recommended)
- **CUDA 11.8+** installed
- Sufficient GPU memory (varies by model resolution)

### Software
- Python 3.12+
- PyTorch 2.6.0+
- Transformers 4.50.0+
- flash-attention-2

## Installation

### 1. Install Dependencies

The base dependencies are already included in `pyproject.toml`. Install them:

```bash
uv sync
```

### 2. Install flash-attention-2 (GPU-specific)

**Important:** flash-attention-2 requires compilation and must be installed separately:

```bash
pip install flash-attn --no-build-isolation
```

This may take several minutes to compile. Ensure you have:
- CUDA toolkit installed
- C++ compiler available
- Sufficient disk space for compilation

### 3. Verify GPU Access

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

## Configuration

### Environment Variables

Update your `.env` file with the following settings:

```bash
# Switch to DeepSeek parser
PDF_PARSER__PARSER_TYPE=deepseek

# DeepSeek-specific settings
PDF_PARSER__DEEPSEEK_MODEL=deepseek-ai/DeepSeek-OCR
PDF_PARSER__DEEPSEEK_RESOLUTION=base

# Common settings (apply to both parsers)
PDF_PARSER__MAX_PAGES=30
PDF_PARSER__MAX_FILE_SIZE_MB=20
```

### Resolution Modes

Choose a resolution mode based on your GPU memory and accuracy requirements:

| Mode | Image Size | Tokens | Memory | Use Case |
|------|------------|--------|--------|----------|
| `tiny` | 512×512 | 64 | Low | Fast preview, low memory |
| `small` | 640×640 | 100 | Medium-Low | Balanced speed/accuracy |
| `base` | 1024×1024 | 256 | Medium | **Recommended default** |
| `large` | 1280×1280 | 400 | High | Maximum accuracy |

**Recommendation:** Start with `base` and adjust based on:
- GPU memory errors → use `small` or `tiny`
- Need higher accuracy → use `large`

## Usage

### Switching Between Parsers

You can easily switch between Docling and DeepSeek by changing the `PDF_PARSER__PARSER_TYPE` environment variable:

**Use DeepSeek (GPU-accelerated):**
```bash
PDF_PARSER__PARSER_TYPE=deepseek
```

**Use Docling (CPU-based):**
```bash
PDF_PARSER__PARSER_TYPE=docling
```

No code changes required - the parser is automatically selected at runtime!

### First-Time Model Download

On first use, DeepSeek will download the model (~several GB):
- Model is cached in `~/.cache/huggingface/`
- Download happens automatically
- Subsequent runs use cached model

### Performance Expectations

**DeepSeek OCR (GPU):**
- First page: ~5-10 seconds (model loading)
- Subsequent pages: ~0.4 seconds per page (2500 tokens/s)
- 30-page paper: ~15 seconds total

**Docling (CPU):**
- Per page: ~2-5 seconds
- 30-page paper: ~60-150 seconds total

**Speed improvement: ~4-10x faster with GPU**

## Section Extraction

Both parsers extract sections similarly, but use different approaches:

### DeepSeek Approach
1. Converts PDF pages to images
2. Runs vision model to extract markdown
3. Parses markdown headers (`#`, `##`) to create sections
4. Returns structured `PaperSection` objects

**Markdown Output Example:**
```markdown
# Introduction
Recent advances in machine learning...

## Background
Previous work has shown...

# Methods
Our approach consists of...
```

### Docling Approach
1. Parses PDF document structure
2. Identifies elements labeled as `title` or `section_header`
3. Groups content under headers
4. Returns structured `PaperSection` objects

**Both produce the same output format:**
```python
PdfContent(
    sections=[
        PaperSection(title="Introduction", content="...", level=1),
        PaperSection(title="Methods", content="...", level=1),
    ],
    raw_text="...",
    parser_used=ParserType.DEEPSEEK,
    metadata={...}
)
```

## Troubleshooting

### "CUDA not available"
**Problem:** GPU not detected
**Solution:**
```bash
# Check CUDA installation
nvidia-smi

# Verify PyTorch sees GPU
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### "Out of memory" errors
**Problem:** GPU memory insufficient
**Solutions:**
1. Use smaller resolution: `PDF_PARSER__DEEPSEEK_RESOLUTION=small`
2. Reduce max pages: `PDF_PARSER__MAX_PAGES=15`
3. Process fewer papers concurrently

### flash-attention installation fails
**Problem:** Compilation errors during installation
**Solutions:**
1. Ensure CUDA toolkit is installed: `nvcc --version`
2. Update pip: `pip install --upgrade pip`
3. Check CUDA version compatibility with flash-attn
4. Install build dependencies: `pip install packaging ninja`

### Model download is slow
**Problem:** Large model download taking too long
**Solution:**
- Download once, then model is cached
- Use faster internet connection for first run
- Alternatively, manually download model to `~/.cache/huggingface/`

### DeepSeek is slower than Docling
**Problem:** Not seeing expected speed improvements
**Likely causes:**
- Running on CPU instead of GPU (check `torch.cuda.is_available()`)
- Using `large` resolution mode (switch to `base` or `small`)
- First run includes model loading time
- GPU is being used by other processes

## Comparison: DeepSeek vs Docling

| Aspect | DeepSeek OCR | Docling |
|--------|--------------|---------|
| **Speed (GPU)** | ~2500 tokens/s | ~200 tokens/s |
| **Speed (CPU)** | Slow (not recommended) | Moderate |
| **Accuracy** | 97% OCR precision | High |
| **Section Detection** | Via markdown headers | Via document structure |
| **Table Extraction** | Supported (markdown tables) | Supported |
| **Figure Extraction** | Supported (descriptions) | Supported |
| **GPU Requirement** | **Yes** | No |
| **Model Size** | ~Several GB | Smaller |
| **Installation** | Complex (flash-attn) | Simple |
| **Best Use Case** | Fast processing with GPU | CPU-only environments |

## Recommendations

**Use DeepSeek when:**
- ✅ You have GPU access (A100, H100, or similar)
- ✅ You need faster processing (4-10x speedup)
- ✅ Processing large volumes of papers daily
- ✅ You can handle the additional setup complexity

**Use Docling when:**
- ✅ No GPU available
- ✅ Simple setup required
- ✅ Processing small volumes of papers
- ✅ CPU resources are sufficient

**Hybrid Approach:**
- Use DeepSeek for production pipeline (speed)
- Keep Docling as fallback for GPU failures
- Switch via environment variable based on available resources

## Monitoring

Check which parser is being used in the logs:

```
INFO: Initializing DeepSeek OCR parser (GPU-accelerated)
INFO: DeepSeek model loaded on GPU: NVIDIA A100-SXM4-40GB
INFO: Successfully parsed paper.pdf with DeepSeek OCR - 5 sections found
```

vs

```
INFO: Initializing Docling parser
INFO: Parsed paper.pdf using docling
```

## Support

For issues specific to:
- **DeepSeek OCR:** Check [GitHub repo](https://github.com/deepseek-ai/DeepSeek-OCR)
- **Docling:** Check [Docling docs](https://github.com/DS4SD/docling)
- **This integration:** Open an issue in this repository

## Summary

DeepSeek OCR provides significant speed improvements for PDF processing when GPU is available. The integration is designed to be a drop-in replacement for Docling with minimal configuration changes. Section extraction works similarly for both parsers, ensuring consistent downstream processing regardless of which parser you choose.
