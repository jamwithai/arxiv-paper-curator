# DeepSeek OCR Quick Start Guide

## TL;DR

```bash
# 1. Install dependencies
uv sync
pip install flash-attn --no-build-isolation

# 2. Update .env
echo "PDF_PARSER__PARSER_TYPE=deepseek" >> .env

# 3. Test it
python scripts/download_sample_pdf.py
python tests/test_parser_comparison.py test_pdfs/2501.10234.pdf

# 4. Done! Your pipeline now uses GPU-accelerated OCR
```

---

## Step-by-Step Setup

### 1. Prerequisites

**Check GPU availability:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

If `False`, DeepSeek will be slower than Docling. Stick with Docling.

### 2. Install Dependencies

**Install base packages:**
```bash
uv sync
```

**Install flash-attention (GPU-specific, takes ~5 min):**
```bash
pip install flash-attn --no-build-isolation
```

**Troubleshooting flash-attn:**
- Requires CUDA toolkit: `nvcc --version`
- Requires gcc/g++: `gcc --version`
- If fails, check CUDA version compatibility

### 3. Configure Parser Type

**Option A: Environment variable (recommended)**
```bash
# In your .env file:
PDF_PARSER__PARSER_TYPE=deepseek
```

**Option B: Direct edit**
```python
# In src/config.py, change default:
parser_type: str = "deepseek"
```

### 4. First Run

**Download test PDF:**
```bash
python scripts/download_sample_pdf.py
```

**Test both parsers:**
```bash
python tests/test_parser_comparison.py test_pdfs/2501.10234.pdf
```

**Expected first run:**
- Model download: ~3-5 GB (one-time)
- First page: ~10 seconds (model loading)
- Subsequent pages: ~0.4 seconds each

### 5. Production Use

**Your existing code needs NO changes!**

```python
# This automatically uses DeepSeek now:
from src.services.pdf_parser.factory import make_pdf_parser_service

parser = make_pdf_parser_service()
result = await parser.parse_pdf(pdf_path)

# result.parser_used == ParserType.DEEPSEEK ✓
# result.sections works exactly the same ✓
```

---

## Configuration Options

### Resolution Modes

Edit `.env`:
```bash
# Fast, lower accuracy (64 tokens/page)
PDF_PARSER__DEEPSEEK_RESOLUTION=tiny

# Balanced (100 tokens/page)
PDF_PARSER__DEEPSEEK_RESOLUTION=small

# Recommended (256 tokens/page)
PDF_PARSER__DEEPSEEK_RESOLUTION=base

# Best accuracy (400 tokens/page)
PDF_PARSER__DEEPSEEK_RESOLUTION=large
```

**Start with `base`, adjust if needed:**
- GPU memory errors → use `small` or `tiny`
- Need better accuracy → use `large`

### Switch Back to Docling

```bash
# In .env:
PDF_PARSER__PARSER_TYPE=docling
```

**No code changes needed!** Just restart your service.

---

## Verification

### Check which parser is active:

```bash
# Run your service and check logs:
grep "Initializing.*parser" logs/app.log
```

**Expected output:**
```
INFO: Initializing DeepSeek OCR parser (GPU-accelerated)
INFO: DeepSeek model loaded on GPU: NVIDIA A100-SXM4-40GB
```

### Test output compatibility:

```bash
python tests/test_parser_comparison.py <your_pdf_path>
```

Should show:
```
✅ Downstream Compatibility: PASSED
   Both parsers produce identical output structures.
```

---

## Performance

### Expected Speed (with GPU)

**DeepSeek OCR on A100-40GB:**
- Model loading: ~5-10 seconds (first run only)
- Per page: ~0.4 seconds
- 30-page paper: ~15 seconds total

**Docling (baseline):**
- Per page: ~2-5 seconds
- 30-page paper: ~60-150 seconds total

**Speedup: 4-10x faster** 🚀

### Memory Usage

| Resolution | GPU Memory | Speed | Accuracy |
|------------|------------|-------|----------|
| tiny       | ~2 GB      | Fast  | Lower    |
| small      | ~3 GB      | Fast  | Medium   |
| base       | ~4 GB      | Good  | High     |
| large      | ~6 GB      | Slower| Highest  |

**Recommendation:** Start with `base`, it's the sweet spot.

---

## Troubleshooting

### "CUDA not available"

**Check:**
```bash
nvidia-smi  # Should show your GPU
nvcc --version  # Should show CUDA version
python -c "import torch; print(torch.cuda.is_available())"
```

**Fix:**
```bash
# Reinstall PyTorch with CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### "Out of memory"

**Solutions:**
1. Use smaller resolution: `PDF_PARSER__DEEPSEEK_RESOLUTION=small`
2. Reduce max pages: `PDF_PARSER__MAX_PAGES=15`
3. Close other GPU applications

### "flash-attn installation failed"

**Common causes:**
- Missing CUDA toolkit
- Wrong CUDA version
- Missing build tools

**Fix:**
```bash
# Install build dependencies
pip install packaging ninja wheel setuptools

# Retry installation
pip install flash-attn --no-build-isolation
```

### "DeepSeek is slow"

**Check GPU usage:**
```bash
nvidia-smi -l 1  # Monitor GPU usage
```

**If GPU shows 0% usage:**
- Model is running on CPU (very slow!)
- Check `torch.cuda.is_available()` returns `True`
- Check logs for GPU loading confirmation

---

## FAQ

**Q: Can I use both parsers in the same application?**
A: Yes! Switch via environment variable, no code changes needed.

**Q: Do I need to change my database schema?**
A: No. Both parsers produce the same `PdfContent` structure.

**Q: Can I use DeepSeek without GPU?**
A: Technically yes, but it will be MUCH slower than Docling. Not recommended.

**Q: What if DeepSeek fails on a PDF?**
A: The parser returns `None`, same as Docling. Your existing error handling works.

**Q: Can I process multiple PDFs in parallel?**
A: Yes, but watch GPU memory. Reduce `MAX_CONCURRENT_PARSING` if needed.

**Q: Do I need to modify my indexing/chunking code?**
A: No. The output structure is identical to Docling.

---

## Next Steps

1. ✅ Run the comparison test
2. ✅ Verify GPU acceleration is working
3. ✅ Test on your actual PDFs
4. ✅ Measure speed improvement
5. ✅ Adjust resolution if needed
6. ✅ Deploy to production!

---

## Support

**If DeepSeek integration issues:**
- Check `docs/IMPLEMENTATION_REVIEW.md` for design details
- Check `docs/DEEPSEEK_OCR_SETUP.md` for detailed setup
- Run comparison test to verify compatibility

**If DeepSeek model issues:**
- Check [official repo](https://github.com/deepseek-ai/DeepSeek-OCR)
- Check HuggingFace model page

**If general parser issues:**
- Both parsers share same validation logic
- Check logs for specific error messages
- Verify PDF is valid and within size/page limits
