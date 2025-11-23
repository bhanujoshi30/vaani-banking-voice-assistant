"""
Generate Round 3 hackathon submission PDF for Vaani Banking Voice Assistant.

This script compiles a professionally formatted PDF that covers:
- Technology stack
- System architecture
- Data model and storage
- AI/ML/Automation components
- Security and compliance
- Scalability and performance

Output file: documentation/Vaani_Round3_Submission.pdf

Note: To keep the PDF generation robust across environments, the script
uses ReportLab's built-in fonts and avoids special Unicode symbols
like the rupee sign. Monetary amounts are written as 'Rs.' instead of '₹'.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)


OUTPUT_PATH = Path(__file__).parent / "Vaani_Round3_Submission.pdf"


def title(text: str):
    return Paragraph(text, ParagraphStyle(name="Title", fontSize=22, leading=26, spaceAfter=14, alignment=1))


def h2(text: str):
    return Paragraph(text, ParagraphStyle(name="H2", fontSize=16, leading=20, spaceBefore=12, spaceAfter=8))


def h3(text: str):
    return Paragraph(text, ParagraphStyle(name="H3", fontSize=13, leading=17, spaceBefore=8, spaceAfter=6, textColor=colors.HexColor("#1f3b57")))


def body(text: str):
    # Standard body copy with comfortable leading
    return Paragraph(text, ParagraphStyle(name="Body", fontSize=10.5, leading=15))


def bullets(items):
    style = ParagraphStyle(name="Bullet", fontSize=10.5, leading=15)
    return ListFlowable([ListItem(Paragraph(i, style), leftIndent=10) for i in items], bulletType="bullet", start="circle")


def key_value_table(rows, col_widths=(5.0 * cm, 11.5 * cm)):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0b4f6c")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.lightgrey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.98, 0.98, 0.98)]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def build_story():
    styles = getSampleStyleSheet()
    small = ParagraphStyle(name="Small", fontSize=9, leading=13, textColor=colors.gray)

    story = []

    # Cover
    story.append(title("Vaani – Voice-First Banking Assistant"))
    story.append(Paragraph("Round 3 Submission – Technical Walkthrough", ParagraphStyle(name="SubT", fontSize=14, leading=18, alignment=1, textColor=colors.HexColor("#0b4f6c"))))
    story.append(Spacer(1, 12))
    story.append(body("Hackathon Theme: AI Voice Assistant for Financial Operations"))
    story.append(Spacer(1, 6))
    story.append(body("Date: %s" % datetime.now().strftime("%d %b %Y")))
    story.append(Spacer(1, 18))

    story.append(key_value_table([
        ["Product Vision", "Vaani brings safe, natural, and multilingual banking to Bharat through a voice-first experience that removes app complexity and builds confidence for low digital-literacy users."],
        ["Target Users", "Tier‑2/3 towns, rural India, and on-the-go mobile users who prefer speaking over navigating menus."],
        ["Core Outcomes", "Reduce support costs, improve First Contact Resolution, and convert 'account ownership' into 'active usage'."],
    ]))
    story.append(PageBreak())

    # 1. Technology Stack
    story.append(h2("1. Technology Stack"))
    story.append(h3("Frontend (Web)"))
    story.append(bullets([
        "React 19 + Vite; React Router; Axios; CSS Modules.",
        "Voice: Web Speech API for speech-to-text and text-to-speech (browser-native).",
        "Environment: VITE_BACKEND_URL (API) and VITE_AI_BACKEND_URL (AI).",
    ]))
    story.append(h3("Backend API"))
    story.append(bullets([
        "FastAPI + SQLAlchemy 2.0; Pydantic v2; JWT auth (python-jose).",
        "SQLite for dev; PostgreSQL ready for production.",
        "Voice biometrics via Resemblyzer; device binding; reminder and beneficiary services.",
    ]))
    story.append(h3("AI Backend"))
    story.append(bullets([
        "LangGraph orchestration with a Hybrid Supervisor routing intents to specialists.",
        "LLM: Ollama locally (Qwen 2.5 7B primary, Llama 3.2 3B fast); optional OpenAI.",
        "RAG: ChromaDB vector store; HuggingFace sentence-transformers (all-MiniLM-L6-v2).",
        "Observability: Structured logs; optional LangSmith tracing.",
    ]))
    story.append(Spacer(1, 6))
    story.append(key_value_table([
        ["Local Ports", "Frontend: 5173 | Backend API: 8000 | AI Backend: 8001 | Ollama: 11434"],
    ]))

    # 2. System Architecture
    story.append(Spacer(1, 12))
    story.append(h2("2. System Architecture"))
    story.append(body("Three microservices work in tandem: Frontend (SPA), Backend API (banking operations), and AI Backend (agentic orchestration). The AI service calls tools that in turn interact with the Backend API and database. Documents are ingested into ChromaDB for grounded answers."))
    story.append(Spacer(1, 6))
    story.append(h3("End-to-End Flows"))
    story.append(bullets([
        "Balance inquiry: User asks → IntentRouter → Banking Agent → tool get_account_balance → Backend API/DB → friendly reply.",
        "Loan/investment FAQs: User asks in English/Hindi → RAG Supervisor → specialist (loan/investment) → vector retrieval → answer with citations.",
        "Hello UPI payments: Wake phrase or UPI mode → UPI Agent → recipient resolution → PIN entry (manual) → initiate payment → audit trail.",
    ]))
    story.append(Spacer(1, 6))
    story.append(key_value_table([
        ["Agents", "Greeting, Banking, UPI, RAG Supervisor (Loan/Investment/Support), Feedback."],
        ["Supervisor", "Deterministic routing + shared conversation state; predictable outputs for UI and logs."],
        ["Voice", "Browser-native TTS/STT today; Azure TTS pluggable."],
    ]))

    # 3. Data Model and Storage
    story.append(PageBreak())
    story.append(h2("3. Data Model and Storage"))
    story.append(body("The application separates transactional data from knowledge data. Banking data sits in SQL; product knowledge is embedded into a vector store."))
    story.append(h3("Relational (Operational)"))
    story.append(bullets([
        "Users, Accounts, Transactions, Reminders, Beneficiaries, DeviceBindings, Sessions, Branches, Cards.",
        "SQLite for development; migrate to PostgreSQL for production (connection pooling, read replicas).",
        "Transactions carry channel (UPI/NEFT/IMPS/etc.), reference IDs, and balance-after to simplify statements.",
    ]))
    story.append(h3("Vector (Knowledge/RAG)"))
    story.append(bullets([
        "ChromaDB with four collections: loan_products, loan_products_hindi, investment_schemes, investment_schemes_hindi.",
        "Semantic chunking preserves sections, tables and FAQs; rich metadata enables precise retrieval (loan_type, scheme_type, language, section).",
        "Embeddings via sentence-transformers/all-MiniLM-L6-v2 (multilingual, CPU‑friendly).",
    ]))
    story.append(Spacer(1, 6))
    story.append(key_value_table([
        ["Statements", "Generated via transaction history; agent can return structured \"statement_data\" for UI download."],
        ["UPI Ledger", "UPI payments recorded as debit/credit pairs with a unique reference like UPI-YYYYMMDD-HHMMSS."],
    ]))

    # 4. AI/ML/Automation Components
    story.append(Spacer(1, 12))
    story.append(h2("4. AI/ML/Automation Components"))
    story.append(h3("Hybrid Supervisor & Agents"))
    story.append(bullets([
        "Supervisor builds conversation state, classifies intent, and dispatches to specialists.",
        "Banking Agent executes tool-augmented operations (balance, transactions, transfers, reminders).",
        "UPI Agent runs a guided, multi-step flow with consent and PIN verification (manual entry).",
        "RAG Supervisor routes to Loan/Investment/Support specialists for grounded answers.",
    ]))
    story.append(h3("Retrieval-Augmented Generation (RAG)"))
    story.append(bullets([
        "PDF ingestion → semantic chunking → embeddings → ChromaDB; runtime similarity search fetches precise context.",
        "Bilingual collections support English and Hindi; code-mixed queries handled via prompts + metadata filtering.",
    ]))
    story.append(h3("Automation & Observability"))
    story.append(bullets([
        "Structured logs for agent decisions and tool calls; optional LangSmith traces for deep debugging.",
        "Graceful failure messages and fallbacks to maintain user confidence.",
    ]))

    # 5. Security and Compliance
    story.append(PageBreak())
    story.append(h2("5. Security and Compliance"))
    story.append(body("Designed as compliance-by-design with Indian banking norms and RBI guardrails in mind."))
    story.append(h3("Identity & Sessions"))
    story.append(bullets([
        "JWT-based sessions with expiry; device binding (trusted/suspicious/revoked).",
        "Voice biometrics via embeddings; adaptive thresholds and AI-assisted scoring path available.",
        "Passwords hashed (bcrypt). No raw voice audio retained — only embeddings/signatures where required.",
    ]))
    story.append(h3("UPI & Payments"))
    story.append(bullets([
        "PIN is never spoken or stored; must be entered manually via secure keypad.",
        "Explicit first-time UPI consent; clear confirmation of amount, recipient, and source account before PIN.",
        "Full audit trail with reference IDs; velocity limits and anomaly detection planned for production.",
    ]))
    story.append(h3("Data Minimisation & Privacy"))
    story.append(bullets([
        "RAG accesses only relevant document chunks at query time (purpose limitation).",
        "Environment variables for secrets; strict input validation on all APIs.",
        "Production hardening: TLS everywhere, Postgres with encryption-at-rest/HSM for PIN, rate limiting and WAF.",
    ]))

    # 6. Scalability and Performance
    story.append(Spacer(1, 12))
    story.append(h2("6. Scalability and Performance"))
    story.append(h3("Horizontal scaling"))
    story.append(bullets([
        "Frontend is static and CDN-friendly.",
        "Backend API is stateless (JWT) and horizontally scalable behind a load balancer.",
        "AI Backend scales out by running multiple replicas; can switch from local Ollama to cloud LLMs.",
    ]))
    story.append(h3("Caching & Throughput"))
    story.append(bullets([
        "RAG context cache (TTL) reduces repeated retrieval costs; Redis recommended for shared cache in prod.",
        "Keep last-N messages only; use fast model for voice turn-taking; stream tokens for perceived latency gains.",
    ]))
    story.append(h3("Target SLAs (dev baselines)"))
    story.append(bullets([
        "Intent classification: 100–200 ms; standard replies: sub‑second to ~2 s; RAG answers: under ~3 s on developer hardware.",
        "UPI flow end-to-end: typically under 5 s including user confirmation and PIN entry.",
    ]))

    # Close
    story.append(PageBreak())
    story.append(h2("Annexure – Evaluation Fit"))
    story.append(body("This solution addresses Round‑1 criteria comprehensively: problem-solution fit for Bharat, core banking coverage, security-first UX, bilingual support (English/Hindi), agentic AI design with RAG, observability, and a practical pilot plan with measurable outcomes."))
    story.append(Spacer(1, 10))
    story.append(key_value_table([
        ["Pilot Scope (3 months)", "1,000 users executing Balance, Transactions, and Hello UPI payments; collect Hinglish audio to refine models."],
        ["Success Metrics", "CSAT uplift, FCR improvement, Rs. cost-to-serve reduction, task completion times, and drop-off analysis."],
    ]))
    story.append(Spacer(1, 18))
    story.append(Paragraph("Vaani – Banking that speaks your language.", ParagraphStyle(name="Footer", fontSize=11, leading=14, textColor=colors.HexColor("#0b4f6c"))))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Sun National Bank (Prototype) – For hackathon evaluation only", small))

    return story


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=2 * cm,
        title="Vaani – Round 3 Submission",
        author="Team Vaani",
    )
    doc.build(build_story())
    print(f"PDF generated at: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
