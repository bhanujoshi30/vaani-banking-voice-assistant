# Vaani Banking Voice Assistant - Documentation Hub

Welcome to the complete documentation for Vaani Banking Voice Assistant.

## 📚 Documentation Structure

### 🚀 Getting Started

**Start Here: [Setup Guide](./setup_guide.md)**
- Complete installation instructions
- Prerequisites (Python, Node.js, uv, Ollama)
- Model downloads (qwen2.5:7b, llama3.2:3b)
- Environment setup
- Running all services with `python run_services.py`

### 🏗️ Architecture

**[System Architecture](./system_architecture.md)** - Complete system overview
- Three-tier architecture (Frontend, Backend API, AI Backend)
- Data flow diagrams
- Technology stack
- Security architecture
- Deployment considerations
- Scalability and monitoring

### 📦 Module Documentation

#### Backend
**[Backend Modules](../backend_modules.md)** - Complete backend documentation
- Database models (User, Account, Transaction, DeviceBinding, Reminder, Beneficiary)
- Repositories (Data access layer)
- Services (Business logic)
- API endpoints and routes
- Authentication and security
- Voice verification services

#### AI System
**[AI Modules](../ai_modules.md)** - AI agent system documentation
- Hybrid supervisor architecture
- Multi-agent orchestration (Intent Classifier, Banking Agent, UPI Agent, RAG Agent)
- RAG System (Loan Agent, Investment Agent, Customer Support Agent)
- LangGraph workflow
- LLM services (Ollama, OpenAI)
- RAG service with ChromaDB vector databases
- Tools (Banking tools, UPI tools)
- Configuration and deployment

#### Frontend
**[Frontend Modules](../frontend_modules.md)** - Frontend components and features
- Page components (Login, Chat, Profile, Transactions, Reminders, Beneficiaries, DeviceBinding)
- Reusable components (Headers, Modals, Language selectors)
- Custom React hooks (Chat, Speech Recognition, TTS, Voice Mode)
- API clients (Backend, AI)
- State management

### 💡 Feature Documentation

#### Investment Schemes
**[Investment Schemes](./investment_schemes.md)** - Investment information system
- 7 investment schemes (PPF, NPS, SSY, ELSS, FD, RD, NSC)
- RAG-based information retrieval
- Structured investment cards
- Bilingual support (English/Hindi)
- Frontend integration
- Query examples and troubleshooting

#### Hindi Language Support
**[Hindi Support](./hindi_support.md)** - Complete Hindi implementation
- Hindi vector databases (loan + investment)
- Hindi PDF document generation
- Font management and extraction
- Bilingual RAG system
- Query examples in Hindi
- Performance and accuracy metrics

#### UPI Payments
**[UPI Payment Flow](./upi_payment_flow.md)** - Hello UPI implementation
- Complete transaction flow (wake phrase to confirmation)
- PIN verification process
- Recipient resolution
- Multi-language support
- RBI compliance
- Security features
- Testing guide

#### Voice Authentication
**[Voice Login Improvements](../docs/VOICE_LOGIN_IMPROVEMENTS.md)** - Voice biometric authentication
- AI-enhanced voice verification
- Device binding process
- Voice enrollment
- Re-binding after revocation
- Security and compliance

### 🏛️ Architecture Documentation

**System Architecture:**
- **[AI Architecture](../ai_architecture.md)** - AI system design and agent flows
- **[Backend Architecture](../backend_architecture.md)** - Backend API and database design
- **[Frontend Architecture](../frontend-architecture.md)** - Frontend component architecture
- **[Hybrid Supervisor Pattern](./hybrid_supervisor_pattern.md)** - Agent orchestration pattern

**Architecture Diagrams:**
- `system_architecture.mmd` - Complete system diagram (all 3 services)
- `ai_architecture.mmd` - AI system diagram
- `backend_architecture.mmd` - Backend structure
- `frontend_architecture.mmd` - Frontend structure
- `hybrid_supervisor_architecture.mmd` - Supervisor flow

### 📖 Additional Resources

**Original Development Documentation** (in `/docs` folder):
- [Implementation Summary](../docs/IMPLEMENTATION_SUMMARY.md) - What was built
- [Architecture Overview](../docs/ARCHITECTURE.md) - System flow diagrams
- [AI README](../docs/AI_README.md) - Detailed AI backend guide
- [UPI Flow](../docs/HELLO_UPI_FLOW.md) - UPI implementation details
- [UPI Debugging](../docs/UPI_MODE_DEBUGGING.md) - Troubleshooting UPI
- [Voice Device Binding](../docs/voice-device-binding.md) - Device binding spec

## 🎯 Quick Navigation

### For New Users
1. Start with [Setup Guide](./setup_guide.md)
2. Read [System Architecture](./system_architecture.md) for overview
3. Run the application
4. Read [Frontend Modules](../frontend_modules.md) to understand the UI
5. Try [UPI Payment Flow](./upi_payment_flow.md) for payments

### For Developers

**System Overview:**
1. [System Architecture](./system_architecture.md) - Complete system design
2. Technology stack and deployment
3. Data flow examples

**Backend Development:**
1. [Backend Modules](../backend_modules.md) - API structure
2. [Backend Architecture](../backend_architecture.md) - Design patterns
3. Database schema and models

**AI Development:**
1. [AI Modules](../ai_modules.md) - Agent system
2. [AI Architecture](../ai_architecture.md) - Design
3. [Hybrid Supervisor Pattern](./hybrid_supervisor_pattern.md) - Orchestration

**Frontend Development:**
1. [Frontend Modules](../frontend_modules.md) - Components
2. [Frontend Architecture](../frontend-architecture.md) - Structure
3. React hooks and API clients

### For Feature Understanding

**Voice Features:**
- [Voice Login](../docs/VOICE_LOGIN_IMPROVEMENTS.md)
- [Voice Device Binding](../docs/voice-device-binding.md)

**UPI Features:**
- [UPI Payment Flow](./upi_payment_flow.md)
- [Hello UPI Implementation](../docs/HELLO_UPI_FLOW.md)
- [UPI Debugging Guide](../docs/UPI_MODE_DEBUGGING.md)

## 🛠️ Technology Stack

### Frontend (Port 5173)
- React 19
- Vite
- React Router DOM
- Web Speech API

### Backend (Port 8000)
- FastAPI
- SQLAlchemy ORM
- SQLite
- Resemblyzer (voice verification)
- JWT authentication

### AI Backend (Port 8001)
- LangGraph
- Ollama (qwen2.5:7b, llama3.2:3b)
- LangSmith
- ChromaDB (vector database for RAG)
- HuggingFace embeddings (sentence-transformers/all-MiniLM-L6-v2)

## 📋 Documentation Checklist

### Completed Documentation
- ✅ Setup Guide (with RAG ingestion steps)
- ✅ Backend Modules
- ✅ AI Modules (updated with RAG agents)
- ✅ Frontend Modules
- ✅ UPI Payment Flow
- ✅ Investment Schemes Feature
- ✅ Hindi Language Support
- ✅ Architecture Diagrams
- ✅ Voice Authentication

### Legacy Documentation (Reference)
- ✅ Implementation Summary
- ✅ Architecture Overview
- ✅ AI README
- ✅ UPI Flow and Debugging
- ✅ Voice Device Binding

## 🔗 External Links

- [Ollama Documentation](https://ollama.com/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith](https://smith.langchain.com)
- [Qwen 2.5 Model](https://huggingface.co/Qwen/Qwen2.5-7B)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)

## 💬 Support

**For Issues:**
1. Check troubleshooting sections in relevant documentation
2. Review logs in `ai/logs/` and browser console
3. Consult [Setup Guide](./setup_guide.md) for common problems

**For Development:**
1. Architecture documentation for design patterns
2. Module documentation for implementation details
3. Original docs for historical context

## 🎉 Getting Started

**Ready to begin?** Start with the **[Setup Guide](./setup_guide.md)** and follow the step-by-step instructions to get Vaani running on your machine!
