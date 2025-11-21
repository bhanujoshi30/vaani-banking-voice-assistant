/**
 * Vocabulary Configuration for Voice Recognition
 * 
 * This file contains custom vocabulary mappings and accent variations
 * to improve speech recognition accuracy, especially for UPI commands.
 * 
 * The normalization layer will map common misrecognitions to correct terms.
 */

/**
 * UPI-specific vocabulary mappings
 * Maps common misrecognitions or accent variations to correct UPI terms
 */
export const UPI_VOCABULARY = {
  'en-IN': {
    // Wake-up phrases
    'hello vanni': 'hello vaani',
    'hello vany': 'hello vaani',
    'hello vani': 'hello vaani',
    'hello vany': 'hello vaani',
    'hello vanni': 'hello vaani',
    'hello vane': 'hello vaani',
    'hello vane': 'hello vaani',
    'hey vanni': 'hey vaani',
    'hey vany': 'hey vaani',
    'hey vani': 'hey vaani',
    
    // UPI terms
    'you pee': 'upi',
    'you p i': 'upi',
    'you pie': 'upi',
    'you pay': 'upi',
    'y u p i': 'upi',
    'you pee eye': 'upi',
    'you p': 'upi',
    
    // Payment terms
    'pay': 'pay',
    'pays': 'pay',
    'paid': 'pay',
    'sends': 'send',
    'sending': 'send',
    'transfer': 'transfer',
    'transfers': 'transfer',
    'transferring': 'transfer',
    
    // Amount terms
    'rupees': 'rupees',
    'rupee': 'rupees',
    'rs': 'rupees',
    'r s': 'rupees',
    'rs.': 'rupees',
    'r s dot': 'rupees',
    'rupe': 'rupees',
    'rupes': 'rupees',
    'hundred': 'hundred',
    'hundreds': 'hundred',
    'hundrad': 'hundred',
    'hundrads': 'hundred',
    'thousand': 'thousand',
    'thousands': 'thousand',
    'thousend': 'thousand',
    'thousends': 'thousand',
    'lakh': 'lakh',
    'lakhs': 'lakh',
    'lac': 'lakh',
    'lacs': 'lakh',
    'lak': 'lakh',
    'laks': 'lakh',
    
    // Beneficiary terms
    'beneficiary': 'beneficiary',
    'beneficiaries': 'beneficiary',
    'beneficiary': 'beneficiary',
    'first': 'first',
    'first one': 'first',
    'first account': 'first',
    'last': 'last',
    'last one': 'last',
    'last account': 'last',
    
    // Account terms
    'account': 'account',
    'accounts': 'account',
    'acount': 'account',
    'acounts': 'account',
    'accont': 'account',
    'acconts': 'account',
    'balance': 'balance',
    'balances': 'balance',
    'balans': 'balance',
    'balanse': 'balance',
    'balence': 'balance',
    'balens': 'balance',
    
    // Common UPI payment phrases
    'send money': 'send money',
    'send money to': 'send money to',
    'transfer money': 'transfer money',
    'transfer money to': 'transfer money to',
    'pay money': 'pay money',
    'pay money to': 'pay money to',
    'via you pee': 'via upi',
    'via you p i': 'via upi',
    'via you pie': 'via upi',
    'via you pay': 'via upi',
    'using you pee': 'using upi',
    'using you p i': 'using upi',
    'through you pee': 'through upi',
    'through you p i': 'through upi',
    
    // Confirmation words
    'yes': 'yes',
    'yeah': 'yes',
    'yep': 'yes',
    'yup': 'yes',
    'ok': 'ok',
    'okay': 'ok',
    'okey': 'ok',
    'sure': 'sure',
    'confirm': 'confirm',
    'proceed': 'proceed',
    'go ahead': 'go ahead',
  },
  
  'hi-IN': {
    // Wake-up phrases (Hindi)
    'हेलो वानी': 'हेलो वाणी',
    'हेलो वानि': 'हेलो वाणी',
    'हेलो वान्नी': 'हेलो वाणी',
    'हेलो वानि': 'हेलो वाणी',
    'हेलो वानी': 'हेलो वाणी',
    
    // UPI terms (Hindi)
    'यू पी आई': 'यूपीआई',
    'यू पी आय': 'यूपीआई',
    'यू पी आय': 'यूपीआई',
    'यू पी आई': 'यूपीआई',
    'यूपी': 'यूपीआई',
    'यू पी': 'यूपीआई',
    
    // Payment terms (Hindi)
    'भेजना': 'भेजें',
    'भेजने': 'भेजें',
    'भुगतान करना': 'भुगतान',
    'भुगतान करें': 'भुगतान',
    'ट्रांसफर करना': 'ट्रांसफर',
    'ट्रांसफर करें': 'ट्रांसफर',
    
    // Amount terms (Hindi)
    'रुपये': 'रुपये',
    'रुपया': 'रुपये',
    'रुपैये': 'रुपये',
    'रुपैया': 'रुपये',
    'सौ': 'सौ',
    'हज़ार': 'हज़ार',
    'हजार': 'हज़ार',
    'लाख': 'लाख',
    'लाक': 'लाख',
    
    // Beneficiary terms (Hindi)
    'लाभार्थी': 'लाभार्थी',
    'पहला': 'पहला',
    'पहली': 'पहला',
    'पहले': 'पहला',
    'आखिरी': 'आखिरी',
    'आखिर': 'आखिरी',
    'दूसरा': 'दूसरा',
    'दूसरी': 'दूसरा',
    
    // Account terms (Hindi)
    'खाता': 'खाता',
    'खाते': 'खाता',
    'खातों': 'खाता',
    'बैलेंस': 'बैलेंस',
    'बैलेन्स': 'बैलेंस',
    'बैलान्स': 'बैलेंस',
    'शेष': 'शेष',
    'शेष राशि': 'शेष राशि',
    'बकाया': 'बकाया',
    'बकाया राशि': 'बकाया राशि',
    
    // Confirmation words (Hindi)
    'हाँ': 'हाँ',
    'हां': 'हाँ',
    'जी': 'जी',
    'जी हाँ': 'जी हाँ',
    'ठीक': 'ठीक',
    'ठीक है': 'ठीक है',
    'सही': 'सही',
    'सही है': 'सही है',
  },
};

/**
 * Accent-specific normalization patterns
 * These patterns help normalize common accent variations
 */
export const ACCENT_PATTERNS = {
  'en-IN': [
    // Indian English accent variations
    { pattern: /\b(you\s+pee|you\s+p\s+i|you\s+pie|you\s+pay)\b/gi, replacement: 'upi' },
    { pattern: /\b(hello\s+vanni|hello\s+vany|hello\s+vani|hello\s+vane)\b/gi, replacement: 'hello vaani' },
    { pattern: /\b(hey\s+vanni|hey\s+vany|hey\s+vani)\b/gi, replacement: 'hey vaani' },
    { pattern: /\b(acount|acounts)\b/gi, replacement: 'account' },
    { pattern: /\b(balans|balanse)\b/gi, replacement: 'balance' },
    { pattern: /\b(r\s+s|r\s+s\s+dot)\b/gi, replacement: 'rupees' },
    { pattern: /\b(hundreds)\b/gi, replacement: 'hundred' },
    { pattern: /\b(thousands)\b/gi, replacement: 'thousand' },
    { pattern: /\b(lac|lacs)\b/gi, replacement: 'lakh' },
    { pattern: /\b(yeah|yep|yup)\b/gi, replacement: 'yes' },
    { pattern: /\b(okey)\b/gi, replacement: 'ok' },
  ],
  
  'hi-IN': [
    // Hindi accent variations
    { pattern: /हेलो\s+वानी/gi, replacement: 'हेलो वाणी' },
    { pattern: /हेलो\s+वानि/gi, replacement: 'हेलो वाणी' },
    { pattern: /हेलो\s+वान्नी/gi, replacement: 'हेलो वाणी' },
    { pattern: /यू\s+पी\s+आई/gi, replacement: 'यूपीआई' },
    { pattern: /यू\s+पी\s+आय/gi, replacement: 'यूपीआई' },
    { pattern: /यूपी/gi, replacement: 'यूपीआई' },
    { pattern: /रुपैये/gi, replacement: 'रुपये' },
    { pattern: /रुपैया/gi, replacement: 'रुपये' },
    { pattern: /हजार/gi, replacement: 'हज़ार' },
    { pattern: /लाक/gi, replacement: 'लाख' },
    { pattern: /हां/gi, replacement: 'हाँ' },
  ],
};

/**
 * Common UPI phrases that should be recognized
 * These are complete phrases that users might say
 */
export const UPI_PHRASES = {
  'en-IN': [
    'hello vaani',
    'hello upi',
    'hey vaani',
    'hey upi',
    'send money',
    'transfer money',
    'pay money',
    'via upi',
    'upi payment',
    'upi balance',
    'balance check',
    'first beneficiary',
    'last beneficiary',
    'account balance',
  ],
  
  'hi-IN': [
    'हेलो वाणी',
    'हेलो यूपीआई',
    'भेजें',
    'भुगतान',
    'ट्रांसफर',
    'यूपीआई भुगतान',
    'यूपीआई बैलेंस',
    'बैलेंस चेक',
    'पहला लाभार्थी',
    'आखिरी लाभार्थी',
    'खाता बैलेंस',
  ],
};

/**
 * Get vocabulary mappings for a specific language
 * @param {string} languageCode - Language code (e.g., 'en-IN', 'hi-IN')
 * @returns {Object} Vocabulary mappings object
 */
export const getVocabularyForLanguage = (languageCode) => {
  return UPI_VOCABULARY[languageCode] || {};
};

/**
 * Get accent patterns for a specific language
 * @param {string} languageCode - Language code (e.g., 'en-IN', 'hi-IN')
 * @returns {Array} Array of accent pattern objects
 */
export const getAccentPatternsForLanguage = (languageCode) => {
  return ACCENT_PATTERNS[languageCode] || [];
};

/**
 * Get UPI phrases for a specific language
 * @param {string} languageCode - Language code (e.g., 'en-IN', 'hi-IN')
 * @returns {Array} Array of UPI phrases
 */
export const getUPIPhrasesForLanguage = (languageCode) => {
  return UPI_PHRASES[languageCode] || [];
};

/**
 * TTS Pronunciation Normalization
 * Converts technical terms to TTS-friendly pronunciations
 * @param {string} text - Text to normalize for TTS
 * @param {string} languageCode - Language code (e.g., 'en-IN', 'hi-IN')
 * @returns {string} Text normalized for TTS pronunciation
 */
export const normalizeForTTS = (text, languageCode = 'en-IN') => {
  if (!text || !text.trim()) {
    return text;
  }
  
  let normalized = text;
  
  // For Hindi language, convert English numbers to Hindi words for proper pronunciation
  if (languageCode === 'hi-IN') {
    // Convert percentages to Hindi words for proper pronunciation
    // "11.00%" → "ग्यारह प्रतिशत" (simplified)
    // "11.50%" → "ग्यारह दशमलव पचास प्रतिशत"
    normalized = normalized.replace(/(\d+\.?\d*)\s*%/g, (match, num) => {
      const numStr = num.toString();
      const parts = numStr.split('.');
      let result = '';
      
      // Hindi number words
      const hindiNumbers = {
        '0': 'शून्य', '1': 'एक', '2': 'दो', '3': 'तीन', '4': 'चार',
        '5': 'पाँच', '6': 'छह', '7': 'सात', '8': 'आठ', '9': 'नौ',
        '10': 'दस', '11': 'ग्यारह', '12': 'बारह', '13': 'तेरह', '14': 'चौदह',
        '15': 'पंद्रह', '16': 'सोलह', '17': 'सत्रह', '18': 'अठारह', '19': 'उन्नीस',
        '20': 'बीस', '25': 'पच्चीस', '30': 'तीस', '50': 'पचास', '60': 'साठ'
      };
      
      // Convert integer part
      if (parts[0]) {
        const intPart = parseInt(parts[0]);
        if (hindiNumbers[intPart]) {
          result += hindiNumbers[intPart];
        } else {
          // For larger numbers, convert digit by digit
          result += parts[0].split('').map(d => hindiNumbers[d] || d).join(' ');
        }
      }
      
      // Convert decimal part only if it's not all zeros
      if (parts[1] && parts[1] !== '00' && parts[1] !== '0') {
        // Remove trailing zeros
        const decimalPart = parts[1].replace(/0+$/, '');
        if (decimalPart.length > 0) {
          result += ' दशमलव ';
          result += decimalPart.split('').map(d => hindiNumbers[d] || d).join(' ');
        }
      }
      
      return result + ' प्रतिशत';
    });
    
    // Convert "Rs." to "रुपये" for Hindi (do this before number conversion)
    normalized = normalized.replace(/\bRs\.\s*/gi, 'रुपये ');
    
    // Convert numbers before Hindi words (लाख, करोड़) to Hindi words
    // Use a more flexible pattern that works with Devanagari characters
    normalized = normalized.replace(/(\d+)\s+(लाख|करोड़)/g, (match, num, unit) => {
      const numStr = num.toString();
      const hindiNumbers = {
        '0': 'शून्य', '1': 'एक', '2': 'दो', '3': 'तीन', '4': 'चार',
        '5': 'पाँच', '6': 'छह', '7': 'सात', '8': 'आठ', '9': 'नौ'
      };
      const numWords = numStr.split('').map(d => hindiNumbers[d] || d).join(' ');
      return numWords + ' ' + unit;
    });
    
    // Also convert numbers before English words (lakhs, crores) if they appear
    normalized = normalized.replace(/\b(\d+)\s+(lakh|lakhs|crore|crores)\b/gi, (match, num, unit) => {
      const numStr = num.toString();
      const hindiNumbers = {
        '0': 'शून्य', '1': 'एक', '2': 'दो', '3': 'तीन', '4': 'चार',
        '5': 'पाँच', '6': 'छह', '7': 'सात', '8': 'आठ', '9': 'नौ'
      };
      const numWords = numStr.split('').map(d => hindiNumbers[d] || d).join(' ');
      const unitWord = (unit.toLowerCase() === 'lakh' || unit.toLowerCase() === 'lakhs') ? 'लाख' : 'करोड़';
      return numWords + ' ' + unitWord;
    });
    
    // UPI pronunciation fixes - convert to letter-by-letter pronunciation
    normalized = normalized.replace(/\bUPI ID\b/gi, 'U P I I D');
    normalized = normalized.replace(/\bUPI\b/gi, 'U P I');
    
    // Other banking/technical terms
    normalized = normalized.replace(/\bOTP\b/gi, 'O T P');
    normalized = normalized.replace(/\bATM\b/gi, 'A T M');
    normalized = normalized.replace(/\bNEFT\b/gi, 'N E F T');
    normalized = normalized.replace(/\bRTGS\b/gi, 'R T G S');
    normalized = normalized.replace(/\bIMPS\b/gi, 'I M P S');
    normalized = normalized.replace(/\bIFSC\b/gi, 'I F S C');
    
    // Clean up multiple spaces
    normalized = normalized.replace(/\s+/g, ' ').trim();
    
    return normalized;
  }
  
  // For English language, ensure proper pronunciation of numbers and Indian currency terms
  if (languageCode === 'en-IN') {
    // Remove any Hindi text that might have been included (Devanagari script) FIRST
    // This regex matches Devanagari characters (Unicode range: \u0900-\u097F)
    normalized = normalized.replace(/[\u0900-\u097F]+/g, '');
    
    // Convert Hindi numerals (०-९) to English (0-9) BEFORE other processing
    normalized = normalized.replace(/[०-९]/g, (match) => {
      const hindiToEnglish = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
      };
      return hindiToEnglish[match] || match;
    });
    
    // Replace Hindi words with English equivalents
    const hindiToEnglish = {
      'प्रति वर्ष': 'per annum',
      'प्रति': 'per',
      'लाख': 'lakhs',
      'करोड़': 'crores',
      'वर्ष': 'years',
      'महीने': 'months',
    };
    
    for (const [hindi, english] of Object.entries(hindiToEnglish)) {
      normalized = normalized.replace(new RegExp(hindi.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), english);
    }
    
    // Ensure "lakhs" is pronounced as "lakhs" (not Hindi pronunciation)
    normalized = normalized.replace(/\b(lakh|lakhs)\b/gi, 'lakhs');
    
    // Ensure "crores" is pronounced as "crores" (not Hindi pronunciation)
    normalized = normalized.replace(/\b(crore|crores)\b/gi, 'crores');
    
    // Ensure percentages are spoken correctly - convert to words for better pronunciation
    // "9.50%" → "nine point five zero percent" for clearer pronunciation
    // But we'll keep numbers as-is and just add "percent" word
    normalized = normalized.replace(/(\d+\.?\d*)\s*%/g, (match, num) => {
      // Convert number to words for better pronunciation
      const numStr = num.toString();
      // Split by decimal point
      const parts = numStr.split('.');
      let result = '';
      
      // Convert integer part
      if (parts[0]) {
        result += parts[0].split('').map(d => {
          const digits = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'];
          return digits[parseInt(d)] || d;
        }).join(' ');
      }
      
      // Convert decimal part
      if (parts[1]) {
        result += ' point ';
        result += parts[1].split('').map(d => {
          const digits = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'];
          return digits[parseInt(d)] || d;
        }).join(' ');
      }
      
      return result + ' percent';
    });
    
    // Ensure "Rs." is pronounced as "rupees" not "R S"
    normalized = normalized.replace(/\bRs\.\s*/gi, 'rupees ');
    
    // Convert numbers before "lakhs" or "crores" to words for better pronunciation
    normalized = normalized.replace(/\b(\d+)\s+(lakh|lakhs|crore|crores)\b/gi, (match, num, unit) => {
      // Convert number to words
      const numStr = num.toString();
      const digits = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'];
      const numWords = numStr.split('').map(d => digits[parseInt(d)] || d).join(' ');
      const unitWord = (unit.toLowerCase() === 'lakh' || unit.toLowerCase() === 'lakhs') ? 'lakhs' : 'crores';
      return numWords + ' ' + unitWord;
    });
    
    // Also handle numbers with commas (e.g., "5,00,000")
    normalized = normalized.replace(/\b(\d{1,2}(?:,\d{2})*)\s*(lakh|lakhs|crore|crores)\b/gi, (match, num, unit) => {
      // Remove commas and convert
      const numStr = num.replace(/,/g, '');
      const digits = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'];
      const numWords = numStr.split('').map(d => digits[parseInt(d)] || d).join(' ');
      const unitWord = (unit.toLowerCase() === 'lakh' || unit.toLowerCase() === 'lakhs') ? 'lakhs' : 'crores';
      return numWords + ' ' + unitWord;
    });
  }
  
  // UPI pronunciation fixes - convert to letter-by-letter pronunciation
  // IMPORTANT: Handle "UPI ID" first before standalone "UPI" to avoid double conversion
  // "UPI ID" → "U P I I D" (pronounced as individual letters)
  normalized = normalized.replace(/\bUPI ID\b/gi, 'U P I I D');
  
  // Then handle standalone "UPI" → "U P I" (pronounced as individual letters)
  // Handle "UPI" as standalone word or in phrases like "UPI payment", "UPI balance"
  // Use word boundary to avoid matching "UPI" inside "UPI ID" (already converted above)
  normalized = normalized.replace(/\bUPI\b/gi, 'U P I');
  
  // Handle "UPI payment" → "U P I payment" (already handled by above)
  // Handle "UPI balance" → "U P I balance" (already handled by above)
  
  // Other banking/technical terms that might need pronunciation fixes
  // "PIN" → "P I N" (if needed, but PIN is usually fine)
  // "OTP" → "O T P" (if needed)
  normalized = normalized.replace(/\bOTP\b/gi, 'O T P');
  
  // "ATM" → "A T M" (if needed)
  normalized = normalized.replace(/\bATM\b/gi, 'A T M');
  
  // "NEFT" → "N E F T" (if needed)
  normalized = normalized.replace(/\bNEFT\b/gi, 'N E F T');
  
  // "RTGS" → "R T G S" (if needed)
  normalized = normalized.replace(/\bRTGS\b/gi, 'R T G S');
  
  // "IMPS" → "I M P S" (if needed)
  normalized = normalized.replace(/\bIMPS\b/gi, 'I M P S');
  
  // "IFSC" → "I F S C" (if needed)
  normalized = normalized.replace(/\bIFSC\b/gi, 'I F S C');
  
  // Clean up multiple spaces that might have been created
  normalized = normalized.replace(/\s+/g, ' ').trim();
  
  return normalized;
};

/**
 * Normalize transcript using vocabulary mappings and accent patterns
 * @param {string} transcript - Raw transcript from speech recognition
 * @param {string} languageCode - Language code (e.g., 'en-IN', 'hi-IN')
 * @returns {string} Normalized transcript
 */
export const normalizeTranscript = (transcript, languageCode = 'en-IN') => {
  if (!transcript || !transcript.trim()) {
    return transcript;
  }
  
  let normalized = transcript.trim();
  
  // Apply accent patterns first (regex-based replacements)
  const accentPatterns = getAccentPatternsForLanguage(languageCode);
  for (const { pattern, replacement } of accentPatterns) {
    normalized = normalized.replace(pattern, replacement);
  }
  
  // Apply vocabulary mappings (exact word/phrase replacements)
  const vocabulary = getVocabularyForLanguage(languageCode);
  const words = normalized.split(/\s+/);
  const normalizedWords = words.map(word => {
    const lowerWord = word.toLowerCase();
    // Check for exact match
    if (vocabulary[lowerWord]) {
      return vocabulary[lowerWord];
    }
    // Check for match preserving case
    const originalCase = word[0] === word[0].toUpperCase() ? 'capitalize' : 'lowercase';
    if (vocabulary[lowerWord]) {
      return originalCase === 'capitalize' 
        ? vocabulary[lowerWord].charAt(0).toUpperCase() + vocabulary[lowerWord].slice(1)
        : vocabulary[lowerWord];
    }
    return word;
  });
  
  normalized = normalizedWords.join(' ');
  
  // Apply phrase-level mappings (for multi-word phrases)
  // Sort by length (longest first) to match longer phrases first
  const phraseEntries = Object.entries(vocabulary)
    .filter(([key]) => key.includes(' '))
    .sort(([a], [b]) => b.length - a.length);
  
  for (const [phrase, replacement] of phraseEntries) {
    const regex = new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    normalized = normalized.replace(regex, replacement);
  }
  
  return normalized.trim();
};

export default {
  UPI_VOCABULARY,
  ACCENT_PATTERNS,
  UPI_PHRASES,
  getVocabularyForLanguage,
  getAccentPatternsForLanguage,
  getUPIPhrasesForLanguage,
  normalizeTranscript,
  normalizeForTTS,
};

