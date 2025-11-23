
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

def generate_pdf():
    doc = SimpleDocTemplate("/Users/ashok/Documents/projects/vaani-banking-voice-assistant/documentation/Vaani_Round2_Submission.pdf", pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=14))
    styles.add(ParagraphStyle(name='MainTitle', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=24, leading=28, spaceAfter=20))
    styles.add(ParagraphStyle(name='CustomTitle', alignment=TA_CENTER, fontName='Helvetica', fontSize=18, leading=22, spaceAfter=20))
    styles.add(ParagraphStyle(name='SectionTitle', alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=16, leading=20, spaceBefore=15, spaceAfter=10, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='SubSectionTitle', alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=13, leading=16, spaceBefore=10, spaceAfter=6))
    
    story = []

    # Title Page
    story.append(Paragraph("Vaani: The Voice-First Bank for Bharat", styles['MainTitle']))
    story.append(Paragraph("Round 2 Technical Submission", styles['CustomTitle']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>Team Name:</b> Code Crusaders", styles['Normal']))
    story.append(Paragraph("<b>Date:</b> 23 November 2025", styles['Normal']))
    story.append(Spacer(1, 50))
    
    intro_text = """
    <b>Executive Summary</b><br/><br/>
    India stands at a unique digital crossroads. While we boast over 900 million internet subscribers, a significant "usability divide" persists. Nearly half of our rural households struggle with complex, menu-driven banking interfaces designed for the digitally savvy urban population. <b>Vaani</b> is our answer to this challenge—a voice-first banking assistant designed specifically for the next 500 million users in Bharat.<br/><br/>
    
    This document details the technical architecture of Vaani. We have moved beyond simple chatbots to create a robust, agentic AI system capable of executing secure financial transactions, understanding "Hinglish" (Hindi-English code-switching), and providing hyper-personalized financial advice using Retrieval-Augmented Generation (RAG). Our solution is not just a wrapper around an LLM; it is a fully integrated banking ecosystem built on a microservices architecture, adhering strictly to RBI's security guidelines and the DPDP Act.<br/><br/>
    
    In this submission, we walk through our technology stack, the "Hybrid Supervisor" AI architecture, our secure data models, and the compliance-first security measures that make Vaani ready for real-world deployment.
    """
    story.append(Paragraph(intro_text, styles['Justify']))
    story.append(PageBreak())

    # 1. Technology Stack
    story.append(Paragraph("1. Technology Stack", styles['SectionTitle']))
    tech_intro = """
    To build a solution that is both cutting-edge and accessible on low-end devices common in Tier-2 and Tier-3 cities, we selected a technology stack that balances performance, scalability, and developer velocity.
    """
    story.append(Paragraph(tech_intro, styles['Justify']))
    
    # Frontend
    story.append(Paragraph("1.1 Frontend: Accessibility First", styles['SubSectionTitle']))
    frontend_text = """
    The user interface is built with <b>React 19</b> and <b>Vite</b>. We chose React for its component-based architecture, allowing us to build a responsive UI that works seamlessly across mobile browsers and desktops. Crucially, we leverage the <b>Web Speech API</b> for native Speech-to-Text (STT) and Text-to-Speech (TTS). This decision eliminates the need for heavy audio file uploads to the server for every utterance, significantly reducing latency and data usage—a critical factor for users with spotty internet connections in rural India. The frontend maintains a persistent WebSocket-like connection experience using efficient polling and state management via React Context, ensuring the conversation feels natural and real-time.
    """
    story.append(Paragraph(frontend_text, styles['Justify']))

    # Backend
    story.append(Paragraph("1.2 Backend API: High Performance & Async", styles['SubSectionTitle']))
    backend_text = """
    Our core banking logic is powered by <b>FastAPI</b>. We chose FastAPI over Django or Flask because of its native support for asynchronous programming (async/await). Banking operations often involve waiting for database queries or external API calls (like UPI gateways). FastAPI handles these concurrent requests efficiently, ensuring that our server can handle thousands of simultaneous users without blocking. We use <b>SQLAlchemy 2.0</b> as our ORM, providing a robust abstraction layer over our database, allowing us to switch between SQLite (for development) and PostgreSQL (for production) with zero code changes. Pydantic v2 is used for rigorous data validation, ensuring that no malformed data ever reaches our core banking logic.
    """
    story.append(Paragraph(backend_text, styles['Justify']))

    # AI Engine
    story.append(Paragraph("1.3 AI Engine: The Brain of Vaani", styles['SubSectionTitle']))
    ai_text = """
    The intelligence layer is a separate microservice built with <b>LangGraph</b> and <b>FastAPI</b>. We moved away from simple linear chains to a graph-based agentic workflow. This allows for cyclic logic—essential for "conversational repair" (e.g., asking for a missing UPI PIN and then retrying the transaction).
    <br/><br/>
    For the LLM, we utilize <b>Ollama</b> to run models locally. We employ a dual-model strategy:
    1. <b>Llama 3.2 3B</b>: A lightweight, ultra-fast model used for intent classification and simple routing. Its low latency ensures the user feels heard immediately.
    2. <b>Qwen 2.5 7B</b>: A more powerful model used for complex reasoning, RAG synthesis, and handling multilingual "Hinglish" queries. Qwen demonstrates superior performance in understanding Indian contexts compared to standard Llama models.
    <br/><br/>
    <b>ChromaDB</b> serves as our vector store, enabling our RAG (Retrieval-Augmented Generation) pipeline to fetch accurate, up-to-date information about loan products and investment schemes without hallucinating.
    """
    story.append(Paragraph(ai_text, styles['Justify']))

    # 2. System Architecture
    story.append(Paragraph("2. System Architecture", styles['SectionTitle']))
    arch_intro = """
    Vaani follows a microservices architecture to ensure separation of concerns and independent scalability. The system is composed of three distinct layers: The Presentation Layer (Frontend), the Application Layer (Backend API), and the Intelligence Layer (AI Backend).
    """
    story.append(Paragraph(arch_intro, styles['Justify']))

    story.append(Paragraph("2.1 The Hybrid Supervisor Pattern", styles['SubSectionTitle']))
    supervisor_text = """
    At the heart of our AI architecture lies the <b>Hybrid Supervisor Pattern</b>. Unlike a standard chatbot that tries to do everything with one prompt, our system uses a specialized orchestrator.
    <br/><br/>
    When a user speaks, the <b>Intent Router</b> first analyzes the utterance. Based on the intent, the request is routed to a specialized "Agent":
    <ul>
        <li><b>Banking Agent:</b> Has access to secure tools for balance checks, transaction history, and fund transfers. It cannot answer general questions, ensuring security.</li>
        <li><b>UPI Agent:</b> A stateful agent designed specifically for the multi-step "Hello! UPI" flow (Verify Payee -> Enter PIN -> Confirm).</li>
        <li><b>RAG Supervisor:</b> Routes information queries to domain experts (Loan Agent, Investment Agent, Support Agent).</li>
    </ul>
    This modular design means we can upgrade the "Loan Agent" without risking the stability of the "Banking Agent". It is a robust, enterprise-grade approach to AI.
    """
    story.append(Paragraph(supervisor_text, styles['Justify']))

    story.append(Paragraph("2.2 Data Flow & Latency Optimization", styles['SubSectionTitle']))
    flow_text = """
    To minimize latency—a key KPI for voice interfaces—we optimized the data flow. Voice processing happens on the edge (browser). The text is sent to the AI Backend. The AI Backend communicates with the Core Banking Backend via internal high-speed APIs to fetch real-time data (e.g., account balance). The LLM then synthesizes the natural language response, which is sent back to the frontend for TTS synthesis. This "Text-in, Text-out" architecture over the network is 10x faster than streaming raw audio.
    """
    story.append(Paragraph(flow_text, styles['Justify']))

    # 3. Data Model and Storage
    story.append(Paragraph("3. Data Model and Storage", styles['SectionTitle']))
    data_intro = """
    Data integrity is paramount in banking. We employ a polyglot persistence strategy, using Relational Databases for transactional data and Vector Databases for unstructured knowledge.
    """
    story.append(Paragraph(data_intro, styles['Justify']))

    story.append(Paragraph("3.1 Relational Schema (SQL)", styles['SubSectionTitle']))
    sql_text = """
    Our primary database (SQLite for dev, Postgres for prod) manages the core banking entities. Key tables include:
    <ul>
        <li><b>Users:</b> Stores KYC details, hashed passwords, and voice profile references.</li>
        <li><b>Accounts:</b> Manages account numbers, types (Savings/Current), and real-time balances.</li>
        <li><b>Transactions:</b> An immutable ledger of all credits and debits, linked to accounts.</li>
        <li><b>DeviceBindings:</b> Implements our security layer, mapping specific device fingerprints to user accounts.</li>
        <li><b>VoiceProfiles:</b> Stores the mathematical embeddings of user voice prints (not raw audio) for biometric verification.</li>
    </ul>
    We use strict foreign key constraints and ACID transactions to ensure that money is never "lost" during a transfer.
    """
    story.append(Paragraph(sql_text, styles['Justify']))

    story.append(Paragraph("3.2 Vector Storage (ChromaDB)", styles['SubSectionTitle']))
    vector_text = """
    For our RAG system, we ingest PDF documents (Loan policies, Investment schemes) into <b>ChromaDB</b>. We maintain separate collections for English and Hindi documents:
    <ul>
        <li><code>loan_products</code> & <code>loan_products_hindi</code></li>
        <li><code>investment_schemes</code> & <code>investment_schemes_hindi</code></li>
    </ul>
    We use <b>HuggingFace embeddings</b> (<code>all-MiniLM-L6-v2</code>) to convert text into vectors. This separation ensures that when a user asks in Hindi, we search the Hindi vector space, providing culturally and linguistically accurate results rather than machine-translated approximations.
    """
    story.append(Paragraph(vector_text, styles['Justify']))

    # 4. AI/ML/Automation Components
    story.append(Paragraph("4. AI/ML & Automation Components", styles['SectionTitle']))
    ai_comp_intro = """
    Vaani is not just a wrapper; it is a sophisticated composition of multiple AI disciplines.
    """
    story.append(Paragraph(ai_comp_intro, styles['Justify']))

    story.append(Paragraph("4.1 Retrieval-Augmented Generation (RAG)", styles['SubSectionTitle']))
    rag_text = """
    Hallucinations are unacceptable in banking. If a user asks about the interest rate for a Home Loan, the AI cannot guess. Our RAG pipeline intercepts these queries. It retrieves the exact paragraph from the bank's official policy PDF stored in ChromaDB and inserts it into the LLM's context window. The system prompt strictly instructs the LLM: "Answer ONLY based on the provided context." This ensures 100% factual accuracy for product queries.
    """
    story.append(Paragraph(rag_text, styles['Justify']))

    story.append(Paragraph("4.2 Voice Biometrics (Resemblyzer)", styles['SubSectionTitle']))
    voice_text = """
    Security is our differentiator. We integrated <b>Resemblyzer</b>, a deep learning model for voice verification. During onboarding, the user speaks a passphrase. We generate a d-vector (voice embedding) and store it. For sensitive transactions, we capture the user's voice again, generate a new embedding, and calculate the cosine similarity. If the score exceeds our threshold (0.75), the transaction is authorized. This provides a seamless, password-less authentication experience that is hard to spoof.
    """
    story.append(Paragraph(voice_text, styles['Justify']))

    story.append(Paragraph("4.3 Multilingual 'Hinglish' Support", styles['SubSectionTitle']))
    hinglish_text = """
    Our target demographic often speaks "Hinglish" (e.g., "Mera account balance kya hai?"). Standard English models fail here. We utilize <b>Qwen 2.5</b>, which has shown remarkable ability to understand code-switched Indic languages. Furthermore, our RAG system is language-aware. The <code>IntentRouter</code> detects the language of the query and instructs the downstream agents to respond in the same language, maintaining a natural conversational flow.
    """
    story.append(Paragraph(hinglish_text, styles['Justify']))

    # 5. Security and Compliance
    story.append(Paragraph("5. Security and Compliance", styles['SectionTitle']))
    sec_intro = """
    Building for Bharat means building with trust. Our architecture is "Secure by Design" and aligns with RBI's Master Directions on Digital Payment Security.
    """
    story.append(Paragraph(sec_intro, styles['Justify']))

    story.append(Paragraph("5.1 Zero Trust & Device Binding", styles['SubSectionTitle']))
    zero_trust_text = """
    We implement a <b>Zero Trust</b> model. Merely having a login credential is not enough. We enforce <b>Device Binding</b>. When a user logs in, we capture the device fingerprint. Subsequent requests must originate from this trusted device. If a login attempt comes from a new device, we trigger a step-up authentication flow. This prevents remote attacks even if credentials are compromised.
    """
    story.append(Paragraph(zero_trust_text, styles['Justify']))

    story.append(Paragraph("5.2 Data Privacy (DPDP Act 2023)", styles['SubSectionTitle']))
    privacy_text = """
    In compliance with India's Digital Personal Data Protection (DPDP) Act:
    <ul>
        <li><b>Data Minimization:</b> We only fetch the data needed for the specific query. The AI context window is cleared after the session ends.</li>
        <li><b>Purpose Limitation:</b> Voice samples are used strictly for authentication and are stored as irreversible mathematical embeddings, not raw audio files.</li>
        <li><b>Local Processing:</b> By using Ollama locally, customer PII (Personally Identifiable Information) never leaves the bank's secure infrastructure to go to a public cloud LLM provider like OpenAI. This is a critical compliance feature for banking data sovereignty.</li>
    </ul>
    """
    story.append(Paragraph(privacy_text, styles['Justify']))

    # 6. Scalability and Performance
    story.append(Paragraph("6. Scalability and Performance", styles['SectionTitle']))
    scale_intro = """
    To serve millions of users, the system must be elastic and resilient.
    """
    story.append(Paragraph(scale_intro, styles['Justify']))

    story.append(Paragraph("6.1 Stateless Architecture", styles['SubSectionTitle']))
    stateless_text = """
    Both our Backend API and AI Backend are designed to be stateless. Session state is managed via JWT tokens and external databases (Redis/SQL). This allows us to horizontally scale our application servers. We can spin up 100 instances of the AI Backend behind a load balancer to handle traffic spikes during demonetization-like events or festival sales.
    """
    story.append(Paragraph(stateless_text, styles['Justify']))

    story.append(Paragraph("6.2 Caching Strategy", styles['SubSectionTitle']))
    cache_text = """
    Database hits are expensive. We implement a multi-layer caching strategy.
    1. <b>RAG Cache:</b> Frequently asked questions (e.g., "What is the interest rate for FD?") are cached. If the same query comes in, we serve the answer from the cache, bypassing the vector search and LLM generation entirely.
    2. <b>Session Cache:</b> User profiles and account metadata are cached in memory (with Redis support planned) to reduce SQL queries during an active conversation session.
    """
    story.append(Paragraph(cache_text, styles['Justify']))

    story.append(Paragraph("Conclusion", styles['SectionTitle']))
    conclusion_text = """
    Vaani is not just a hackathon prototype; it is a blueprint for the future of inclusive banking in India. By combining state-of-the-art Generative AI with rigorous banking security standards, we have created a system that is intuitive enough for a farmer in a remote village and robust enough for a national bank. We are ready to bridge the digital divide, one voice command at a time.
    """
    story.append(Paragraph(conclusion_text, styles['Justify']))

    doc.build(story)
    print("PDF generated successfully at documentation/Vaani_Round2_Submission.pdf")

if __name__ == "__main__":
    generate_pdf()
