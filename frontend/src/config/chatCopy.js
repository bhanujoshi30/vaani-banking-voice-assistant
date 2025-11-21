import { DEFAULT_LANGUAGE } from "./voiceConfig.js";

export const PREFERRED_LANGUAGE_OPTIONS = ["en-IN", "hi-IN"];

export const LANGUAGE_MODAL_COPY = {
  title: "Choose your assistant language",
  subtitle: "Vaani can guide you in English or Hindi. Pick one to continue.",
  note: "You can change this anytime by tapping the assistant button.",
  continueButton: "Continue",
  cancelButton: "Not now",
  options: {
    "en-IN": {
      label: "English",
      description: "Full support with Indian English accent",
    },
    "hi-IN": {
      label: "हिंदी",
      description: "भारतीय हिंदी में सहज बातचीत",
    },
  },
};

const CHAT_COPY = {
  "en-IN": {
    initialGreeting: "Hello! I'm Vaani, your voice banking assistant. How can I help you today?",
    helperText: null,
    quickActionsTitle: "Quick Actions",
    quickActions: [
      { id: "balance", icon: "💰", label: "Check Balance", prompt: "Please share my latest account balance.", command: "Please share my latest account balance." },
      { id: "transfer", icon: "💸", label: "Transfer Funds", prompt: "Help me transfer funds to another account.", command: "Help me transfer funds to another account." },
      { id: "upi", icon: "📱", label: "UPI Transfer", prompt: "Help me transfer money using UPI", command: "Help me transfer money using UPI" },
      { id: "transactions", icon: "📊", label: "View Transactions", prompt: "Show my recent transactions.", command: "Show my recent transactions." },
      { id: "loan", icon: "📋", label: "Loan Information", prompt: "Tell me about loan products and options.", command: "Tell me about loan products and options." },
      { id: "investment", icon: "📈", label: "Investment Schemes", prompt: "Show me available investment schemes.", command: "Show me available investment schemes." },
      { id: "reminder", icon: "🔔", label: "Set Reminder", prompt: "I want to set a payment reminder.", command: "I want to set a payment reminder." },
      { id: "support", icon: "💬", label: "Customer Support", prompt: "I need help with customer support.", command: "I need help with customer support." },
    ],
    recentTopicsTitle: "Recent Topics",
    recentTopics: ["Account balance inquiry", "Transaction history", "Fund transfer"],
    voiceFeatures: {
      title: "🎤 Voice Features",
      description: "Tap the microphone icon to use voice commands.",
      assistantDescription: "Your intelligent voice banking assistant powered by DeewaniAI. Get instant help with account balances, transfers, transactions, and more using natural voice commands.",
      languageLabel: "Language",
      notSupportedHint: "Use Chrome, Edge, or Safari for voice input",
      comingSoonHint: "Currently selected:",
      comingSoonWarning: "This language is not ready yet. Please use English or Hindi.",
      readyHint: "Currently using:",
      badges: {
        notAvailable: "Not Available",
        comingSoon: "🚧 Coming Soon",
        ready: "✓ Ready",
      },
    },
    chatInput: {
      placeholders: {
        default: "Type your message or use voice input...",
        listening: "Listening... speak now",
        voiceMode: "Voice mode active - speak your message...",
        speaking: "Assistant is speaking... please wait",
        comingSoon: "Voice input not available for this language yet. Type your message or pick English/Hindi.",
      },
      micTooltip: {
        unsupported: "Voice input not supported in this browser",
        comingSoon: "This language is coming soon. Please use English or Hindi.",
        voiceMode: "Voice mode enabled - microphone stays on",
        stop: "Stop listening",
        start: "Start voice input",
      },
      hints: {
        speaking: "Assistant is speaking...",
        comingSoon: "Voice input coming soon for this language. Please use English or Hindi.",
        voiceMode: "Voice mode active - Speak naturally, your message will be sent automatically",
        listening: "Listening... Speak clearly",
        idle: "Try: \"Check my account balance\" or \"Show recent transactions\"",
        clickToRecord: "Click microphone to record again",
      },
      sendButtonTitle: {
        default: "Send message",
        disabled: "Please wait while assistant is speaking",
      },
    },
    fallbackResponses: {
      balance: "I can help you check your account balance. This feature will be fully functional once connected to the backend.",
      transfer: "I can assist you with transferring funds. This feature will be available once backend integration is complete.",
      transactions: "I can show you your transaction history. This will be connected to your actual transactions soon.",
      reminder: "I can help you set up payment reminders. This feature will be enabled after backend integration.",
      greeting: "Hello! How can I assist you with your banking needs today?",
      help: "I can help you with: checking balances, transferring funds, viewing transactions, and setting reminders. What would you like to do?",
      generic: "I understand your request. This feature will be connected to the backend soon to process your banking queries.",
    },
    cardIntros: {
      balance: "Here are the balances for your linked accounts.",
      transactions: "I've listed your latest transactions below. Use the card to filter or switch accounts as needed.",
      transfer: "Let's get this payment started. Pick the source account, enter the amount, and confirm the beneficiary using the card.",
      statement_request: "Choose the account and time period in this form before downloading your statement.",
      reminder_manager: "Use this panel to create a new reminder or review the ones you already have.",
      reminder: "Here's the reminder information you asked for.",
      loan: "Here's a quick summary of the loan details you asked about.",
      transfer_receipt: "Here's the receipt for the transfer you just completed.",
    },
    languageChange: {
      title: "Change Language",
      message: "Changing the language will refresh the chat. All messages will be cleared and you'll start a new conversation. Do you want to continue?",
      confirm: "Yes, change language",
      cancel: "Cancel",
    },
  },
  "hi-IN": {
    initialGreeting: "नमस्ते! मैं वाणी हूँ, आपकी वॉइस बैंकिंग सहायक। आज मैं आपकी कैसे मदद कर सकती हूँ?",
    helperText: null,
    quickActionsTitle: "त्वरित क्रियाएँ",
    quickActions: [
      {
        id: "balance",
        icon: "💰",
        label: "खाता बैलेंस देखें",
        prompt: "कृपया मेरा ताज़ा खाता बैलेंस बताएं।",
        command: "कृपया मेरा ताज़ा खाता बैलेंस बताएं।",
      },
      {
        id: "upi",
        icon: "📱",
        label: "UPI से पैसा ट्रांसफर करें",
        prompt: "UPI से पैसा ट्रांसफर करने में मेरी मदद करें",
        command: "UPI से पैसा ट्रांसफर करने में मेरी मदद करें",
      },
      {
        id: "transfer",
        icon: "💸",
        label: "राशि ट्रांसफ़र करें",
        prompt: "मुझे किसी खाते में राशि ट्रांसफ़र करनी है।",
        command: "Help me transfer funds to another account.",
      },
      {
        id: "transactions",
        icon: "📊",
        label: "लेनदेन देखें",
        prompt: "मेरे हाल के लेनदेन दिखाएँ।",
        command: "Show my recent transactions.",
      },
      {
        id: "loan",
        icon: "📋",
        label: "ऋण जानकारी",
        prompt: "मुझे ऋण उत्पादों और विकल्पों के बारे में बताएं।",
        command: "Tell me about loan products and options.",
      },
      {
        id: "investment",
        icon: "📈",
        label: "निवेश योजनाएं",
        prompt: "मुझे उपलब्ध निवेश योजनाएं दिखाएं।",
        command: "Show me available investment schemes.",
      },
      {
        id: "reminder",
        icon: "🔔",
        label: "रिमाइंडर सेट करें",
        prompt: "मैं एक भुगतान रिमाइंडर सेट करना चाहता हूँ।",
        command: "I want to set a payment reminder.",
      },
      {
        id: "support",
        icon: "💬",
        label: "ग्राहक सहायता",
        prompt: "मुझे ग्राहक सहायता की आवश्यकता है।",
        command: "I need help with customer support.",
      },
    ],
    recentTopicsTitle: "हाल के विषय",
    recentTopics: ["खाता बैलेंस पूछताछ", "लेनदेन इतिहास", "फंड ट्रांसफ़र"],
    voiceFeatures: {
      title: "🎤 वॉइस सुविधाएँ",
      description: "वॉइस कमांड के लिए माइक्रोफ़ोन आइकन टैप करें।",
      assistantDescription: "DeewaniAI द्वारा संचालित आपकी बुद्धिमान वॉइस बैंकिंग सहायक। प्राकृतिक वॉइस कमांड का उपयोग करके खाता बैलेंस, ट्रांसफ़र, लेनदेन और बहुत कुछ के साथ तत्काल सहायता प्राप्त करें।",
      languageLabel: "भाषा",
      notSupportedHint: "वॉइस इनपुट के लिए Chrome, Edge या Safari का उपयोग करें",
      comingSoonHint: "वर्तमान भाषा:",
      comingSoonWarning: "यह भाषा अभी तैयार नहीं है। कृपया अंग्रेज़ी या हिंदी का उपयोग करें।",
      readyHint: "सक्रिय भाषा:",
      badges: {
        notAvailable: "उपलब्ध नहीं",
        comingSoon: "🚧 जल्द आ रहा है",
        ready: "✓ तैयार",
      },
    },
    chatInput: {
      placeholders: {
        default: "अपना संदेश टाइप करें या आवाज़ का उपयोग करें...",
        listening: "सुन रहा हूँ... अब बोलें",
        voiceMode: "वॉइस मोड सक्रिय है - अपना संदेश बोलें...",
        speaking: "सहायक बोल रहा है... कृपया प्रतीक्षा करें",
        comingSoon: "इस भाषा के लिए वॉइस इनपुट अभी उपलब्ध नहीं है। कृपया संदेश टाइप करें या अंग्रेज़ी/हिंदी चुनें।",
      },
      micTooltip: {
        unsupported: "इस ब्राउज़र में वॉइस इनपुट समर्थित नहीं है",
        comingSoon: "यह भाषा जल्द ही उपलब्ध होगी। कृपया अंग्रेज़ी या हिंदी चुनें।",
        voiceMode: "वॉइस मोड चालू है - माइक्रोफ़ोन सक्रिय रहेगा",
        stop: "सुनना बंद करें",
        start: "वॉइस इनपुट शुरू करें",
      },
      hints: {
        speaking: "सहायक बोल रहा है... इनपुट बंद है",
        comingSoon: "इस भाषा के लिए वॉइस इनपुट जल्द ही उपलब्ध होगा। कृपया अंग्रेज़ी या हिंदी का उपयोग करें।",
        voiceMode: "वॉइस मोड सक्रिय है - सामान्य रूप से बोलें, संदेश अपने आप भेजा जाएगा",
        listening: "सुन रहा हूँ... साफ़ बोलें",
        idle: "कोशिश करें: \"मेरा खाता बैलेंस बताओ\" या \"हाल के लेनदेन दिखाओ\"",
        clickToRecord: "फिर से रिकॉर्ड करने के लिए माइक्रोफ़ोन पर क्लिक करें",
      },
      sendButtonTitle: {
        default: "संदेश भेजें",
        disabled: "कृपया प्रतीक्षा करें, सहायक बोल रहा है",
      },
    },
    fallbackResponses: {
      balance: "मैं आपके खाते का बैलेंस जांचने में मदद कर सकती हूँ। यह सुविधा जल्द ही बैकएंड से जुड़ जाएगी।",
      transfer: "मैं आपको राशि ट्रांसफ़र करने में मदद कर सकती हूँ। यह सुविधा बैकएंड इंटीग्रेशन पूरा होने पर उपलब्ध होगी।",
      transactions: "मैं आपके हाल के लेनदेन दिखा सकती हूँ। यह जल्द ही आपके वास्तविक लेनदेन से जुड़ जाएगा।",
      reminder: "मैं आपको भुगतान रिमाइंडर सेट करने में मदद कर सकती हूँ। बैकएंड के जुड़ते ही यह सुविधा सक्रिय हो जाएगी।",
      greeting: "नमस्ते! आज मैं आपकी बैंकिंग ज़रूरतों में कैसे मदद कर सकती हूँ?",
      help: "मैं बैलेंस जांचने, राशि ट्रांसफ़र करने, लेनदेन देखने और रिमाइंडर सेट करने में मदद कर सकती हूँ। आप क्या करना चाहेंगे?",
      generic: "मैंने आपका अनुरोध समझ लिया है। यह सुविधा जल्द ही बैकएंड से जुड़कर आपकी बैंकिंग क्वेरीज़ को पूरा करेगी।",
    },
    cardIntros: {
      balance: "यह रहे आपके खातों के वर्तमान बैलेंस।",
      transactions: "यहाँ आपके ताज़ा लेनदेन दिख रहे हैं। कार्ड से खाते बदलें या फ़िल्टर चुनें।",
      transfer: "चलिए यह भुगतान शुरू करते हैं। कार्ड में स्रोत खाता चुनें, राशि दर्ज करें और लाभार्थी की पुष्टि करें।",
      statement_request: "स्टेटमेंट डाउनलोड करने से पहले नीचे दिए फ़ॉर्म से खाता और अवधि चुनें।",
      reminder_manager: "इस पैनल से नए अनुस्मारक बनाएँ या मौजूदा को देखें।",
      reminder: "यह वह अनुस्मारक विवरण है जो आपने माँगा था।",
      loan: "यहाँ आपके अनुरोधित ऋण विवरण का सारांश है।",
      transfer_receipt: "यह आपके हाल के ट्रांसफ़र की रसीद है।",
    },
    languageChange: {
      title: "भाषा बदलें",
      message: "भाषा बदलने से चैट रीफ़्रेश होगी। सभी संदेश हटा दिए जाएंगे और आप एक नई बातचीत शुरू करेंगे। क्या आप जारी रखना चाहते हैं?",
      confirm: "हाँ, भाषा बदलें",
      cancel: "रद्द करें",
    },
  },
};

export const getChatCopy = (languageCode) => {
  return CHAT_COPY[languageCode] || CHAT_COPY[DEFAULT_LANGUAGE];
};

export default CHAT_COPY;
