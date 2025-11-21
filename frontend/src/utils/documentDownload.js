/**
 * Utility functions for downloading loan and investment PDF documents
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Map loan product names to document identifiers
 */
const mapLoanNameToDocumentId = (loanName) => {
  if (!loanName) return null;
  
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
    // Hindi names
    'होम लोन': 'home_loan',
    'पर्सनल लोन': 'personal_loan',
    'ऑटो लोन': 'auto_loan',
    'एजुकेशन लोन': 'education_loan',
    'बिजनेस लोन': 'business_loan',
    'गोल्ड लोन': 'gold_loan',
    'प्रॉपर्टी के खिलाफ लोन': 'loan_against_property',
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
 */
export const downloadDocument = async (documentType, documentName, language = 'en-IN', accessToken = null) => {
  try {
    // Map the name to document ID
    let documentId;
    if (documentType === 'loan') {
      documentId = mapLoanNameToDocumentId(documentName);
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

