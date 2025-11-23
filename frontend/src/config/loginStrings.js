import { DEFAULT_LANGUAGE } from "./voiceConfig.js";

/**
 * Login Page String Assets
 * 
 * Centralized location for all login page text content in multiple languages.
 * This ensures consistency and makes it easy to maintain and extend translations.
 */

export const LOGIN_STRINGS = {
  "en-IN": {
    // Voice login section
    voiceLogin: {
      firstTimeBanner: {
        text: "First time with voice login? We'll capture the passphrase",
        textAfter: "twice to enroll your voice securely. From the next login you can speak any short phrase.",
      },
      referenceBox: {
        header: "These are example phrases to record voice:",
        languageLabel: "English:",
        phrase: "Sun Bank is my companion, a promise of secure banking at every step",
      },
      recording: {
        statusFirstTime: "Recording… Speak clearly:",
        statusNormal: "Recording… Speak naturally in your own words.",
        statusFirstSample: "First sample captured. Please re-record the passphrase to confirm your voice.",
        statusConfirmed: "Voice sample confirmed. You can proceed to login.",
        statusProcessing: "Processing voice sample…",
        statusError: "Unable to process the voice sample.",
        statusPermissionDenied: "Microphone permission denied by the browser.",
        statusNotSupported: "Microphone access is not supported on this device.",
        statusRequesting: "Requesting microphone access…",
      },
      controls: {
        recordButton: "Record voice sample",
        stopButton: "Stop recording",
        resetButton: "Reset voice capture",
        sampleReady: "Sample ready",
        sample1Ready: "Sample 1 ready",
        sample2Ready: "Sample 2 ready",
        captured: "Captured",
      },
      errors: {
        noVoiceSample: "Please capture and confirm your voice sample before continuing. (If this is your first time enrolling for voice login, record the passphrase twice.)",
      },
    },
    // Language toggle
    languageToggle: {
      switchTo: "Switch to Hindi",
      targetLanguage: "हिंदी", // Language name shown on button (the language it will switch TO) - in Hindi script
      ariaLabel: "Switch language to Hindi",
    },
    // General login
    general: {
      welcomeTitle: "Welcome back.",
      welcomeSubtitle: "Sign in to continue to your Sun National Bank profile.",
      userIdLabel: "User ID",
      userIdPlaceholder: "Enter your customer ID",
      passwordLabel: "Password",
      voiceLabel: "Voice",
      passwordPlaceholder: "Enter your password",
      showPassword: "Show",
      hidePassword: "Hide",
      loginButton: "Log in",
      verifyOtpButton: "Verify OTP",
      verifying: "Verifying…",
      verifyingVoice: "Verifying voice…",
      otpLabel: "Enter OTP",
      otpPlaceholder: "Enter the 5-digit OTP",
      showOtp: "Show",
      hideOtp: "Hide",
      editDetails: "Edit details",
      needHelp: "Need help signing in?",
      sunHeaderSubtitle: "Voice-first banking, made human.",
      scrollHint: "Scroll to explore more",
      scrollDown: "Scroll down",
    },
    // Hero section
    hero: {
      titleEnglish: "Voice-First Banking",
      titleHindi: "आवाज़-पहली बैंकिंग",
      languageTagEnglish: "English",
      languageTagHindi: "हिंदी",
      languageTagMore: "+ More languages",
      subtitleText: "Currently available in English & Hindi",
      subtitleHint: "Extensible to any language worldwide",
      tagline: "Secure, smart, and seamless banking for Bharat",
    },
    // Vaani AI Assistant section
    vaani: {
      badge: "What's New",
      title: "Experience Banking with Vaani AI Assistant",
      description: "Your intelligent voice-first banking companion. Ask questions, get instant answers about loans, investments, and banking services in English or Hindi.",
      feature1: "Voice-first interaction for seamless banking",
      feature2: "AI-powered intelligent responses",
      feature3: "Multi-language support (English & Hindi)",
      feature4: "Natural conversation interface",
    },
    // Loan products section
    loans: {
      title: "Our Loan Products",
      subtitle: "Choose from a wide range of loan options tailored to your needs",
      homeLoan: {
        title: "Home Loan",
        rate: "8.35% - 9.50% p.a.",
        description: "Up to ₹5 crores | Up to 30 years",
      },
      autoLoan: {
        title: "Auto Loan",
        rate: "8.75% - 12% p.a.",
        description: "Up to ₹50 lakhs | Up to 7 years",
      },
      personalLoan: {
        title: "Personal Loan",
        rate: "10.5% - 24% p.a.",
        description: "Up to ₹40 lakhs | Up to 5 years",
      },
      educationLoan: {
        title: "Education Loan",
        rate: "8.5% - 11.5% p.a.",
        description: "Up to ₹1 crore | Up to 15 years",
      },
      businessLoan: {
        title: "Business Loan",
        rate: "11% - 18% p.a.",
        description: "Up to ₹50 lakhs | MSME/SME",
      },
      goldLoan: {
        title: "Gold Loan",
        rate: "10% - 15% p.a.",
        description: "Up to ₹25 lakhs | Quick approval",
      },
      loanAgainstProperty: {
        title: "Loan Against Property",
        rate: "9.5% - 12.5% p.a.",
        description: "Up to ₹5 crores | Up to 15 years",
      },
    },
    // Investment schemes section
    investments: {
      title: "Investment Schemes",
      subtitle: "Grow your wealth with our diverse investment options",
      ppf: {
        title: "PPF",
        rate: "7.1% p.a.",
        description: "₹500 - ₹1.5L/year | 15 years | Tax-free",
      },
      nps: {
        title: "NPS",
        rate: "8-12% p.a.",
        description: "Market-linked | Retirement scheme | Extra ₹50K tax deduction",
      },
      ssy: {
        title: "SSY",
        rate: "8.2% p.a.",
        description: "₹250 - ₹1.5L/year | Girl child scheme | 21 years",
      },
      elss: {
        title: "ELSS",
        rate: "Market-linked",
        description: "₹500+ | 3-year lock-in | Tax saving mutual fund",
      },
      fixedDeposit: {
        title: "Fixed Deposit",
        rate: "6-8% p.a.",
        description: "₹1000+ | 7 days-10 years | Safe investment",
      },
      recurringDeposit: {
        title: "Recurring Deposit",
        rate: "6-7.5% p.a.",
        description: "₹100/month | Regular savings",
      },
      nsc: {
        title: "NSC",
        rate: "7-9% p.a.",
        description: "₹1000+ | 5 years | Government backed",
      },
    },
    // Footer
    footer: {
      text: "© {year} Sun National Bank · RBI compliant · Made for Bharat",
    },
    // Errors
    errors: {
      noUserId: "Please enter your User ID to continue.",
      invalidPassword: "Enter a valid password (minimum 4 characters).",
      invalidOtp: "The OTP you entered is incorrect. Please try again.",
      credentialsError: "Credentials could not be verified. Try again.",
      authError: "We could not verify those credentials. Try again.",
      serverError: "Something went wrong while contacting the bank. Please try again.",
    },
  },
  "hi-IN": {
    // Voice login section
    voiceLogin: {
      firstTimeBanner: {
        text: "पहली बार वॉइस लॉगिन कर रहे हैं? हम पासफ़्रेज़",
        textAfter: "को दो बार कैप्चर करेंगे ताकि आपकी आवाज़ सुरक्षित रूप से पंजीकृत हो जाए। अगली बार से आप कोई भी छोटा वाक्य बोल सकते हैं।",
      },
      referenceBox: {
        header: "ये आवाज़ रिकॉर्ड करने के लिए उदाहरण वाक्य हैं:",
        languageLabel: "हिंदी:",
        phrase: "सन बैंक मेरा साथी, हर कदम सुरक्षित बैंकिंग का वादा",
      },
      recording: {
        statusFirstTime: "रिकॉर्डिंग… साफ़ बोलें:",
        statusNormal: "रिकॉर्डिंग… अपने शब्दों में स्वाभाविक रूप से बोलें।",
        statusFirstSample: "पहला नमूना कैप्चर हो गया। कृपया अपनी आवाज़ की पुष्टि के लिए पासफ़्रेज़ को फिर से रिकॉर्ड करें।",
        statusConfirmed: "आवाज़ का नमूना पुष्ट हो गया। आप लॉगिन कर सकते हैं।",
        statusProcessing: "आवाज़ का नमूना प्रसंस्करण कर रहे हैं…",
        statusError: "आवाज़ का नमूना प्रसंस्कृत नहीं कर सका।",
        statusPermissionDenied: "ब्राउज़र द्वारा माइक्रोफ़ोन अनुमति अस्वीकार कर दी गई।",
        statusNotSupported: "इस डिवाइस पर माइक्रोफ़ोन एक्सेस समर्थित नहीं है।",
        statusRequesting: "माइक्रोफ़ोन एक्सेस का अनुरोध कर रहे हैं…",
      },
      controls: {
        recordButton: "आवाज़ का नमूना रिकॉर्ड करें",
        stopButton: "रिकॉर्डिंग रोकें",
        resetButton: "आवाज़ कैप्चर रीसेट करें",
        sampleReady: "नमूना तैयार",
        sample1Ready: "नमूना 1 तैयार",
        sample2Ready: "नमूना 2 तैयार",
        captured: "कैप्चर किया गया",
      },
      errors: {
        noVoiceSample: "कृपया आगे बढ़ने से पहले अपना आवाज़ का नमूना कैप्चर और पुष्टि करें। (यदि यह आपका पहली बार वॉइस लॉगिन के लिए पंजीकरण है, तो पासफ़्रेज़ को दो बार रिकॉर्ड करें।)",
      },
    },
    // Language toggle
    languageToggle: {
      switchTo: "अंग्रेज़ी में बदलें",
      targetLanguage: "English", // Language name shown on button (the language it will switch TO)
      ariaLabel: "भाषा को अंग्रेज़ी में बदलें",
    },
    // General login
    general: {
      welcomeTitle: "वापसी पर स्वागत है।",
      welcomeSubtitle: "अपने सन नेशनल बैंक प्रोफ़ाइल पर जारी रखने के लिए साइन इन करें।",
      userIdLabel: "उपयोगकर्ता आईडी",
      userIdPlaceholder: "अपना ग्राहक आईडी दर्ज करें",
      passwordLabel: "पासवर्ड",
      voiceLabel: "आवाज़",
      passwordPlaceholder: "अपना पासवर्ड दर्ज करें",
      showPassword: "दिखाएँ",
      hidePassword: "छुपाएँ",
      loginButton: "लॉग इन करें",
      verifyOtpButton: "OTP सत्यापित करें",
      verifying: "सत्यापित कर रहे हैं…",
      verifyingVoice: "आवाज़ सत्यापित कर रहे हैं…",
      otpLabel: "OTP दर्ज करें",
      otpPlaceholder: "5 अंकों का OTP दर्ज करें",
      showOtp: "दिखाएँ",
      hideOtp: "छुपाएँ",
      editDetails: "विवरण संपादित करें",
      needHelp: "साइन इन करने में मदद चाहिए?",
      sunHeaderSubtitle: "आवाज़-पहली बैंकिंग, मानवीय बनाई गई।",
      scrollHint: "और जानकारी देखने के लिए नीचे स्क्रॉल करें",
      scrollDown: "नीचे स्क्रॉल करें",
    },
    // Hero section
    hero: {
      titleEnglish: "Voice-First Banking",
      titleHindi: "आवाज़-पहली बैंकिंग",
      languageTagEnglish: "English",
      languageTagHindi: "हिंदी",
      languageTagMore: "+ अधिक भाषाएँ",
      subtitleText: "वर्तमान में अंग्रेज़ी और हिंदी में उपलब्ध",
      subtitleHint: "दुनिया भर की किसी भी भाषा में विस्तार योग्य",
      tagline: "भारत के लिए सुरक्षित, स्मार्ट और निर्बाध बैंकिंग",
    },
    // Vaani AI Assistant section
    vaani: {
      badge: "नया क्या है",
      title: "वाणी AI असिस्टेंट के साथ बैंकिंग का अनुभव करें",
      description: "आपका बुद्धिमान आवाज़-पहली बैंकिंग साथी। अंग्रेज़ी या हिंदी में ऋण, निवेश और बैंकिंग सेवाओं के बारे में प्रश्न पूछें, तत्काल उत्तर प्राप्त करें।",
      feature1: "निर्बाध बैंकिंग के लिए आवाज़-पहली बातचीत",
      feature2: "AI-संचालित बुद्धिमान प्रतिक्रियाएँ",
      feature3: "बहु-भाषा समर्थन (अंग्रेज़ी और हिंदी)",
      feature4: "प्राकृतिक वार्तालाप इंटरफ़ेस",
    },
    // Loan products section
    loans: {
      title: "हमारे ऋण उत्पाद",
      subtitle: "अपनी आवश्यकताओं के अनुरूप ऋण विकल्पों की विस्तृत श्रृंखला में से चुनें",
      homeLoan: {
        title: "होम लोन",
        rate: "8.35% - 9.50% प्रति वर्ष",
        description: "₹5 करोड़ तक | 30 वर्ष तक",
      },
      autoLoan: {
        title: "ऑटो लोन",
        rate: "8.75% - 12% प्रति वर्ष",
        description: "₹50 लाख तक | 7 वर्ष तक",
      },
      personalLoan: {
        title: "पर्सनल लोन",
        rate: "10.5% - 24% प्रति वर्ष",
        description: "₹40 लाख तक | 5 वर्ष तक",
      },
      educationLoan: {
        title: "एजुकेशन लोन",
        rate: "8.5% - 11.5% प्रति वर्ष",
        description: "₹1 करोड़ तक | 15 वर्ष तक",
      },
      businessLoan: {
        title: "बिज़नेस लोन",
        rate: "11% - 18% प्रति वर्ष",
        description: "₹50 लाख तक | MSME/SME",
      },
      goldLoan: {
        title: "गोल्ड लोन",
        rate: "10% - 15% प्रति वर्ष",
        description: "₹25 लाख तक | त्वरित अनुमोदन",
      },
      loanAgainstProperty: {
        title: "संपत्ति के खिलाफ ऋण",
        rate: "9.5% - 12.5% प्रति वर्ष",
        description: "₹5 करोड़ तक | 15 वर्ष तक",
      },
    },
    // Investment schemes section
    investments: {
      title: "निवेश योजनाएँ",
      subtitle: "हमारे विविध निवेश विकल्पों के साथ अपनी संपत्ति बढ़ाएँ",
      ppf: {
        title: "PPF",
        rate: "7.1% प्रति वर्ष",
        description: "₹500 - ₹1.5L/वर्ष | 15 वर्ष | कर-मुक्त",
      },
      nps: {
        title: "NPS",
        rate: "8-12% प्रति वर्ष",
        description: "बाज़ार-लिंक्ड | सेवानिवृत्ति योजना | अतिरिक्त ₹50K कर कटौती",
      },
      ssy: {
        title: "SSY",
        rate: "8.2% प्रति वर्ष",
        description: "₹250 - ₹1.5L/वर्ष | बालिका योजना | 21 वर्ष",
      },
      elss: {
        title: "ELSS",
        rate: "बाज़ार-लिंक्ड",
        description: "₹500+ | 3 वर्ष लॉक-इन | कर बचत म्यूचुअल फंड",
      },
      fixedDeposit: {
        title: "फिक्स्ड डिपॉज़िट",
        rate: "6-8% प्रति वर्ष",
        description: "₹1000+ | 7 दिन-10 वर्ष | सुरक्षित निवेश",
      },
      recurringDeposit: {
        title: "रिकरिंग डिपॉज़िट",
        rate: "6-7.5% प्रति वर्ष",
        description: "₹100/महीना | नियमित बचत",
      },
      nsc: {
        title: "NSC",
        rate: "7-9% प्रति वर्ष",
        description: "₹1000+ | 5 वर्ष | सरकारी समर्थित",
      },
    },
    // Footer
    footer: {
      text: "© {year} सन नेशनल बैंक · RBI अनुपालन · भारत के लिए बनाया गया",
    },
    // Errors
    errors: {
      noUserId: "कृपया आगे बढ़ने के लिए अपना उपयोगकर्ता आईडी दर्ज करें।",
      invalidPassword: "एक वैध पासवर्ड दर्ज करें (न्यूनतम 4 वर्ण)।",
      invalidOtp: "आपके द्वारा दर्ज किया गया OTP गलत है। कृपया पुनः प्रयास करें।",
      credentialsError: "क्रेडेंशियल सत्यापित नहीं किए जा सके। पुनः प्रयास करें।",
      authError: "हम उन क्रेडेंशियल को सत्यापित नहीं कर सके। पुनः प्रयास करें।",
      serverError: "बैंक से संपर्क करते समय कुछ गलत हो गया। कृपया पुनः प्रयास करें।",
    },
  },
};

/**
 * Get login strings for a specific language
 * @param {string} languageCode - Language code (e.g., 'en-IN', 'hi-IN')
 * @returns {object} Login strings for the specified language
 */
export const getLoginStrings = (languageCode) => {
  return LOGIN_STRINGS[languageCode] || LOGIN_STRINGS[DEFAULT_LANGUAGE];
};

/**
 * Voice phrases for each language
 */
export const VOICE_PHRASES = {
  "en-IN": "Sun Bank is my companion, a promise of secure banking at every step",
  "hi-IN": "सन बैंक मेरा साथी, हर कदम सुरक्षित बैंकिंग का वादा",
};

/**
 * Get voice phrase for a specific language
 * @param {string} languageCode - Language code (e.g., 'en-IN', 'hi-IN')
 * @returns {string} Voice phrase for the specified language
 */
export const getVoicePhrase = (languageCode) => {
  return VOICE_PHRASES[languageCode] || VOICE_PHRASES[DEFAULT_LANGUAGE];
};

export default LOGIN_STRINGS;

