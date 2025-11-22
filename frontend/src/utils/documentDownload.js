/**
 * Utility functions for downloading loan and investment PDF documents
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Map sub-loan types to their parent loan types (for document download)
 * Sub-loans should download the parent document
 */
const getParentLoanType = (loanType) => {
  if (!loanType) return null;
  
  const normalizedType = loanType.toUpperCase();
  
  // Map sub-loan types to parent loan types
  const subLoanToParent = {
    // Business loan sub-types -> business_loan
    'BUSINESS_LOAN_MUDRA': 'business_loan',
    'BUSINESS_LOAN_TERM': 'business_loan',
    'BUSINESS_LOAN_WORKING_CAPITAL': 'business_loan',
    'BUSINESS_LOAN_INVOICE': 'business_loan',
    'BUSINESS_LOAN_EQUIPMENT': 'business_loan',
    'BUSINESS_LOAN_OVERDRAFT': 'business_loan',
    // Home loan sub-types -> home_loan
    'HOME_LOAN_PURCHASE': 'home_loan',
    'HOME_LOAN_CONSTRUCTION': 'home_loan',
    'HOME_LOAN_PLOT_CONSTRUCTION': 'home_loan',
    'HOME_LOAN_EXTENSION': 'home_loan',
    'HOME_LOAN_RENOVATION': 'home_loan',
    'HOME_LOAN_BALANCE_TRANSFER': 'home_loan',
  };
  
  return subLoanToParent[normalizedType] || null;
};

/**
 * Map loan product names to document identifiers
 */
const mapLoanNameToDocumentId = (loanName, loanType = null) => {
  if (!loanName) return null;
  
  // If loanType is provided and it's a sub-loan type, map to parent
  if (loanType) {
    const parentLoanType = getParentLoanType(loanType);
    if (parentLoanType) {
      return parentLoanType;
    }
  }
  
  const normalizedName = loanName.toLowerCase().trim();
  
  // Direct mappings
  const mappings = {
    'home loan': 'home_loan',
    'home_loan': 'home_loan',
    'personal loan': 'personal_loan',
    'personal_loan': 'personal_loan',
    'auto loan': 'auto_loan',
    'auto_loan': 'auto_loan',
    'education loan': 'education_loan',
    'education_loan': 'education_loan',
    'business loan': 'business_loan',
    'business_loan': 'business_loan',
    'gold loan': 'gold_loan',
    'gold_loan': 'gold_loan',
    'loan against property': 'loan_against_property',
    'loan_against_property': 'loan_against_property',
    'property loan': 'loan_against_property',
    'lap': 'loan_against_property',
    // Sub-loan types -> parent documents
    'mudra loan': 'business_loan',
    'mudra': 'business_loan',
    'term loan': 'business_loan',
    'working capital': 'business_loan',
    'working capital loan': 'business_loan',
    'invoice financing': 'business_loan',
    'equipment financing': 'business_loan',
    'business overdraft': 'business_loan',
    'home purchase loan': 'home_loan',
    'home construction loan': 'home_loan',
    'plot construction loan': 'home_loan',
    'home extension loan': 'home_loan',
    'home renovation loan': 'home_loan',
    'balance transfer loan': 'home_loan',
    // Hindi names
    'होम लोन': 'home_loan',
    'होमलोन': 'home_loan',
    'पर्सनल लोन': 'personal_loan',
    'पर्सनललोन': 'personal_loan',
    'ऑटो लोन': 'auto_loan',
    'अटो लोन': 'auto_loan', // Variant spelling
    'ऑटोलोन': 'auto_loan',
    'अटोलोन': 'auto_loan', // Variant spelling
    'एजुकेशन लोन': 'education_loan',
    'एजुकेशनलोन': 'education_loan',
    'बिजनेस लोन': 'business_loan',
    'बिजनेसलोन': 'business_loan',
    'गोल्ड लोन': 'gold_loan',
    'गोल्डलोन': 'gold_loan',
    'प्रॉपर्टी के खिलाफ लोन': 'loan_against_property',
    'प्रॉपर्टी लोन': 'loan_against_property',
    // Hindi sub-loan types -> parent documents
    'मुद्रा लोन': 'business_loan',
    'मुद्रा': 'business_loan',
    'टर्म लोन': 'business_loan',
    'वर्किंग कैपिटल': 'business_loan',
    'वर्किंग कैपिटल लोन': 'business_loan',
    'इनवॉइस फाइनेंसिंग': 'business_loan',
    'इक्विपमेंट फाइनेंसिंग': 'business_loan',
    'बिजनेस ओवरड्राफ्ट': 'business_loan',
  };
  
  // Check direct match
  if (mappings[normalizedName]) {
    return mappings[normalizedName];
  }
  
  // Check partial matches
  for (const [key, value] of Object.entries(mappings)) {
    if (normalizedName.includes(key) || key.includes(normalizedName)) {
      return value;
    }
  }
  
  // Try to extract from name (e.g., "Home Loan" -> "home_loan")
  const words = normalizedName.split(/\s+/);
  if (words.length >= 2) {
    const key = words.join('_');
    if (mappings[key]) {
      return mappings[key];
    }
  }
  
  return null;
};

/**
 * Map investment scheme names to document identifiers
 */
const mapInvestmentNameToDocumentId = (investmentName) => {
  if (!investmentName) return null;
  
  const normalizedName = investmentName.toLowerCase().trim();
  
  const mappings = {
    'ppf': 'ppf',
    'public provident fund': 'ppf',
    'nps': 'nps',
    'national pension system': 'nps',
    'national pension': 'nps',
    'ssy': 'ssy',
    'sukanya samriddhi yojana': 'ssy',
    'sukanya': 'ssy',
    'sukanya samriddhi': 'ssy',
    // Hindi names
    'पीपीएफ': 'ppf',
    'एनपीएस': 'nps',
    'सुकन्या समृद्धि योजना': 'ssy',
    'सुकन्या': 'ssy',
    'सुकन्या समृद्धि': 'ssy',
    'ईएलएसएस': 'elss',
    'elss': 'elss',
    'फिक्स्ड डिपॉजिट': 'fd',
    'fd': 'fd',
    'fixed deposit': 'fd',
    'रिकरिंग डिपॉजिट': 'rd',
    'rd': 'rd',
    'recurring deposit': 'rd',
    'नेशनल सेविंग्स सर्टिफिकेट': 'nsc',
    'nsc': 'nsc',
    'national savings certificate': 'nsc',
  };
  
  // Check direct match
  if (mappings[normalizedName]) {
    return mappings[normalizedName];
  }
  
  // Check partial matches
  for (const [key, value] of Object.entries(mappings)) {
    if (normalizedName.includes(key) || key.includes(normalizedName)) {
      return value;
    }
  }
  
  return null;
};

/**
 * Download a PDF document
 * @param {string} documentType - 'loan' or 'investment'
 * @param {string} documentName - Product/scheme name
 * @param {string} language - Language code (en-IN or hi-IN)
 * @param {string} accessToken - Authentication token (optional, for protected endpoints)
 * @param {string} loanType - Optional loan type (e.g., 'BUSINESS_LOAN_MUDRA') for sub-loans
 */
export const downloadDocument = async (documentType, documentName, language = 'en-IN', accessToken = null, loanType = null) => {
  try {
    // Map the name to document ID
    let documentId;
    if (documentType === 'loan') {
      documentId = mapLoanNameToDocumentId(documentName, loanType);
    } else if (documentType === 'investment') {
      documentId = mapInvestmentNameToDocumentId(documentName);
    } else {
      throw new Error(`Invalid document type: ${documentType}`);
    }
    
    if (!documentId) {
      throw new Error(`Could not map document name "${documentName}" to a document ID`);
    }
    
    // Build the download URL
    const url = `${API_BASE_URL}/api/v1/documents/${documentType}/${documentId}?language=${language}`;
    
    // Create headers
    const headers = {};
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    // Fetch the PDF
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail?.error?.message || `Failed to download document: ${response.statusText}`);
    }
    
    // Get the blob
    const blob = await response.blob();
    
    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `${documentId}_guide.pdf`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    // Create download link and trigger download
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
    
    return { success: true, filename };
  } catch (error) {
    console.error('Error downloading document:', error);
    throw error;
  }
};

export { mapLoanNameToDocumentId, mapInvestmentNameToDocumentId };

