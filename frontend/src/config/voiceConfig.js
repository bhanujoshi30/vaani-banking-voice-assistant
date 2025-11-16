/**
 * Voice Configuration Module
 * 
 * This file centralizes all voice-related configurations.
 * To change voice provider or add new features, modify this file only.
 */

/**
 * Available Languages Configuration
 * Add new languages here to support them throughout the app
 */
export const SUPPORTED_LANGUAGES = [
  {
    code: 'en-IN',
    name: 'English',
    nativeName: 'English',
    flag: '🇮🇳',
    enabled: true,
  },
  {
    code: 'hi-IN',
    name: 'Hindi',
    nativeName: 'हिंदी',
    flag: '🇮🇳',
    enabled: true,
  },
  {
    code: 'ta-IN',
    name: 'Tamil',
    nativeName: 'தமிழ்',
    flag: '🇮🇳',
    enabled: false, // Enable when ready
  },
  {
    code: 'te-IN',
    name: 'Telugu',
    nativeName: 'తెలుగు',
    flag: '🇮🇳',
    enabled: true, // Coming soon - UI ready, backend integration pending
    comingSoon: true, // Mark as coming soon
  },
  {
    code: 'mr-IN',
    name: 'Marathi',
    nativeName: 'मराठी',
    flag: '🇮🇳',
    enabled: false,
  },
  {
    code: 'bn-IN',
    name: 'Bengali',
    nativeName: 'বাংলা',
    flag: '🇮🇳',
    enabled: false,
  },
  {
    code: 'gu-IN',
    name: 'Gujarati',
    nativeName: 'ગુજરાતી',
    flag: '🇮🇳',
    enabled: false,
  },
  {
    code: 'kn-IN',
    name: 'Kannada',
    nativeName: 'ಕನ್ನಡ',
    flag: '🇮🇳',
    enabled: false,
  },
  {
    code: 'ml-IN',
    name: 'Malayalam',
    nativeName: 'മലയാളം',
    flag: '🇮🇳',
    enabled: false,
  },
  {
    code: 'pa-IN',
    name: 'Punjabi',
    nativeName: 'ਪੰਜਾਬੀ',
    flag: '🇮🇳',
    enabled: false,
  },
];

/**
 * Get only enabled languages
 */
export const getEnabledLanguages = () => {
  return SUPPORTED_LANGUAGES.filter(lang => lang.enabled);
};

/**
 * Get language by code
 */
export const getLanguageByCode = (code) => {
  return SUPPORTED_LANGUAGES.find(lang => lang.code === code);
};

/**
 * Default language
 */
export const DEFAULT_LANGUAGE = 'en-IN';

/**
 * Voice Provider Configuration
 * Change this to switch between different voice recognition providers
 */
export const VOICE_PROVIDER = {
  type: 'web-speech-api', // Options: 'web-speech-api', 'google-cloud', 'azure', 'custom'
  
  // Web Speech API specific settings
  webSpeechApi: {
    continuous: true,
    interimResults: true,
    maxAlternatives: 1,
  },
  
  // Placeholder for future providers
  googleCloud: {
    apiKey: '', // Add when implementing
    endpoint: '',
  },
  
  azure: {
    subscriptionKey: '', // Add when implementing
    region: '',
  },
};

/**
 * Voice Recognition Settings
 */
export const VOICE_SETTINGS = {
  // Auto-send message after silence (in milliseconds)
  autoSendDelay: null, // null = disabled, number = delay in ms
  
  // Show interim results (real-time transcription)
  showInterimResults: true,
  
  // Confidence threshold (0-1)
  confidenceThreshold: 0.5,
  
  // Maximum recording duration (in milliseconds)
  maxRecordingDuration: 60000, // 60 seconds
  
  // Enable voice feedback (beep sounds, etc.)
  enableFeedback: true,
};

/**
 * UI Text Configuration
 * Localized strings for the voice interface
 */
export const VOICE_UI_TEXT = {
  'en-IN': {
    startListening: 'Start voice input',
    stopListening: 'Stop listening',
    listening: 'Listening... Speak clearly',
    processing: 'Processing...',
    placeholder: 'Type your message or use voice input...',
    placeholderListening: 'Listening... speak now',
    notSupported: 'Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.',
    permissionDenied: 'Microphone permission denied. Please allow microphone access.',
    noSpeech: 'No speech detected. Please try again.',
    hint: 'Try: "Check my account balance" or "Show recent transactions"',
  },
  'hi-IN': {
    startListening: 'आवाज़ इनपुट शुरू करें',
    stopListening: 'सुनना बंद करें',
    listening: 'सुन रहा हूँ... स्पष्ट बोलें',
    processing: 'प्रोसेस हो रहा है...',
    placeholder: 'अपना संदेश टाइप करें या आवाज़ का उपयोग करें...',
    placeholderListening: 'सुन रहा हूँ... अब बोलें',
    notSupported: 'आवाज़ इनपुट आपके ब्राउज़र में समर्थित नहीं है। कृपया Chrome, Edge, या Safari का उपयोग करें।',
    permissionDenied: 'माइक्रोफ़ोन अनुमति अस्वीकृत। कृपया माइक्रोफ़ोन एक्सेस की अनुमति दें।',
    noSpeech: 'कोई आवाज़ नहीं मिली। कृपया पुनः प्रयास करें।',
    hint: 'कोशिश करें: "मेरा खाता बैलेंस चेक करें" या "हाल के लेनदेन दिखाएं"',
  },
};

/**
 * Get UI text for a specific language
 */
export const getVoiceUIText = (languageCode) => {
  return VOICE_UI_TEXT[languageCode] || VOICE_UI_TEXT[DEFAULT_LANGUAGE];
};

/**
 * Browser Compatibility Check
 */
export const checkVoiceSupport = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  return {
    supported: !!SpeechRecognition,
    provider: SpeechRecognition ? 'Web Speech API' : null,
    browser: getBrowserInfo(),
  };
};

/**
 * Get browser information
 */
const getBrowserInfo = () => {
  const ua = navigator.userAgent;
  if (ua.includes('Chrome')) return 'Chrome';
  if (ua.includes('Safari')) return 'Safari';
  if (ua.includes('Firefox')) return 'Firefox';
  if (ua.includes('Edge')) return 'Edge';
  return 'Unknown';
};

/**
 * Voice Provider Factory
 * Use this to instantiate the appropriate voice provider
 * 
 * @param {string} languageCode - The language code to use
 * @returns {Object} Voice provider instance
 */
export const createVoiceProvider = (languageCode = DEFAULT_LANGUAGE) => {
  switch (VOICE_PROVIDER.type) {
    case 'web-speech-api':
      return {
        type: 'web-speech-api',
        config: {
          lang: languageCode,
          ...VOICE_PROVIDER.webSpeechApi,
        },
      };
    
    // Add other providers here as needed
    case 'google-cloud':
      return {
        type: 'google-cloud',
        config: {
          lang: languageCode,
          ...VOICE_PROVIDER.googleCloud,
        },
      };
    
    case 'azure':
      return {
        type: 'azure',
        config: {
          lang: languageCode,
          ...VOICE_PROVIDER.azure,
        },
      };
    
    default:
      throw new Error(`Unknown voice provider: ${VOICE_PROVIDER.type}`);
  }
};

export default {
  SUPPORTED_LANGUAGES,
  getEnabledLanguages,
  getLanguageByCode,
  DEFAULT_LANGUAGE,
  VOICE_PROVIDER,
  VOICE_SETTINGS,
  VOICE_UI_TEXT,
  getVoiceUIText,
  checkVoiceSupport,
  createVoiceProvider,
};
