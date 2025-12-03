# Vaani Banking Voice Assistant - Complete Setup Guide

## Overview

Vaani is a full-stack voice-enabled banking assistant with three main components:
- **Frontend**: React (Vite) - User interface with voice capabilities
- **Backend**: FastAPI - Authentication, banking operations, database
- **AI**: LangGraph + Ollama - Multi-agent conversational AI

This guide will walk you through setting up the entire system from scratch.

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Python 3.11+**
   ```bash
   python3 --version
   # Should show Python 3.11.0 or higher
   ```

2. **Node.js 18+**
   ```bash
   node --version
   # Should show v18.0.0 or higher
   ```

3. **uv Package Manager** (Python package installer)
   ```bash
   # Install uv (faster than pip)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or via Homebrew on macOS
   brew install uv
   
   # Verify installation
   uv --version
   ```

4. **Ollama** (Local LLM runtime)
   ```bash
   # macOS
   brew install ollama
   
   # Or download from https://ollama.com
   
   # Verify installation
   ollama --version
   ```

### System Requirements

- **OS**: macOS, Linux, or Windows (WSL2)
- **RAM**: Minimum 16GB (32GB+ recommended for better AI performance)
- **Storage**: At least 10GB free space for models
- **Network**: Internet connection for initial setup

---

## Step 1: Clone and Setup Project

```bash
# Navigate to your projects directory
cd ~/Documents/projects

# Clone the repository (if not already done)
git clone https://github.com/bhanujoshi30/vaani-banking-voice-assistant.git

# Navigate to project root
cd vaani-banking-voice-assistant
```

---

## Step 2: Install and Setup Ollama

Ollama runs the AI models locally on your machine.

### Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows - Download from https://ollama.com/download/windows
```

### Start Ollama Server

```bash
# Start Ollama in a dedicated terminal window
ollama serve
```

**Keep this terminal running** throughout your development session.

### Pull Required Models

Open a **new terminal** and run:

```bash
# Pull Qwen 2.5 7B (Primary model - best for Hindi + English)
ollama pull qwen2.5:7b

# Pull Llama 3.2 3B (Fast model for voice mode)
ollama pull llama3.2:3b

# Verify models are downloaded
ollama list
```

**Expected output:**
```
NAME              ID              SIZE      MODIFIED
qwen2.5:7b        abc123...       4.7 GB    2 minutes ago
llama3.2:3b       def456...       1.7 GB    1 minute ago
```

**Note**: The first download will take 5-10 minutes depending on your internet connection.

---

## Step 3: Setup Python Environment

### Create Virtual Environment

```bash
# From project root directory
uv venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows
```

You should see `(.venv)` prefix in your terminal prompt.

### Install Root Dependencies

```bash
# Install main project dependencies
uv pip install -r requirements.txt
```

### Extract Hindi Fonts (Optional but Recommended)

For Hindi PDF document generation:

```bash
# Navigate to documents folder
cd backend/documents

# Extract Devanagari fonts from macOS system
python extract_system_hindi_font.py

# Verify fonts extracted
ls fonts/
# Should show: DevanagariSangamMNRegular.ttf, DevanagariSangamMNBold.ttf

# Test font rendering (creates test_hindi_font.pdf)
python verify_hindi_font.py

# Return to project root
cd ../..
```

**Note**: This step is only needed if you plan to regenerate Hindi PDFs. Pre-generated Hindi PDFs are already included in the repository.

### Install AI Module Dependencies

```bash
# Install AI backend dependencies
uv pip install -r ai/requirements.txt
```

**Note**: Using `uv` instead of `pip` significantly speeds up package installation.

---

## Step 4: Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Return to project root
cd ..
```

---

## Step 5: Configure Environment Variables

### Backend Configuration

The backend uses SQLite by default, so no additional configuration is needed for basic setup. Configuration files are already set up.

### AI Backend Configuration (Optional)

The AI backend works out of the box with default settings. For advanced features:

```bash
# Navigate to AI directory
cd ai

# Copy example environment file (if you want to customize)
cp .env.example .env

# Edit .env for custom settings (optional)
nano .env
```

**Key configuration options** (all optional):

```env
# Ollama Configuration (defaults work for local setup)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_FAST_MODEL=llama3.2:3b

# LangSmith Tracing (optional but recommended for debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key_here  # Get from smith.langchain.com
LANGCHAIN_PROJECT=vaani-banking-assistant

# Azure TTS (optional - for better voice quality)
AZURE_TTS_ENABLED=false
# AZURE_TTS_KEY=your_azure_key
# AZURE_TTS_REGION=centralindia

# Database (uses backend database by default)
DATABASE_URL=sqlite:///../backend/vaani.db

# API Configuration
API_PORT=8001
API_HOST=0.0.0.0
```

**Return to project root:**
```bash
cd ..
```

---

## Step 6: Setup RAG Vector Databases (Optional but Recommended)

The RAG (Retrieval-Augmented Generation) system provides intelligent answers about loans and investments using PDF documents.

### Generate Documents (If Not Present)

Pre-generated PDFs are already included, but you can regenerate them:

**English Loan Documents**:
```bash
cd backend/documents
python create_loan_product_docs.py
# Creates 7 PDFs in loan_products/
cd ../..
```

**Hindi Loan Documents**:
```bash
cd backend/documents
python create_loan_product_docs_hindi.py
# Creates 7 PDFs in loan_products_hindi/
cd ../..
```

**English Investment Documents**:
```bash
cd backend/documents
python create_investment_scheme_docs.py
# Creates investment scheme PDFs in investment_schemes/
cd ../..
```

**Hindi Investment Documents**:
```bash
cd backend/documents
python create_investment_scheme_docs_hindi.py
# Creates investment scheme PDFs in investment_schemes_hindi/
cd ../..
```

### Ingest Documents into Vector Databases

**English Documents** (Loans + Investments):
```bash
cd ai

# Ingest English loan documents
python ingest_documents.py
# Creates: chroma_db/loan_products/

# Ingest English investment documents
python ingest_investment_documents.py
# Creates: chroma_db/investment_schemes/

cd ..
```

**Hindi Documents** (Loans + Investments):
```bash
cd ai

# Ingest Hindi documents (both loans and investments)
python ingest_documents_hindi.py
# Creates: 
#   - chroma_db/loan_products_hindi/
#   - chroma_db/investment_schemes_hindi/

cd ..
```

**Expected Completion Time**: 2-5 minutes total

**What This Does**:
- Loads PDF documents
- Splits text into chunks (1000 characters each)
- Generates embeddings using `sentence-transformers/all-MiniLM-L6-v2`
- Stores in ChromaDB vector database
- Enables semantic search for loan/investment queries

**Verify Success**:
```bash
# Check vector databases exist
ls ai/chroma_db/
# Should show:
#   loan_products/
#   loan_products_hindi/
#   investment_schemes/
#   investment_schemes_hindi/
```

**Skip This Step If**:
- You don't need RAG features
- Vector databases already exist
- You're just testing basic banking features

---

## Step 7: Initialize SQLite Database (Optional)

The SQLite database (`backend/db/vaani.db`) will be created automatically on first run with the necessary schema. To populate it with sample data for testing:

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Run database seed script (creates sample users and transactions)
python -m backend.db.seed
```

**What This Creates:**
- Sample user accounts with different profiles
- Bank accounts with initial balances
- Transaction history
- Reminders and beneficiaries
- Device bindings for testing

**Database Details:**
- **Type**: SQLite3 (file-based, no server required)
- **Location**: `backend/db/vaani.db`
- **Size**: ~100KB initially, grows with usage
- **Backup**: Simply copy the `vaani.db` file

**Note**: The database is SQLite for development. For production, the system can be configured to use PostgreSQL by setting environment variables.

---

## Step 8: Run All Services

Now you're ready to start all three components!

### Option 1: Run All Services Together (Recommended)

```bash
# From project root, with virtual environment activated
source .venv/bin/activate

# Run all services with a single command
python run_services.py
```

This starts:
1. **Backend** on `http://localhost:8000`
2. **AI Backend** on `http://localhost:8001`
3. **Frontend** on `http://localhost:5173`

**Press Ctrl+C to stop all services.**

### Option 2: Run Services Manually (For Debugging)

If you need more control or want to see logs separately, run each service in its own terminal:

**Terminal 1: Backend**
```bash
cd vaani-banking-voice-assistant
source .venv/bin/activate
python main.py
```

**Terminal 2: AI Backend**
```bash
cd vaani-banking-voice-assistant/ai
source ../.venv/bin/activate
./run.sh
# OR
python main.py
```

**Terminal 3: Frontend**
```bash
cd vaani-banking-voice-assistant/frontend
npm run dev
```

**Terminal 4: Ollama** (should already be running from Step 2)
```bash
ollama serve
```

---

## Step 8: Verify Installation

### Check Backend Health

```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Check AI Backend Health

```bash
curl http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "ollama_status": true,
  "azure_tts_available": false
}
```

### Check Frontend

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the Vaani login page.

---

## Step 9: Test the Application

### Login to Application

1. Open browser: `http://localhost:5173`
2. Use test credentials (from seeded data):
   - **User ID**: `john.doe`
   - **Password**: `password123`
3. Click "Sign In"

### Test Voice Chat

1. Navigate to **Chat** page (sidebar menu)
2. Click microphone icon to enable voice mode
3. Speak: "Check my account balance"
4. System should respond with your balance

### Test Text Chat

1. Type in chat: "Show my recent transactions"
2. AI should respond with transaction history

### Test UPI Payment

1. In chat, type: "Hello Vaani, pay ₹500 to John via UPI"
2. Accept UPI consent (first time)
3. Enter 6-digit PIN
4. Verify transaction success

---

## Common Issues and Solutions

### Issue 1: "Ollama connection refused"

**Problem**: AI backend cannot connect to Ollama

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve

# Verify it's accessible
curl http://localhost:11434/api/tags
```

### Issue 2: "Module not found" errors

**Problem**: Python packages not installed correctly

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
uv pip install -r requirements.txt
uv pip install -r ai/requirements.txt
```

### Issue 3: Frontend not connecting to backend

**Problem**: CORS or network issues

**Solution**:
```bash
# Check all services are running
curl http://localhost:8000/api/health  # Backend
curl http://localhost:8001/health      # AI Backend
curl http://localhost:5173             # Frontend

# Check browser console for CORS errors
# Ensure backend allows frontend origin in CORS settings
```

### Issue 4: "Database not found"

**Problem**: Database file doesn't exist

**Solution**:
```bash
# Run backend once to create database
python main.py

# Or manually seed database
python -m backend.db.seed
```

### Issue 5: Models not downloaded

**Problem**: Ollama models not pulled

**Solution**:
```bash
# Check installed models
ollama list

# If missing, pull them
ollama pull qwen2.5:7b
ollama pull llama3.2:3b
```

### Issue 6: Port already in use

**Problem**: Port 8000, 8001, or 5173 is occupied

**Solution**:
```bash
# Find process using the port (macOS/Linux)
lsof -i :8000
lsof -i :8001
lsof -i :5173

# Kill the process
kill -9 <PID>

# Or change port in configuration files
```

---

## Development Workflow

### Daily Startup

```bash
# Terminal 1: Start Ollama (if not already running)
ollama serve

# Terminal 2: Start all services
cd vaani-banking-voice-assistant
source .venv/bin/activate
python run_services.py
```

### Making Changes

**Backend changes:**
- Edit files in `backend/` directory
- Server auto-reloads (uvicorn --reload)

**AI changes:**
- Edit files in `ai/` directory
- Server auto-reloads

**Frontend changes:**
- Edit files in `frontend/src/`
- Vite hot-reloads automatically

### Viewing Logs

**Combined logs:**
- All logs appear in terminal running `run_services.py`

**Individual logs:**
- Backend: Console output
- AI: `ai/logs/ai_backend.log`
- Frontend: Browser console

---

## Optional Enhancements

### Enable LangSmith Tracing (Recommended for AI Debugging)

1. Create free account at [smith.langchain.com](https://smith.langchain.com)
2. Get API key from settings
3. Add to `ai/.env`:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_your_key_here
   LANGCHAIN_PROJECT=vaani-banking-assistant
   ```
4. Restart AI backend
5. View traces in LangSmith dashboard

### Enable Azure TTS (Better Voice Quality)

1. Create Azure account and get Speech Service key
2. Add to `ai/.env`:
   ```env
   AZURE_TTS_ENABLED=true
   AZURE_TTS_KEY=your_azure_key
   AZURE_TTS_REGION=centralindia
   ```
3. Restart AI backend

---

## Next Steps

Now that your setup is complete:

1. **Explore the documentation**:
   - [Architecture Overview](../ai_architecture.md)
   - [Backend Documentation](../backend_architecture.md)
   - [Frontend Documentation](../frontend-architecture.md)

2. **Learn the features**:
   - [UPI Payment Flow](./upi_payment_flow.md)
   - [Voice Authentication](./voice_authentication.md)
   - [API Reference](./api_reference.md)

3. **Start developing**:
   - Add new banking features
   - Enhance AI agents
   - Improve voice recognition
   - Add new UI components

---

## Support and Resources

**Documentation**: See `documentation/` folder for detailed guides

**Logs**: 
- Backend: Console output
- AI: `ai/logs/ai_backend.log`
- Frontend: Browser DevTools console

**LangSmith**: View AI traces at [smith.langchain.com](https://smith.langchain.com)

**Issues**: Check logs first, then see troubleshooting section above

---

## Summary Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] uv package manager installed
- [ ] Ollama installed and running
- [ ] Models pulled (qwen2.5:7b, llama3.2:3b)
- [ ] Virtual environment created (`.venv`)
- [ ] Python dependencies installed (`uv pip install -r requirements.txt`)
- [ ] AI dependencies installed (`uv pip install -r ai/requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Database seeded (optional)
- [ ] All services running (`python run_services.py`)
- [ ] Backend accessible (`http://localhost:8000`)
- [ ] AI backend accessible (`http://localhost:8001`)
- [ ] Frontend accessible (`http://localhost:5173`)
- [ ] Successfully logged in to application
- [ ] Chat feature working

**Congratulations! Your Vaani Banking Voice Assistant is ready to use! 🎉**
