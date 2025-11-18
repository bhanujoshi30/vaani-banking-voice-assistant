# 🚀 Complete Setup Guide - Vaani Banking AI

## Quick Start (5 Minutes)

### Step 1: Install Ollama

```bash
# Install Ollama
brew install ollama

# Start Ollama server (keep this running in a separate terminal)
ollama serve
```

### Step 2: Setup AI Backend

```bash
# Navigate to project root
cd /Users/ashok/Documents/projects/vaani-banking-voice-assistant

# Go to AI directory
cd ai

# Run automated setup
./start.sh
```

The script will:
- ✅ Check Ollama is running
- ✅ Download required models (Qwen 2.5 7B, Llama 3.2 3B)
- ✅ Create virtual environment
- ✅ Install Python dependencies
- ✅ Start FastAPI server

### Step 3: Setup Frontend (Optional - Update for AI)

```bash
# In a new terminal, navigate to frontend
cd frontend

# Add environment variable for AI backend
echo "VITE_AI_BACKEND_URL=http://localhost:8001" > .env

# Restart frontend if running
npm run dev
```

### Step 4: Test the System

```bash
# In another terminal, test the AI backend
curl http://localhost:8001/health

# Test chat (update account number to match your data)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my account balance?",
    "user_id": 1,
    "session_id": "test-123",
    "language": "en-IN",
    "user_context": {
      "account_number": "ACC001",
      "name": "Test User"
    }
  }'
```

---

## Detailed Setup

### Prerequisites

- **macOS** with M4 Max chip (or any Mac with 16GB+ RAM)
- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Ollama** (for local LLM)

### 1. Install Ollama

```bash
# Option 1: Homebrew (recommended)
brew install ollama

# Option 2: Download from https://ollama.ai/download
```

### 2. Download AI Models

```bash
# Start Ollama server (in terminal 1)
ollama serve

# In terminal 2, download models
ollama pull qwen2.5:7b     # Primary model (4.7GB)
ollama pull llama3.2:3b    # Fast model (1.7GB)

# Verify downloads
ollama list
```

Expected output:
```
NAME              ID              SIZE     MODIFIED
qwen2.5:7b        abc123          4.7 GB   2 minutes ago
llama3.2:3b       def456          1.7 GB   1 minute ago
```

### 3. Setup Python Environment

```bash
# Navigate to AI directory
cd ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env
```

**Minimum configuration:**
```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_FAST_MODEL=llama3.2:3b

# Database (use existing backend database)
DATABASE_URL=sqlite:///../backend/vaani_banking.db

# LangSmith (optional but recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=  # Get from smith.langchain.com
LANGCHAIN_PROJECT=vaani-banking-assistant

# Azure TTS (optional - leave disabled for now)
AZURE_TTS_ENABLED=false
```

### 5. Get LangSmith API Key (Optional but Recommended)

1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Sign up for free account
3. Go to Settings → API Keys
4. Create new API key
5. Copy key to `.env` file

### 6. Start AI Backend

```bash
# Make sure you're in ai/ directory with venv activated
source venv/bin/activate

# Run the server
python main.py
```

Or use the startup script:
```bash
./start.sh
```

Server will start at: `http://localhost:8001`

### 7. Verify Backend is Running

```bash
# Health check
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "ollama_status": true,
  "azure_tts_available": false
}
```

### 8. Start Backend API (Existing)

```bash
# In new terminal, go to project root
cd /Users/ashok/Documents/projects/vaani-banking-voice-assistant

# Start existing backend
python main.py
```

Backend runs at: `http://localhost:8000`

### 9. Start Frontend

```bash
# In new terminal, go to frontend
cd frontend

# Create .env file with AI backend URL
echo "VITE_AI_BACKEND_URL=http://localhost:8001" > .env

# Start frontend
npm run dev
```

Frontend runs at: `http://localhost:5174`

---

## Testing the Integration

### Test 1: Health Check

```bash
curl http://localhost:8001/health
```

### Test 2: English Chat

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check my balance",
    "user_id": 1,
    "session_id": "test-session",
    "language": "en-IN",
    "user_context": {
      "account_number": "ACC001",
      "name": "John Doe"
    }
  }'
```

### Test 3: Hindi Chat

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "मेरा बैलेंस क्या है?",
    "user_id": 1,
    "session_id": "test-session",
    "language": "hi-IN",
    "user_context": {
      "account_number": "ACC001"
    }
  }'
```

### Test 4: Frontend Integration

1. Open browser to `http://localhost:5174`
2. Login with existing credentials
3. Navigate to Chat page
4. Send message: "What is my balance?"
5. Should get AI-powered response

---

## Running All Services

You need **4 terminals**:

### Terminal 1: Ollama
```bash
ollama serve
```

### Terminal 2: AI Backend
```bash
cd ai
source venv/bin/activate
python main.py
```

### Terminal 3: Backend API
```bash
python main.py  # From project root
```

### Terminal 4: Frontend
```bash
cd frontend
npm run dev
```

---

## Troubleshooting

### "Ollama connection error"

**Problem:** AI backend can't connect to Ollama

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve

# Verify it's accessible
curl http://localhost:11434/api/tags
```

### "Module not found" errors

**Problem:** Python imports failing

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path includes backend
python -c "import sys; print(sys.path)"
```

### "Database error"

**Problem:** Can't access database

**Solution:**
```bash
# Check database file exists
ls -la ../backend/vaani_banking.db

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Should be: sqlite:///../backend/vaani_banking.db
```

### "LangSmith not tracing"

**Problem:** No traces appearing in LangSmith

**Solution:**
```bash
# Verify .env settings (MUST be exact)
LANGCHAIN_TRACING_V2=true  # Not "True" or "1"
LANGCHAIN_API_KEY=lsv2_pt_xxx  # Your actual key

# Restart server after changing .env
```

### Frontend not calling AI backend

**Problem:** Chat still using mock responses

**Solution:**
```bash
# Check frontend .env has AI backend URL
cd frontend
cat .env

# Should contain:
# VITE_AI_BACKEND_URL=http://localhost:8001

# Restart frontend dev server
npm run dev
```

---

## Performance Tips

### For Faster Responses

1. **Use voice mode** - Automatically uses fast model (Llama 3.2 3B)
2. **Limit message history** - Only sends last 10 messages
3. **Warm up models** - First request is slower, subsequent ones are fast

### For Better Quality

1. **Use text mode** - Uses quality model (Qwen 2.5 7B)
2. **Provide context** - Include account number and name in user_context
3. **Clear intents** - Specific questions get better answers

---

## Next Steps

### Optional Enhancements

1. **Enable Azure TTS:**
   - Get Azure key from portal.azure.com
   - Add to `.env`:
     ```env
     AZURE_TTS_ENABLED=true
     AZURE_TTS_KEY=your_key
     AZURE_TTS_REGION=centralindia
     ```

2. **Add Redis Caching:**
   ```bash
   brew install redis
   redis-server
   ```
   Update `.env`:
   ```env
   REDIS_ENABLED=true
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Setup Vector Database (for RAG):**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
   Update `.env`:
   ```env
   QDRANT_ENABLED=true
   QDRANT_URL=http://localhost:6333
   ```

---

## Development Workflow

### Making Changes

1. **Backend changes:**
   - Edit files in `ai/` directory
   - Server auto-reloads (if using --reload flag)

2. **Test changes:**
   ```bash
   curl -X POST http://localhost:8001/api/chat -H "Content-Type: application/json" -d '{...}'
   ```

3. **View logs:**
   ```bash
   tail -f logs/ai_backend.log
   ```

4. **Check LangSmith:**
   - Go to smith.langchain.com
   - View traces for your project

---

## Production Deployment

For hackathon demo, current setup is sufficient.

For production:
1. Use Docker Compose (see docker-compose.yml)
2. Setup HTTPS with nginx
3. Use production database (PostgreSQL)
4. Enable all security features
5. Setup monitoring and alerts

---

## Support

**Issues:** Check logs in `ai/logs/ai_backend.log`

**Questions:** See `ai/README.md` for detailed documentation

**LangSmith:** View traces at smith.langchain.com for debugging

---

**🎉 You're all set! Start chatting with Vaani powered by Qwen 2.5 7B!**
