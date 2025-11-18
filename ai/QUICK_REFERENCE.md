# 🚀 Quick Reference: Switching LLM Providers

## One-Line Switch

```bash
# Edit .env and change this line:
LLM_PROVIDER=ollama  # or openai
```

Then restart: `cd ai && ./run.sh`

---

## Provider Options

### 🏠 Ollama (Local - Default)
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
```
✅ Free, Private, No Internet  
❌ Needs local GPU/CPU power

### ☁️ OpenAI (Cloud)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```
✅ Fast, High Quality  
❌ Costs money, Requires internet

---

## Quick Test

```bash
cd ai
python test_llm_providers.py
```

---

## Code Example

```python
from services import get_llm_service

# Automatic (uses .env config)
llm = get_llm_service()
response = await llm.chat(messages)

# Manual override
from services import LLMProvider
llm = get_llm_service(provider=LLMProvider.OPENAI)
```

---

## Configuration Matrix

| Setting | Ollama | OpenAI |
|---------|--------|--------|
| `LLM_PROVIDER` | `ollama` | `openai` |
| **Required** | Ollama running | API key |
| **Optional** | Model names | Model name |
| **Cost** | Free | ~$0.002/1K tokens |

---

## Files Modified

1. **New Services:**
   - `services/openai_service.py` - OpenAI integration
   - `services/llm_service.py` - Unified interface

2. **Updated Agents:**
   - `agents/intent_classifier.py` - Uses unified service
   - `agents/banking_agent.py` - Uses unified service
   - `agents/faq_agent.py` - Uses unified service

3. **Configuration:**
   - `config.py` - Added OpenAI settings
   - `.env.example` - Added examples

4. **Documentation:**
   - `LLM_PROVIDER_GUIDE.md` - Full guide
   - `test_llm_providers.py` - Test script

---

## Troubleshooting

**Error:** "OpenAI API key not configured"
```bash
# Add to .env:
OPENAI_API_KEY=sk-your-actual-key
```

**Error:** "Failed to connect to Ollama"
```bash
ollama serve  # Start Ollama
```

**Error:** "Unknown LLM provider"
```bash
# Check .env has:
LLM_PROVIDER=ollama  # or openai (lowercase)
```

---

## 💰 Cost Comparison

**Ollama (Local):**
- Setup: Free
- Usage: Free
- Total: **$0**

**OpenAI GPT-3.5:**
- Setup: Free (account)
- Usage: $0.002 per 1K tokens
- Example: 1000 conversations/day ≈ **$5-10/month**

---

## 🎯 When to Use What?

**Use Ollama if:**
- Privacy is critical
- No budget for AI
- Have good local hardware
- Working offline

**Use OpenAI if:**
- Need best quality
- Limited local resources
- Budget available
- Want consistent speed

**Mix Both:**
- Ollama for development
- OpenAI for production
- Easy switch with one line!

---

📖 **Full Guide:** See `LLM_PROVIDER_GUIDE.md`  
🧪 **Test:** Run `python test_llm_providers.py`
