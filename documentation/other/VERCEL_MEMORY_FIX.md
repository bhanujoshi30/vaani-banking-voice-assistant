# Memory Optimization for Vercel Build

## Problem
Build is hitting "Out of Memory" (OOM) errors during dependency installation, even with minimal requirements.

## Root Cause
`resemblyzer`, `librosa`, and `soundfile` pull in heavy dependencies (PyTorch, audio processing libraries) that consume too much memory during build.

## Solution Applied

1. **Optimized requirements.txt**:
   - Removed test dependencies (`pytest`, `pytest-asyncio`, `pytest-cov`)
   - Removed `faker` (only needed for seeding, not production)
   - Added version constraints to prevent pulling latest heavy versions
   - Constrained `numpy` and `scipy` to avoid v2.x which might be heavier

2. **Build Memory Considerations**:
   - Vercel build environment: 8GB RAM
   - Heavy ML libraries can consume 4-6GB during installation
   - Optimized requirements reduce memory footprint

## Alternative Solutions (if still failing)

### Option 1: Make Voice Verification Optional
If voice verification isn't critical for initial deployment:
- Comment out `resemblyzer`, `librosa`, `soundfile` temporarily
- Deploy backend without voice features
- Add voice features later as separate service

### Option 2: Use External Voice Service
- Move voice verification to separate service (e.g., AWS Lambda, Google Cloud Functions)
- Backend calls external service via API
- Reduces backend deployment size

### Option 3: Upgrade Vercel Plan
- Vercel Pro plan has more build memory
- But this costs money

## Current Status

✅ Build script hides `pyproject.toml`  
✅ Uses `requirements.txt` (optimized)  
✅ Removed unnecessary dependencies  
⏳ Testing if OOM is resolved  

## Next Steps

1. Monitor next deployment
2. If OOM persists, consider Option 1 (make voice verification optional)
3. Or split voice verification into separate service

