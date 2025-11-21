# Investment Schemes RAG System Implementation Guide

## Overview
This document describes the complete implementation of the Investment Schemes RAG system, mirroring the loan products system architecture.

## System Architecture

### 1. PDF Generation (`backend/documents/create_investment_scheme_docs.py`)
- **Status**: ✅ Created
- **Schemes Covered**: PPF, NPS, SSY (with structure for ELSS, FD, RD, NSC)
- **Features**:
  - Comprehensive scheme details
  - Interest rates, tax benefits, eligibility
  - Withdrawal rules and maturity calculations
  - FAQs and important notes

### 2. Frontend Components

#### InvestmentInfoCard (`frontend/src/components/Chat/InvestmentInfoCard.jsx`)
- **Status**: ✅ Created
- **Features**:
  - Displays investment scheme information
  - Shows interest rate, investment amount, tenure
  - Tax benefits section
  - Features list
  - Supports Hindi and English

#### InvestmentSelectionTable (`frontend/src/components/Chat/InvestmentSelectionTable.jsx`)
- **Status**: ✅ Created
- **Features**:
  - Displays all available investment schemes
  - Clickable/voice-selectable rows
  - Hindi and English support
  - Icons for each scheme

### 3. RAG Service Updates Needed

Update `ai/services/rag_service.py` to support investment documents:

```python
# Add method to load investment documents
def load_investment_documents(self) -> List[Document]:
    """Load investment scheme PDFs"""
    investment_path = self.documents_path.parent / "investment_schemes"
    documents = []
    pdf_files = list(investment_path.glob("*.pdf"))
    
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = pdf_path.name
                doc.metadata["scheme_type"] = pdf_path.stem.replace("_scheme_guide", "")
            documents.extend(docs)
        except Exception as e:
            logger.error("pdf_load_error", file=pdf_path.name, error=str(e))
    
    return documents
```

### 4. FAQ Agent Updates Needed

Add investment query detection and handling in `ai/agents/faq_agent.py`:

```python
# Add investment keywords
investment_keywords = [
    "investment", "invest", "scheme", "ppf", "nps", "ssy", "elss",
    "fixed deposit", "fd", "recurring deposit", "rd", "nsc",
    "tax saving", "retirement", "pension", "savings"
]

# Add general investment queries
general_investment_queries = [
    "what investments", "investment schemes", "investment options",
    "tax saving schemes", "retirement plans", "savings schemes"
]

# Add investment type detection
investment_types = {
    "ppf": "ppf",
    "public provident fund": "ppf",
    "nps": "nps",
    "national pension": "nps",
    "ssy": "ssy",
    "sukanya": "ssy",
    "elss": "elss",
    "tax saving mutual fund": "elss",
    "fixed deposit": "fd",
    "fd": "fd",
    "recurring deposit": "rd",
    "rd": "rd",
    "nsc": "nsc",
    "national savings certificate": "nsc"
}
```

### 5. ChatMessage Integration

Update `frontend/src/components/Chat/ChatMessage.jsx`:

```javascript
import InvestmentInfoCard from "./InvestmentInfoCard.jsx";
import InvestmentSelectionTable from "./InvestmentSelectionTable.jsx";

// Add in structured data rendering:
{message.structuredData.type === 'investment' && message.structuredData.investmentInfo && (
  <InvestmentInfoCard 
    investmentInfo={message.structuredData.investmentInfo} 
    language={language}
  />
)}

{message.structuredData.type === 'investment_selection' && message.structuredData.investments && (
  <InvestmentSelectionTable 
    investments={message.structuredData.investments} 
    language={language}
    onInvestmentSelect={(investmentType) => {
      if (onSendMessage) {
        const query = language === 'hi-IN' 
          ? `${investmentType.replace(/_/g, ' ')} के बारे में बताएं`
          : `Tell me about ${investmentType.replace(/_/g, ' ')}`;
        onSendMessage(query);
      }
    }}
  />
)}
```

## Quick Actions

Add quick actions for investments in the chat interface:

```javascript
const investmentQuickActions = [
  {
    label: language === 'hi-IN' ? 'निवेश योजनाएं देखें' : 'View Investment Schemes',
    action: () => sendMessage('What investment schemes do you offer?')
  },
  {
    label: language === 'hi-IN' ? 'PPF के बारे में' : 'About PPF',
    action: () => sendMessage('Tell me about PPF')
  },
  {
    label: language === 'hi-IN' ? 'NPS के बारे में' : 'About NPS',
    action: () => sendMessage('Tell me about NPS')
  }
];
```

## Implementation Steps

1. ✅ Create PDF generation script
2. ✅ Create frontend components
3. ⏳ Update RAG service to load investment documents
4. ⏳ Update FAQ agent to handle investment queries
5. ⏳ Update ChatMessage to render investment cards
6. ⏳ Add quick actions
7. ⏳ Generate PDFs: `python backend/documents/create_investment_scheme_docs.py`
8. ⏳ Ingest documents: Update `ai/ingest_documents.py` to include investments

## Investment Schemes Details

### PPF (Public Provident Fund)
- Interest Rate: 7.1% p.a.
- Investment: Rs. 500 - Rs. 1.5 lakhs/year
- Tenure: 15 years
- Tax Benefits: Section 80C (up to Rs. 1.5L), tax-free interest

### NPS (National Pension System)
- Returns: Market-linked (8-12% typically)
- Investment: Rs. 500 minimum, no maximum
- Tax Benefits: 80C (Rs. 1.5L) + 80CCD(1B) (Rs. 50K)
- Withdrawal: 60% at 60 years, 40% annuity

### SSY (Sukanya Samriddhi Yojana)
- Interest Rate: 8.2% p.a.
- Investment: Rs. 250 - Rs. 1.5 lakhs/year
- Tenure: 21 years
- Eligibility: Girl child below 10 years

## Testing Checklist

- [ ] PDFs generated successfully
- [ ] Investment selection table displays correctly
- [ ] Investment cards show all details
- [ ] Voice commands work for investment queries
- [ ] Quick actions trigger correct queries
- [ ] Hindi translations work correctly
- [ ] RAG retrieval returns relevant investment information

## Next Steps

1. Complete PDF generation for remaining schemes (ELSS, FD, RD, NSC)
2. Update RAG service initialization
3. Test end-to-end flow
4. Add more investment schemes as needed

