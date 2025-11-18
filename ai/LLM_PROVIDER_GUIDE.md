# LLM Provider Switching Guide

Vaani Banking Assistant supports both **local (Ollama)** and **cloud (OpenAI)** LLM providers. You can easily switch between them with a simple configuration change.

## 🎯 Quick Switch

Edit your `.env` file and change the `LLM_PROVIDER` setting:

```bash
# Use Ollama (local, free, privacy-friendly)
LLM_PROVIDER=ollama

# OR use OpenAI (cloud, requires API key, costs money)
LLM_PROVIDER=openai
```

Restart the AI backend and you're done! 🚀

---

## 📋 Provider Comparison

| Feature | Ollama (Local) | OpenAI (Cloud) |
|---------|---------------|----------------|
| **Cost** | Free | Pay per token (~$0.002/1K tokens) |
| **Privacy** | 100% local, no data sent | Data sent to OpenAI servers |
| **Speed** | Depends on hardware | Fast, consistent |
| **Setup** | Requires Ollama installation | Just needs API key |
| **Models** | Qwen 2.5 7B, Llama 3.2 3B | GPT-3.5 Turbo, GPT-4 |
| **Internet** | Not required | Required |
| **Quality** | Good, depends on model | Excellent |

---

## 🔧 Setup Instructions

### Option 1: Ollama (Local) - Default

**Prerequisites:**
- Ollama installed and running
- Models pulled: `qwen2.5:7b` and `llama3.2:3b`

**Configuration:**
```bash
# .env file
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_FAST_MODEL=llama3.2:3b
```

**Installation:**
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull qwen2.5:7b
ollama pull llama3.2:3b

# Start Ollama (if not running)
ollama serve
```

**Verify:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

---

### Option 2: OpenAI (Cloud)

**Prerequisites:**
- OpenAI account
- API key from https://platform.openai.com/api-keys
- Active billing/credits

**Configuration:**
```bash
# .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4
OPENAI_ENABLED=true
```

**Available Models:**
- `gpt-3.5-turbo` - Fast, cheap ($0.002/1K tokens)
- `gpt-4` - Best quality ($0.03/1K tokens)
- `gpt-4-turbo-preview` - Faster GPT-4

**Verify:**
```bash
# Test your API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 💻 Code Usage

The unified LLM service automatically uses your configured provider:

```python
from services import get_llm_service

# Get LLM service (uses config to decide ollama/openai)
llm = get_llm_service()

# Chat completion
response = await llm.chat([
    {"role": "user", "content": "What is my account balance?"}
])

# Streaming response
async for chunk in llm.chat_stream(messages):
    print(chunk, end="")

# Check current provider
print(f"Using: {llm.get_provider_name()}")  # "ollama" or "openai"
```

### Explicit Provider Selection

```python
from services import get_llm_service, LLMProvider

# Force Ollama
llm_local = get_llm_service(provider=LLMProvider.OLLAMA)

# Force OpenAI
llm_cloud = get_llm_service(provider=LLMProvider.OPENAI)
```

---

## 🔄 Switching During Runtime

You can switch providers without code changes:

1. Update `.env` file:
   ```bash
   LLM_PROVIDER=openai  # or ollama
   ```

2. Restart AI backend:
   ```bash
   cd ai
   ./run.sh
   ```

The system automatically detects the change!

---

## ⚙️ Advanced Configuration

### Temperature & Top-P

Control response randomness (works for both providers):

```bash
# .env
LLM_TEMPERATURE=0.7  # 0.0 = deterministic, 2.0 = very random
LLM_TOP_P=0.9        # Nucleus sampling
LLM_MAX_TOKENS=512   # Maximum response length
```

### Fast Model (Ollama Only)

Ollama supports a fast model for quick tasks like intent classification:

```python
# Use fast model (llama3.2:3b)
response = await llm.chat(messages, use_fast_model=True)

# Use main model (qwen2.5:7b)
response = await llm.chat(messages, use_fast_model=False)
```

For OpenAI, `use_fast_model` is ignored (always uses configured model).

---

## 🧪 Testing

Test your LLM provider:

```bash
cd ai

# Test Ollama
python -c "
from services import get_llm_service, LLMProvider
import asyncio

async def test():
    llm = get_llm_service(LLMProvider.OLLAMA)
    response = await llm.chat([{'role': 'user', 'content': 'Hello!'}])
    print(response)

asyncio.run(test())
"

# Test OpenAI
python -c "
from services import get_llm_service, LLMProvider
import asyncio

async def test():
    llm = get_llm_service(LLMProvider.OPENAI)
    response = await llm.chat([{'role': 'user', 'content': 'Hello!'}])
    print(response)

asyncio.run(test())
"
```

---

## 🛡️ Security Best Practices

### For OpenAI:

1. **Never commit API keys** to git
   ```bash
   # .env is already in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables** in production
   ```bash
   export OPENAI_API_KEY="sk-your-key"
   ```

3. **Set spending limits** in OpenAI dashboard

4. **Rotate keys regularly**

### For Ollama:

1. **Firewall protection** - Don't expose Ollama port (11434) to internet
2. **Local network only** - Keep Ollama on localhost or internal network

---

## 📊 Cost Estimation (OpenAI)

Approximate costs for GPT-3.5 Turbo:

| Usage | Tokens/Month | Cost/Month |
|-------|-------------|-----------|
| Light (100 chats/day) | ~500K | ~$1 |
| Medium (500 chats/day) | ~2.5M | ~$5 |
| Heavy (2000 chats/day) | ~10M | ~$20 |

**Note:** Actual costs vary based on conversation length and complexity.

---

## 🐛 Troubleshooting

### Ollama Issues:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve

# Re-pull models
ollama pull qwen2.5:7b
ollama pull llama3.2:3b
```

### OpenAI Issues:

```bash
# Verify API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check error logs
tail -f ai/logs/ai_backend.log | grep openai
```

### Common Errors:

1. **"OpenAI API key not configured"**
   - Add `OPENAI_API_KEY` to `.env`

2. **"Failed to connect to Ollama"**
   - Start Ollama: `ollama serve`

3. **"Unknown LLM provider"**
   - Check `LLM_PROVIDER` is either "ollama" or "openai"

---

## 📚 Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Qwen 2.5 Model Card](https://ollama.com/library/qwen2.5)
- [GPT-3.5 Turbo Guide](https://platform.openai.com/docs/models/gpt-3-5-turbo)

---

## 🎉 That's It!

You can now seamlessly switch between local and cloud LLM providers. Choose based on your needs:

- **Development/Privacy/Free** → Use Ollama
- **Production/Quality/Scale** → Use OpenAI (or mix both!)

Happy coding! 🚀
