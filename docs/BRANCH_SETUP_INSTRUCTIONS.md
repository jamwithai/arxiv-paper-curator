# DeepSeek OCR Branch Setup Instructions

## Overview

The DeepSeek OCR integration is in a **separate feature branch** so you can:
1. Keep `main` branch stable with working Docling parser
2. Test DeepSeek on GPU machine without affecting main code
3. Merge to main only after GPU testing is complete

---

## Branch Information

**Branch name:** `feature/deepseek-ocr-integration`
**Status:** Ready for GPU testing
**Commit:** Complete integration with docs and tests

---

## Setup on Another Machine (with GPU)

### 1. Clone Repository (if not already cloned)

```bash
git clone https://github.com/jamwithai/arxiv-paper-curator
cd arxiv-paper-curator
```

### 2. Checkout DeepSeek Feature Branch

```bash
# Fetch all branches
git fetch origin

# Checkout the DeepSeek integration branch
git checkout feature/deepseek-ocr-integration

# Verify you're on the right branch
git branch
# Should show: * feature/deepseek-ocr-integration
```

### 3. Install Dependencies

```bash
# Install base dependencies
uv sync

# Install flash-attention (GPU-specific, takes ~5 min)
pip install flash-attn --no-build-isolation
```

**Troubleshooting flash-attn:**
- Requires CUDA toolkit: `nvcc --version`
- Requires gcc/g++: `gcc --version`
- If installation fails, check CUDA version compatibility

### 4. Verify GPU Access

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

**Expected output:**
```
CUDA available: True
GPU: NVIDIA A100-SXM4-40GB
```

### 5. Configure Parser

Create or update `.env`:

```bash
# Switch to DeepSeek parser
PDF_PARSER__PARSER_TYPE=deepseek

# DeepSeek configuration
PDF_PARSER__DEEPSEEK_RESOLUTION=base  # tiny|small|base|large
PDF_PARSER__DEEPSEEK_MODEL=deepseek-ai/DeepSeek-OCR

# Common settings
PDF_PARSER__MAX_PAGES=30
PDF_PARSER__MAX_FILE_SIZE_MB=20
```

### 6. Test the Integration

**Quick test on sample PDF:**
```bash
# Download test PDF
python scripts/download_sample_pdf.py

# Test both parsers
python test_both_parsers.py test_pdfs/2501.10234.pdf
```

**Test on your PDFs:**
```bash
# Test Docling (baseline)
python test_parsers_simple.py pdfs/your_paper.pdf

# Compare both parsers
python test_both_parsers.py pdfs/your_paper.pdf
```

**Expected output:**
```
✅ BOTH PARSERS SUCCEEDED!
✅ FINAL VERDICT: OUTPUT STRUCTURES ARE COMPATIBLE
✅ DeepSeek model loaded on GPU: NVIDIA A100-SXM4-40GB
```

### 7. Run Your Pipeline

Your existing pipeline code needs **zero changes**:

```python
# This automatically uses DeepSeek now:
from src.services.pdf_parser.factory import make_pdf_parser_service

parser = make_pdf_parser_service()
result = await parser.parse_pdf(pdf_path)

# result works exactly the same as with Docling!
```

---

## Switching Between Parsers

**Use DeepSeek (GPU-accelerated):**
```bash
# In .env:
PDF_PARSER__PARSER_TYPE=deepseek
```

**Use Docling (CPU-friendly):**
```bash
# In .env:
PDF_PARSER__PARSER_TYPE=docling
```

**No code changes, just restart your service!**

---

## Verify It's Working

### Check Logs

```bash
# Should see:
INFO: Initializing DeepSeek OCR parser (GPU-accelerated)
INFO: DeepSeek model loaded on GPU: NVIDIA A100-SXM4-40GB
INFO: Successfully parsed paper.pdf with DeepSeek OCR - 15 sections found
```

### Monitor GPU Usage

```bash
# Watch GPU usage during processing
nvidia-smi -l 1
```

### Check Performance

**Expected on GPU (A100-40GB):**
- First page: ~10 seconds (model loading)
- Subsequent pages: ~0.4 seconds each
- 30-page paper: ~15 seconds total
- **4-10x faster than Docling**

---

## After GPU Testing is Complete

### Option 1: Merge to Main (Recommended)

If DeepSeek works well on GPU:

```bash
# Switch to main
git checkout main

# Merge the feature branch
git merge feature/deepseek-ocr-integration

# Push to remote
git push origin main
```

### Option 2: Keep Using Branch

If you want to keep testing:

```bash
# Stay on feature branch
git checkout feature/deepseek-ocr-integration

# Pull latest changes if needed
git pull origin feature/deepseek-ocr-integration
```

### Option 3: Delete Branch (If Not Needed)

If DeepSeek doesn't work well:

```bash
# Switch back to main
git checkout main

# Delete local branch
git branch -d feature/deepseek-ocr-integration

# Delete remote branch
git push origin --delete feature/deepseek-ocr-integration
```

---

## What's in This Branch

### Core Implementation
- `src/services/pdf_parser/deepseek.py` - DeepSeek OCR parser
- `src/services/pdf_parser/parser.py` - Updated to support both parsers
- `src/config.py` - Parser configuration options
- `pyproject.toml` - Added dependencies

### Documentation
- `docs/QUICKSTART_DEEPSEEK.md` - Quick start guide
- `docs/DEEPSEEK_OCR_SETUP.md` - Detailed setup instructions
- `docs/IMPLEMENTATION_REVIEW.md` - Design review (SOLID/KISS)
- `docs/TEST_RESULTS.md` - Test results on actual PDFs

### Testing
- `test_parsers_simple.py` - Test individual parsers
- `test_both_parsers.py` - Compare both parsers
- `tests/test_parser_comparison.py` - Automated comparison
- `scripts/download_sample_pdf.py` - Download test PDFs

### Modified Files
- `src/schemas/pdf_parser/models.py` - Added ParserType.DEEPSEEK
- `src/services/pdf_parser/factory.py` - Factory supports both parsers
- `.env.example` - Configuration examples

---

## Differences from Main Branch

**Main branch:**
- ✅ Only Docling parser
- ✅ Stable and tested
- ✅ Works on CPU

**Feature branch:**
- ✅ Docling parser (unchanged)
- ✅ DeepSeek parser (new)
- ✅ Configuration-based switching
- ✅ Requires GPU for speed benefits

**Both produce identical output structures!**

---

## Troubleshooting

### "Branch not found"

```bash
git fetch origin
git checkout feature/deepseek-ocr-integration
```

### "CUDA not available" on GPU machine

```bash
# Reinstall PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### "flash-attn installation failed"

```bash
# Install build dependencies
pip install packaging ninja wheel setuptools

# Retry installation
pip install flash-attn --no-build-isolation
```

### "DeepSeek is slow"

Check if running on GPU:
```bash
# Monitor GPU usage
nvidia-smi -l 1

# Check in Python
python -c "import torch; print(torch.cuda.is_available())"
```

If `False`, DeepSeek runs on CPU (very slow). Use Docling instead.

---

## Quick Command Reference

```bash
# Setup
git checkout feature/deepseek-ocr-integration
uv sync
pip install flash-attn --no-build-isolation

# Configure
echo "PDF_PARSER__PARSER_TYPE=deepseek" >> .env

# Test
python test_both_parsers.py test_pdfs/2501.10234.pdf

# Run pipeline (no code changes)
# Your existing code works automatically!

# Monitor GPU
nvidia-smi -l 1

# Switch back to Docling
echo "PDF_PARSER__PARSER_TYPE=docling" >> .env
```

---

## Support

- **Branch issues:** Check this doc
- **DeepSeek setup:** See `docs/DEEPSEEK_OCR_SETUP.md`
- **Quick start:** See `docs/QUICKSTART_DEEPSEEK.md`
- **Design questions:** See `docs/IMPLEMENTATION_REVIEW.md`
- **Test results:** See `docs/TEST_RESULTS.md`

---

## Summary

1. ✅ Checkout branch: `git checkout feature/deepseek-ocr-integration`
2. ✅ Install deps: `uv sync && pip install flash-attn --no-build-isolation`
3. ✅ Configure: `PDF_PARSER__PARSER_TYPE=deepseek` in `.env`
4. ✅ Test: `python test_both_parsers.py test_pdfs/2501.10234.pdf`
5. ✅ Run: Your existing code works unchanged!

**Main branch stays clean. Test DeepSeek on GPU machine. Merge when ready!**
