# Hindi Font Setup Guide

## Problem
Hindi text in generated PDFs appears as colored blocks instead of readable text because ReportLab needs a proper Devanagari-supporting font.

## Solution

### Option 1: Download Noto Sans Devanagari (Recommended)

The easiest solution is to download the Noto Sans Devanagari font:

```bash
cd backend/documents
python download_hindi_font.py
```

This will download the font files to `backend/documents/fonts/` directory.

### Option 2: Use System Fonts with fonttools

If you have Devanagari fonts installed on your system (macOS has them by default), you can extract them:

```bash
pip install fonttools
```

The scripts will automatically extract `.ttc` (TrueType Collection) files to `.ttf` format.

### Option 3: Manual Font Installation

1. Download Noto Sans Devanagari from: https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari
2. Extract the `.ttf` files
3. Place them in `backend/documents/fonts/`:
   - `NotoSansDevanagari-Regular.ttf`
   - `NotoSansDevanagari-Bold.ttf` (optional)

## Verification

Before generating PDFs, verify that fonts are working:

```bash
cd backend/documents
python verify_hindi_font.py
```

This will:
1. Check if fonts are registered correctly
2. Create a test PDF (`test_hindi_verification.pdf`)
3. Show you if Hindi text renders correctly

**Open the test PDF and verify:**
- ✅ Hindi text is readable (not colored blocks)
- ✅ All characters render correctly
- ✅ Font looks good

## Regenerating PDFs

Once fonts are verified, regenerate Hindi PDFs:

```bash
# Regenerate loan documents
python create_loan_product_docs_hindi.py

# Regenerate investment documents
python create_investment_scheme_docs_hindi.py
```

## Troubleshooting

### Issue: "fonttools not available"
**Solution:** Install fonttools:
```bash
pip install fonttools
```

### Issue: "No Hindi fonts found"
**Solution:** 
1. Run `python download_hindi_font.py` to download fonts
2. Or manually place `.ttf` files in `backend/documents/fonts/`

### Issue: Hindi text still shows as blocks
**Solution:**
1. Verify fonts are downloaded: `ls backend/documents/fonts/`
2. Run verification script: `python verify_hindi_font.py`
3. Check the test PDF to see if fonts work
4. If test PDF works but generated PDFs don't, check console output for font registration messages

### Issue: Font registration fails
**Solution:**
1. Make sure font files are `.ttf` format (not `.ttc` without fonttools)
2. Check file permissions
3. Try downloading fonts again: `python download_hindi_font.py`

## Technical Details

The scripts use ReportLab's `TTFont` to register custom fonts. The font registration happens at import time, so you'll see messages like:

```
✅ Registered Hindi font: /path/to/font.ttf
✅ Registered Hindi bold font: /path/to/bold.ttf
```

If you see warnings instead, fonts may not work correctly.

## Font Files Location

Fonts are stored in: `backend/documents/fonts/`

This directory is created automatically and can contain:
- Downloaded Noto Sans Devanagari fonts
- Extracted fonts from system `.ttc` files

## Next Steps

After fonts are working:
1. ✅ Verify fonts with `verify_hindi_font.py`
2. ✅ Regenerate Hindi PDFs
3. ✅ Re-ingest documents: `python ai/ingest_documents_hindi.py`
4. ✅ Test the system with Hindi language selected

