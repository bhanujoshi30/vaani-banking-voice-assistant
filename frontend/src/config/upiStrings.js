export const UPI_STRINGS = {
  "en-IN": {
    // Wake-up phrases
    wakeUpPhrases: ["hello vaani", "hello upi", "hey vaani", "hey upi"],
    
    // UPI Mode
    upiModeActive: "UPI Mode Active",
    upiModeInactive: "UPI Mode Inactive",
    upiModeDescription: "You can now make UPI payments using voice commands",
    
    // PIN Modal
    upiPinTitle: "Enter UPI PIN",
    pinDescription: "Please enter your 6-digit UPI PIN to confirm the payment",
    pinInvalid: "PIN must be 6 digits",
    amount: "Amount",
    to: "To",
    cancel: "Cancel",
    confirm: "Confirm",
    edit: "Edit",
    save: "Save",
    
    // Consent Modal
    consentTitle: "Hello UPI - Terms & Conditions",
    consentIntro: "To use Hello UPI voice-assisted payments, please review and accept the following:",
    consentPoint1: "I understand that UPI PIN must be entered manually and cannot be spoken",
    consentPoint2: "I agree to use Hello UPI in compliance with RBI guidelines",
    consentPoint3: "I acknowledge that all transactions are subject to verification",
    consentPoint4: "I will keep my UPI PIN confidential and not share it with anyone",
    consentNote: "By proceeding, you agree to the terms and conditions of Hello UPI service.",
    decline: "Decline",
    accept: "Accept & Continue",
    
    // Payment Messages
    paymentPrompt: "Please provide the amount and recipient details for UPI payment.",
    paymentConfirm: "UPI Payment: Send ₹{amount} to {recipient}. Please enter your UPI PIN.",
    paymentSuccess: "UPI payment of ₹{amount} to {recipient} successful",
    paymentFailed: "UPI payment failed. Please try again.",
    recipientNotFound: "Recipient not found. Please check the UPI ID or phone number.",
    
    // Quick Actions
    upiQuickAction: "Pay via UPI",
    upiQuickActionPrompt: "Hello Vaani, pay ₹500 to John via UPI",
  },
  "hi-IN": {
    // Wake-up phrases
    wakeUpPhrases: ["हेलो वाणी", "हेलो upi", "हेलो यूपीआई"],
    
    // UPI Mode
    upiModeActive: "UPI मोड सक्रिय",
    upiModeInactive: "UPI मोड निष्क्रिय",
    upiModeDescription: "अब आप वॉइस कमांड का उपयोग करके UPI भुगतान कर सकते हैं",
    
    // PIN Modal
    upiPinTitle: "UPI PIN दर्ज करें",
    pinDescription: "कृपया भुगतान की पुष्टि के लिए अपना 6-अंकीय UPI PIN दर्ज करें",
    pinInvalid: "PIN 6 अंकों का होना चाहिए",
    amount: "राशि",
    to: "को",
    cancel: "रद्द करें",
    confirm: "पुष्टि करें",
    edit: "संपादित करें",
    save: "सहेजें",
    
    // Consent Modal
    consentTitle: "Hello UPI - नियम और शर्तें",
    consentIntro: "Hello UPI वॉइस-सहायक भुगतान का उपयोग करने के लिए, कृपया निम्नलिखित की समीक्षा करें और स्वीकार करें:",
    consentPoint1: "मैं समझता हूं कि UPI PIN मैन्युअल रूप से दर्ज किया जाना चाहिए और बोला नहीं जा सकता",
    consentPoint2: "मैं RBI दिशानिर्देशों के अनुपालन में Hello UPI का उपयोग करने के लिए सहमत हूं",
    consentPoint3: "मैं स्वीकार करता हूं कि सभी लेनदेन सत्यापन के अधीन हैं",
    consentPoint4: "मैं अपने UPI PIN को गोपनीय रखूंगा और इसे किसी के साथ साझा नहीं करूंगा",
    consentNote: "आगे बढ़कर, आप Hello UPI सेवा की नियम और शर्तों से सहमत हैं।",
    decline: "अस्वीकार करें",
    accept: "स्वीकार करें और जारी रखें",
    
    // Payment Messages
    paymentPrompt: "कृपया UPI भुगतान के लिए राशि और प्राप्तकर्ता की जानकारी दें।",
    paymentConfirm: "UPI भुगतान: ₹{amount} {recipient} को भेजना है। कृपया अपना UPI PIN दर्ज करें।",
    paymentSuccess: "{recipient} को ₹{amount} का UPI भुगतान सफल",
    paymentFailed: "UPI भुगतान विफल। कृपया पुनः प्रयास करें।",
    recipientNotFound: "प्राप्तकर्ता नहीं मिला। कृपया UPI ID या फोन नंबर जांचें।",
    
    // Quick Actions
    upiQuickAction: "UPI से भुगतान करें",
    upiQuickActionPrompt: "हेलो वाणी, UPI से जॉन को ₹500 भेजें",
  },
};

export const getUPIStrings = (language = "en-IN") => {
  return UPI_STRINGS[language] || UPI_STRINGS["en-IN"];
};

