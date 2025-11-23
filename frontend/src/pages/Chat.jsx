import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import PropTypes from "prop-types";
import { Navigate, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import ChatMessage from "../components/Chat/ChatMessage.jsx";
import TypingIndicator from "../components/Chat/TypingIndicator.jsx";
import ChatInput from "../components/Chat/ChatInput.jsx";
import ChatSidebar from "../components/Chat/ChatSidebar.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
import UPIPinModal from "../components/UPIPinModal.jsx";
import UPIConsentModal from "../components/UPIConsentModal.jsx";
import VoiceEnrollmentModal from "../components/VoiceEnrollmentModal.jsx";
import useSpeechRecognition from "../hooks/useSpeechRecognition.js";
import useTextToSpeech from "../hooks/useTextToSpeech.js";
import { useChatMessages } from "../hooks/useChatMessages.js";
import { useVoiceMode } from "../hooks/useVoiceMode.js";
import { useChatHandler } from "../hooks/useChatHandler.js";
import { usePageLanguage } from "../hooks/usePageLanguage.js";
import { DEFAULT_LANGUAGE, getLanguageByCode } from "../config/voiceConfig.js";
import { getChatCopy } from "../config/chatCopy.js";
import { getUPIStrings } from "../config/upiStrings.js";
import { getPreferredLanguage, setPreferredLanguage, PREFERRED_LANGUAGE_KEY } from "../utils/preferences.js";
import { listDeviceBindings } from "../api/client.js";
import "./Chat.css";
import "../components/Chat/VoiceModeToggle.css";
import "../App.css";

const Chat = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState("");
  const [language, setLanguage] = useState(() => getPreferredLanguage());
  const [isVoiceModeEnabled, setIsVoiceModeEnabled] = useState(false);
  const [upiMode, setUpiMode] = useState(false);
  const [showUPIPinModal, setShowUPIPinModal] = useState(false);
  // Track if modal was opened via button click (not via pending message)
  const [upiConsentModalOpenedByButton, setUpiConsentModalOpenedByButton] = useState(false);
  const [showUPIConsentModal, setShowUPIConsentModal] = useState(false);
  const [upiPaymentDetails, setUpiPaymentDetails] = useState(null);
  // Initialize UPI consent - always start as false to ensure consent modal shows on first activation
  // We'll track consent in sessionStorage to persist within the session
  const [upiConsentGiven, setUpiConsentGiven] = useState(() => {
    // Always start as false - consent must be explicitly given in this session
    // Don't check localStorage or sessionStorage on initialization to ensure modal shows first time
    // UPI consent initialized - will show consent modal on first activation
    return false;
  });
  const [pendingUPIMessage, setPendingUPIMessage] = useState(null); // Store pending message waiting for consent
  const inputRef = useRef(null);
  // Track when PIN modal was opened by user action (via Proceed button) to prevent auto-closing
  const pinModalOpenedByUserRef = useRef(false);

  // Voice binding status
  const { strings: pageStrings } = usePageLanguage();
  const chatPageStrings = useMemo(() => pageStrings.chat || {}, [pageStrings, language]);
  const [hasVoiceBinding, setHasVoiceBinding] = useState(false);
  const [checkingVoiceBinding, setCheckingVoiceBinding] = useState(true);
  const [isVoiceEnrollmentModalOpen, setIsVoiceEnrollmentModalOpen] = useState(false);

  // Check if current session was logged in with voice
  const loggedInWithVoice = useMemo(() => {
    const detail = session?.detail ?? {};
    return Boolean(detail.voiceLogin) || detail.loginMode === "voice";
  }, [session?.detail]);

  // Determine if voice session is secured
  // Voice session is secured if:
  // 1. User logged in with voice, OR
  // 2. User has an active voice binding (even if logged in with password)
  const isVoiceSecured = useMemo(() => {
    return loggedInWithVoice || hasVoiceBinding;
  }, [loggedInWithVoice, hasVoiceBinding]);

  const chatCopy = useMemo(() => getChatCopy(language), [language]);
  const upiStrings = useMemo(() => getUPIStrings(language), [language]);

  // Get current language info
  const currentLanguage = getLanguageByCode(language);
  const isLanguageComingSoon = currentLanguage?.comingSoon || false;

  // Chat messages management
  const {
    messages,
    setMessages,
    messagesEndRef,
    addUserMessage,
    addAssistantMessage,
    clearUnusedCards,
    markLanguageChanging,
  } = useChatMessages({ initialMessage: chatCopy.initialGreeting });

  // Use speech recognition hook with selected language
  // In normal mode, use non-continuous (stops after each utterance)
  // In voice mode, use continuous (keeps listening)
  const {
    isListening,
    isSpeechSupported,
    fullTranscript,
    transcript,
    interimTranscript,
    error: speechError,
    toggleListening,
    startListening,
    stopListening,
    resetTranscript,
    clearManualStopFlags, // Function to clear manual stop flags in speech recognition
  } = useSpeechRecognition({
    lang: language,
    continuous: isVoiceModeEnabled, // Only continuous in voice mode
    interimResults: true,
  });

  // Use text-to-speech hook
  const {
    isSpeaking,
    isTTSSupported,
    selectedVoice,
    speak,
    stop: stopSpeaking,
  } = useTextToSpeech({
    lang: language,
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0,
  });

  // Chat message handling
  // Note: Removed excessive UPI mode logging - only log when state actually changes
  
  const {
    isTyping,
    sendMessage,
    handleQuickAction,
  } = useChatHandler({
    session,
    language,
    isVoiceModeEnabled,
    messages,
    addUserMessage,
    addAssistantMessage,
    resetTranscript,
    clearUnusedCards,
    setInputText,
    isListening,
    isSpeaking,
    stopListening,
    toggleListening,
    stopSpeaking, // Pass stopSpeaking to handler
    upiConsentGiven, // Pass consent status to handler
    upiMode, // Pass UPI mode state to handler
    setPendingUPIMessage, // Pass setter for pending messages
  });

  // Handle sending message from input
  const handleSendMessage = async (e) => {
    e.preventDefault();
    await sendMessage(inputText);
  };

  // Voice mode orchestration
  const { resetManualStop } = useVoiceMode({
    isVoiceModeEnabled,
    isLanguageComingSoon,
    isSpeaking,
    isTyping,
    isListening,
    fullTranscript,
    messages,
    startListening,
    stopListening,
    speak,
    resetTranscript,
    setInputText,
    onAutoSend: handleSendMessage,
    upiMode, // Pass UPI mode state to voice mode hook
    showUPIConsentModal, // Pass UPI consent modal state
    showUPIPinModal, // Pass UPI PIN modal state
    clearManualStopFlags, // Pass function to clear manual stop flags
  });

  // Note: UPI mode activation is now handled by backend response via structured_data
  // We don't activate UPI mode from transcript detection to avoid premature activation

  // Unified language change handler - used by both dropdown and AI
  // This ensures consistent behavior regardless of how language is changed
  // MUST be defined before useEffects that use it to avoid "Cannot access before initialization" error
  const handleLanguageChange = useCallback((newLang) => {
    // Validate language code
    if (!newLang || !["en-IN", "hi-IN"].includes(newLang)) {
      console.warn('Invalid language code:', newLang);
      return;
    }

    // If language hasn't changed, do nothing
    if (newLang === language) {
      console.log('Language unchanged, skipping update:', newLang);
      return;
    }

    // CRITICAL: Stop any ongoing speech/listening FIRST before changing language
    // This prevents the voice mode from recording while AI is speaking
    console.log('🛑 Language change: Stopping TTS and listening. Changing from', language, 'to', newLang);
    
    // Stop listening first to prevent recording
    if (isListening) {
      stopListening();
    }
    
    // Stop speaking if active
    if (isSpeaking) {
      stopSpeaking();
    }
    
    // Mark that we're changing language to prevent hook interference
    // This will prevent voice mode from auto-starting during language change
    markLanguageChanging();
    
    // Set the new language preference FIRST (this updates localStorage)
    setPreferredLanguage(newLang);
    
    // Update local language state - keep all messages as they are
    setLanguage(newLang);
    
    // Dispatch event to notify other components (including dropdown)
    // This ensures dropdown and other components stay in sync
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: newLang } }));
    
    console.log('✅ Language changed successfully to:', newLang);
  }, [language, isListening, isSpeaking, stopListening, stopSpeaking, markLanguageChanging]);

  // Update input text when speech transcript changes
  useEffect(() => {
    if (fullTranscript && !isSpeaking) {
      console.log('Updating input with transcript:', fullTranscript);
      setInputText(fullTranscript);
    }
  }, [fullTranscript, isSpeaking]);

  // Track processed message IDs to avoid re-processing
  const processedMessageIdsRef = useRef(new Set());
  // Track processed language changes to avoid re-processing
  const processedLanguageChangeRef = useRef(null);
  
  // Handle UPI mode activation and payment structured data
  // This now only handles messages that are already in chat (after consent)
  useEffect(() => {
    // Check the last assistant message for structured data
    const lastAssistantMessage = [...messages].reverse().find(msg => msg.role === 'assistant');
    if (!lastAssistantMessage) return;
    
    // Handle UPI mode activation (wake-up phrase)
    if (lastAssistantMessage?.structuredData?.type === 'upi_mode_activation') {
      // If consent already given, activate UPI mode
      if (upiConsentGiven && !upiMode) {
        setUpiMode(true);
      } else if (!upiConsentGiven && !pendingUPIMessage) {
        // If consent not given and no pending message, this shouldn't happen
        // but if it does, ensure the message is in pendingUPIMessage
        console.warn('⚠️ UPI mode activation detected but no pending message and no consent - this should not happen');
      }
      // Note: If consent not given, the message should be in pendingUPIMessage
      // and the consent modal should be shown by the other useEffect
      return;
    }
    
    // Handle UPI payment card - show card for entering UPI ID and amount
    // BUT: Only if consent has been given (consent check happens in useChatHandler)
    if (lastAssistantMessage?.structuredData?.type === 'upi_payment_card') {
      const messageId = lastAssistantMessage.id;
      const isNewMessage = !processedMessageIdsRef.current.has(messageId);
      
      // CRITICAL: Stop recording immediately when UPI payment card appears
      // This prevents AI from recording its own statement about UPI payment
      // BUT: User can still manually start recording by clicking the mic button
      if (isListening) {
        stopListening();
        // Clear transcript to prevent AI's statement from being captured
        resetTranscript();
        setInputText('');
      }
      
      // IMPORTANT: Only stop TTS if this is NOT a new message (i.e., user is interacting)
      // For new messages, allow TTS to complete so the user hears the instruction
      if (isSpeaking && !isNewMessage) {
        stopSpeaking();
        // Mark as processed when stopping TTS for non-new messages
        processedMessageIdsRef.current.add(messageId);
      } else if (isNewMessage) {
        // CRITICAL: Don't mark as processed immediately - let useVoiceMode.js handle TTS first
        // Mark it as processed after a delay to ensure TTS has started and completed
        // This prevents the effect from running again and interfering with TTS
        setTimeout(() => {
          processedMessageIdsRef.current.add(messageId);
        }, 2000); // Longer delay to allow TTS to start and complete
      }
      
      // Only activate UPI mode if consent has been given
      // If consent not given, the message should be pending and not reach here
      if (!upiMode && upiConsentGiven) {
        setUpiMode(true);
      }
      
      // Card will be displayed by ChatMessage component - no PIN modal needed here
      // PIN modal will be shown when user clicks "Proceed" in the card
      // IMPORTANT: Only close PIN modal if it was open from a PREVIOUS payment card
      // Don't close it if user just clicked Proceed (that would be a race condition)
      // We check if this is a new message - if it's new, don't close modal
      // Also check if modal was opened by user action - if so, don't close it
      if (showUPIPinModal && !isNewMessage && !pinModalOpenedByUserRef.current) {
        // Closing PIN modal from previous payment card state
        setShowUPIPinModal(false);
        setUpiPaymentDetails(null);
      }
      // Reset the user action flag after a delay to allow for normal flow
      // This prevents the effect from closing the modal immediately after user opens it
      if (pinModalOpenedByUserRef.current) {
        setTimeout(() => {
          pinModalOpenedByUserRef.current = false;
        }, 500);
      }
      return;
    }
    
    // Handle UPI payment request - only if consent already given
    if (lastAssistantMessage?.structuredData?.type === 'upi_payment') {
      const paymentData = lastAssistantMessage.structuredData;
      
      // Set UPI mode if not already set
      if (!upiMode) {
        setUpiMode(true);
      }
      
      // Show PIN modal if amount and recipient are available AND UPI ID is validated
      if (paymentData.amount && paymentData.recipient_identifier && paymentData.upi_id_validated !== false) {
        // Validate UPI ID format before showing PIN modal
        const validateUPIId = (upiId) => {
          if (!upiId || !upiId.trim()) return false;
          const trimmed = upiId.trim();
          if (trimmed.length < 5 || trimmed.length > 100) return false;
          if (!trimmed.includes('@')) return false;
          const parts = trimmed.split('@');
          if (parts.length !== 2) return false;
          const [username, payee] = parts;
          if (username.length < 3 || username.length > 99) return false;
          if (payee.length < 2 || payee.length > 20) return false;
          if (!/^[a-zA-Z0-9._-]+$/.test(username)) return false;
          if (!/^[a-zA-Z0-9]+$/.test(payee)) return false;
          return true;
        };
        
        // Only show PIN modal if UPI ID is valid (or if it's a beneficiary selector)
        if (paymentData.recipient_identifier === "first" || 
            paymentData.recipient_identifier === "last" ||
            validateUPIId(paymentData.recipient_identifier)) {
          setUpiPaymentDetails({
            amount: paymentData.amount,
            recipient: paymentData.recipient_identifier,
            sourceAccount: paymentData.source_account_number,
            remarks: paymentData.remarks,
          });
          setShowUPIPinModal(true);
        } else {
          // Invalid UPI ID - error message should already be in the assistant response
          // Invalid UPI ID - not showing PIN modal
        }
      }
    }
    
    // Handle UPI balance check request - only if consent already given
    if (lastAssistantMessage?.structuredData?.type === 'upi_balance_check') {
      const balanceData = lastAssistantMessage.structuredData;
      
      // Set UPI mode if not already set
      if (!upiMode) {
        setUpiMode(true);
      }
      
      // If account selection is pending, don't show PIN modal yet
      if (balanceData.pending_account_selection) {
        // User needs to specify which account - message already sent
        return;
      }
      
      // Show PIN modal if account is selected
      if (balanceData.source_account_id && balanceData.source_account_number) {
        setUpiPaymentDetails({
          operation: 'balance_check',
          sourceAccount: balanceData.source_account_number,
          sourceAccountId: balanceData.source_account_id,
        });
        setShowUPIPinModal(true);
      }
    }
    
    // Handle language change request
    // Use the same handleLanguageChange function that the dropdown uses
    // This ensures both AI and manual dropdown changes work identically
    if (lastAssistantMessage?.structuredData?.type === 'language_change') {
      const languageData = lastAssistantMessage.structuredData;
      
      // If language was actually changed, call the same function the dropdown uses
      if (languageData.changed && languageData.requested_language) {
        const newLang = languageData.requested_language;
        const messageId = lastAssistantMessage.id;
        
        // Check if we've already processed this language change for this message
        // This prevents re-processing when handleLanguageChange updates language state
        if (processedLanguageChangeRef.current !== messageId) {
          processedLanguageChangeRef.current = messageId;
          // Call handleLanguageChange - same function used by dropdown
          // It will handle all the state updates, TTS/listening stops, and event dispatching
          handleLanguageChange(newLang);
        }
      }
      // If user requested current language, response already handled by backend
    }
  }, [messages, upiConsentGiven, upiMode, isListening, isSpeaking, stopListening, stopSpeaking, markLanguageChanging, showUPIPinModal, resetTranscript, setInputText]);

  // Handle pending UPI message - show consent modal when pending message exists
  useEffect(() => {
    if (pendingUPIMessage && !upiConsentGiven) {
      // Mark that modal was opened by pending message (not button)
      setUpiConsentModalOpenedByButton(false);
      // Force show the consent modal
      setShowUPIConsentModal(true);
    } else if (pendingUPIMessage && upiConsentGiven) {
      // Consent was given, clear pending message (it should have been added to chat in handleUPIConsentAccept)
      setPendingUPIMessage(null);
    }
    // Don't close modal if it's opened via button click - only handle pending messages
  }, [pendingUPIMessage, upiConsentGiven, upiConsentModalOpenedByButton]);

  // Show speech errors
  useEffect(() => {
    if (speechError) {
      console.warn('Speech error:', speechError);
      alert(speechError); // Show error to user
    }
  }, [speechError]);

  // Function to check voice binding status
  const checkVoiceBindingStatus = useCallback(() => {
    if (!session?.accessToken) {
      setCheckingVoiceBinding(false);
      setHasVoiceBinding(false);
      return;
    }
    let mounted = true;
    setCheckingVoiceBinding(true);
    listDeviceBindings({ accessToken: session.accessToken })
      .then((data) => {
        if (!mounted) return;
        // Check if any ACTIVE (non-revoked) device binding has voice signature
        // Only count bindings that are trusted (not revoked) and have voice signature
        const hasVoice = data.some(
          (binding) => 
            binding.voiceSignaturePresent === true && 
            binding.trustLevel !== "revoked"
        );
        setHasVoiceBinding(hasVoice);
      })
      .catch((error) => {
        if (!mounted) return;
        // Don't show error for voice check, just assume no voice
        setHasVoiceBinding(false);
      })
      .finally(() => {
        if (mounted) setCheckingVoiceBinding(false);
      });
    return () => {
      mounted = false;
    };
  }, [session?.accessToken]);

  // Check voice binding status on mount
  useEffect(() => {
    checkVoiceBindingStatus();
  }, [checkVoiceBindingStatus]);

  // Refresh voice binding status when page becomes visible (user returns from device binding page)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && session?.accessToken) {
        // Small delay to ensure any pending operations complete
        const timeoutId = setTimeout(() => {
          checkVoiceBindingStatus();
        }, 500);
        return () => clearTimeout(timeoutId);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [checkVoiceBindingStatus, session?.accessToken]);

  // Cleanup: Stop speech when voice mode is disabled
  useEffect(() => {
    if (!isVoiceModeEnabled) {
      stopSpeaking();
    }
  }, [isVoiceModeEnabled, stopSpeaking]);

  // Listen for language changes from other sources (like other tabs)
  // Use handleLanguageChange for consistency, but only if language actually changed
  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === PREFERRED_LANGUAGE_KEY) {
        const newLang = event.newValue || DEFAULT_LANGUAGE;
        // Use handleLanguageChange for consistency - it handles all the cleanup
        if (newLang !== language) {
          handleLanguageChange(newLang);
        }
      }
    };

    // Note: We don't listen to "languageChanged" events here because:
    // 1. handleLanguageChange already dispatches this event for OTHER components
    // 2. If we listen to it and call handleLanguageChange again, we'd create a loop
    // 3. The dropdown and other components listen to this event, but Chat component
    //    uses handleLanguageChange directly, which is the single source of truth

    window.addEventListener("storage", handleStorageChange);
    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [language, handleLanguageChange]);

  if (!session.authenticated) {
    return <Navigate to="/" replace />;
  }

  const handleVoiceInput = () => {
    if (!isSpeechSupported) {
      alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isLanguageComingSoon) {
      alert('Voice input for this language is coming soon. Please use English or Hindi.');
      return;
    }

    // CRITICAL: User manually clicked mic button - this is a user override
    // Stop speaking/thinking and start recording immediately (user wants to interrupt)
    const wasSpeaking = isSpeaking;
    const wasTyping = isTyping;
    
    if (isSpeaking && stopSpeaking) {
      // User override: Stopping TTS - user wants to speak
      stopSpeaking();
    }
    
    // Note: We can't stop typing directly, but we'll start listening anyway
    // The voice mode hook will handle stopping listening if typing continues
    
    // NORMAL MODE: Simple toggle - completely independent of voice mode
    if (!isVoiceModeEnabled) {
      if (isListening) {
        stopListening();
      } else {
        // User override: start recording even if AI is thinking/speaking
        startListening();
      }
      return;
    }

    // VOICE MODE: Simple logic - if listening, stop; if not listening, start
    if (isListening) {
      stopListening();
      return;
    }

    // User clicked to START recording - clear all flags and start
    // This is simple: user wants to record, so let them record
    if (clearManualStopFlags) {
      clearManualStopFlags();
    }
    if (resetManualStop) {
      resetManualStop();
    }
    startListening();
  };

  const handleVoiceModeToggle = () => {
    if (!isSpeechSupported || !isTTSSupported) {
      alert('Voice mode requires browser support for both speech recognition and text-to-speech. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isLanguageComingSoon) {
      alert('Voice mode is not available for this language yet. Please use English or Hindi.');
      return;
    }

    setIsVoiceModeEnabled((prev) => !prev);
  };

  const handleUPIModeToggle = () => {
    if (upiMode) {
      // Deactivate UPI mode
      // Deactivating UPI mode
      setUpiMode(false);
      setUpiConsentGiven(false);
      localStorage.removeItem('upi_consent_given');
      sessionStorage.removeItem('upi_consent_given_session');
      setShowUPIConsentModal(false);
      setShowUPIPinModal(false);
      setUpiPaymentDetails(null);
      pinModalOpenedByUserRef.current = false;
    } else {
      // Activate UPI mode - show consent modal FIRST if not given
      if (!upiConsentGiven) {
        // Show consent modal first, don't activate yet
        setUpiConsentModalOpenedByButton(true);
        setTimeout(() => {
          setShowUPIConsentModal(true);
        }, 0);
      } else {
        // Consent already given, safe to activate
        setUpiMode(true);
      }
    }
  };

  // Handle UPI PIN confirmation
  const handleUPIPinConfirm = async (pin) => {
    // Handle UPI PIN confirmation
    
    if (!upiPaymentDetails) {
      console.error('No payment details found');
      return;
    }
    
    try {
      // Verify PIN with backend - use API_BASE_URL from client.js
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
      const response = await fetch(`${API_BASE_URL}/api/v1/upi/verify-pin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.accessToken}`,
        },
        body: JSON.stringify({
          pin,
          paymentDetails: upiPaymentDetails,
        }),
      });
      
      const data = await response.json();
      
      // UPI PIN verified successfully
      
      if (!response.ok) {
        // Handle different error types
        const errorDetail = data?.detail?.error || data?.error || {};
        const errorCode = errorDetail.code || '';
        const errorMessage = errorDetail.message || data?.detail?.message || 'Payment failed. Please try again.';
        
        console.error('UPI PIN verification failed:', response.status, errorMessage, errorCode);
        
        // If UPI ID not found, show specific error and close modal
        if (errorCode === 'upi_id_not_found' || errorCode === 'recipient_not_found') {
          setShowUPIPinModal(false);
          setUpiPaymentDetails(null);
          pinModalOpenedByUserRef.current = false;
          
          const errorMsg = language === 'hi-IN'
            ? `UPI ID नहीं मिला: ${upiPaymentDetails?.recipient || ''}. कृपया UPI ID जांचें और पुनः प्रयास करें।`
            : `UPI ID not found: ${upiPaymentDetails?.recipient || ''}. Please verify the UPI ID and try again.`;
          
          addAssistantMessage(errorMsg, null, null, language);
          return;
        }
        
        // For other errors (like PIN verification), throw to be caught by catch block
        throw new Error(errorMessage);
      }
      
      if (!data.data?.success) {
        // PIN verification failed - modal stays open, error shown in modal
        console.error('PIN verification failed:', data);
        // Don't close modal on error - let the modal show the error
        return;
      }
      
      // Store payment details before clearing (needed for both balance check and payment)
      const paymentDetails = { ...upiPaymentDetails };
      
      // Close PIN modal immediately on success
      setShowUPIPinModal(false);
      setUpiPaymentDetails(null); // Clear payment details
      pinModalOpenedByUserRef.current = false; // Reset user action flag
      
      // Handle balance check operation FIRST (before payment handling)
      if (paymentDetails.operation === 'balance_check') {
        console.log('Balance check operation detected, response data:', data.data);
        
        if (data.data?.balance) {
          const balanceInfo = data.data.balance;
          const balanceMessage = language === 'hi-IN'
            ? `आपके खाते की शेष राशि: ₹${parseFloat(balanceInfo.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
            : `Your account balance: ₹${parseFloat(balanceInfo.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
          
          console.log('Adding balance message:', balanceMessage);
          
          // Add balance message
          addAssistantMessage(balanceMessage, null, {
            type: 'balance',
            accounts: [{
              accountNumber: balanceInfo.account_number,
              accountType: balanceInfo.account_type,
              balance: balanceInfo.balance,
              currency: balanceInfo.currency || 'INR'
            }]
          }, language);
          return; // Exit early after handling balance check
        } else {
          console.error('Balance data not found in response:', data.data);
          // Fallback: show error message
          addAssistantMessage(
            language === 'hi-IN' 
              ? 'शेष राशि प्राप्त करने में त्रुटि हुई। कृपया पुनः प्रयास करें।'
              : 'Error fetching balance. Please try again.',
            null,
            null,
            language
          );
          return; // Exit early after error
        }
      }
      
      // Handle payment operations (only if not balance check)
      // Check if receipt is returned (for payments)
      if (data.data?.receipt) {
        // Payment successful - remove payment card and show only success message (no receipt card)
        const receipt = data.data.receipt;
        const successMessage = language === 'hi-IN'
          ? `₹${parseFloat(receipt.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ${receipt.beneficiaryName || paymentDetails?.recipient} को सफलतापूर्वक भेज दिया गया है।`
          : `Successfully sent ₹${parseFloat(receipt.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })} to ${receipt.beneficiaryName || paymentDetails?.recipient}.`;
        
        // Remove UPI payment card from messages
        setMessages((prev) => {
          return prev.map((msg) => {
            // Remove structured data cards (especially upi_payment_card) from assistant messages
            if (msg.role === 'assistant' && msg.structuredData?.type === 'upi_payment_card') {
              const { structuredData, ...rest } = msg;
              return rest;
            }
            return msg;
          });
        });
        
        // Add success message only (no receipt card)
        addAssistantMessage(successMessage, null, null, language);
      } else if (paymentDetails && !paymentDetails.operation) {
        // Fallback: send message to trigger payment processing (only if not a balance check)
        const paymentMessage = `Confirm UPI payment: ₹${paymentDetails.amount} to ${paymentDetails.recipient}${paymentDetails.remarks ? ` for ${paymentDetails.remarks}` : ''}`;
        await sendMessage(paymentMessage);
      }
    } catch (error) {
      console.error('UPI PIN verification error:', error);
      alert(upiStrings.paymentFailed || 'Payment failed. Please try again.');
    }
  };

  // Handle UPI consent
  const handleUPIConsentAccept = () => {
    // UPI consent accepted
    // User accepted consent - now activate UPI mode
    setUpiConsentGiven(true);
    localStorage.setItem('upi_consent_given', 'true');
    sessionStorage.setItem('upi_consent_given_session', 'true'); // Track in session storage too
    setShowUPIConsentModal(false);
    setUpiConsentModalOpenedByButton(false); // Reset button flag
    setUpiMode(true); // Activate UPI mode after consent is accepted
    
    // If there's a pending UPI message, add it to chat now
    if (pendingUPIMessage) {
      // Consent accepted - adding pending UPI message
      addAssistantMessage(
        pendingUPIMessage.text || pendingUPIMessage.content,
        pendingUPIMessage.statementData,
        pendingUPIMessage.structuredData,
        language
      );
      
      // Handle UPI mode activation
      if (pendingUPIMessage.structuredData?.type === 'upi_mode_activation') {
        // UPI mode is already activated above, just ensure it's set
        // UPI mode activated after consent
      }
      
      // Handle balance check if present
      if (pendingUPIMessage.structuredData?.type === 'upi_balance_check') {
        const balanceData = pendingUPIMessage.structuredData;
        // If account selection is pending, don't show PIN modal yet
        if (!balanceData.pending_account_selection && balanceData.source_account_id) {
          setUpiPaymentDetails({
            operation: 'balance_check',
            sourceAccount: balanceData.source_account_number,
            sourceAccountId: balanceData.source_account_id,
          });
          setShowUPIPinModal(true);
        }
      }
      
      // Handle payment details if present
      if (pendingUPIMessage.structuredData?.type === 'upi_payment') {
        const paymentData = pendingUPIMessage.structuredData;
        if (paymentData.amount && paymentData.recipient_identifier) {
          setUpiPaymentDetails({
            amount: paymentData.amount,
            recipient: paymentData.recipient_identifier,
            sourceAccount: paymentData.source_account_number,
            remarks: paymentData.remarks,
          });
          setShowUPIPinModal(true);
        }
      }
      
      // Clear pending message
      setPendingUPIMessage(null);
    } else {
      // No pending message but consent accepted - just activate UPI mode
      // UPI consent accepted, no pending message
    }
  };

  // Handle UPI consent decline
  const handleUPIConsentDecline = () => {
    // User declined consent - do NOT activate UPI mode
    setShowUPIConsentModal(false);
    setUpiConsentModalOpenedByButton(false); // Reset button flag
    
    // Remove pending message and add a decline message instead
    if (pendingUPIMessage) {
      // Consent declined - removing pending message and adding decline message
      const declineMessage = language === 'hi-IN' 
        ? 'आपने UPI मोड को अस्वीकार कर दिया है। UPI भुगतान सुविधा उपलब्ध नहीं होगी।'
        : 'You have denied UPI mode. UPI payment feature will not be available.';
      addAssistantMessage(declineMessage, null, null, language);
      setPendingUPIMessage(null);
    } else {
      // If no pending message, just add a general denial message
      addAssistantMessage(upiStrings.upiConsentDenied || "You have denied UPI mode. UPI payment feature will not be available.", null, null, language);
    }
    
    // Ensure UPI mode is inactive and consent is not given
    setUpiMode(false);
    setUpiConsentGiven(false);
    localStorage.removeItem('upi_consent_given');
    sessionStorage.removeItem('upi_consent_given_session'); // Also remove from session storage
  };

  return (
    <div className="app-shell">
      <div className="app-content app-content--fullwidth">
        <div className="app-gradient app-gradient--fullwidth">
          <SunHeader
            subtitle={`${session.user.branch.name} · ${session.user.branch.city}`}
            actionSlot={
              <div className="chat-header-actions">
                <LanguageDropdown onSelect={handleLanguageChange} value={language} />
                <button
                  type="button"
                  className="ghost-btn ghost-btn--compact"
                  onClick={() => navigate("/profile")}
                >
                  {chatPageStrings.backToProfile || "← Back to Profile"}
                </button>
                <button type="button" className="ghost-btn ghost-btn--compact" onClick={onSignOut}>
                  {chatPageStrings.logOut || "Log out"}
                </button>
              </div>
            }
          />
          <main className={`chat-container ${isVoiceModeEnabled ? 'chat-container--voice-mode' : ''}`}>
            <div className="chat-main">
              {/* Speaking indicator */}
              {isSpeaking && (
                <div className="chat-speaking-indicator">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z"
                      fill="currentColor"
                      opacity="0.2"
                    />
                    <path
                      d="M12 6V12L16 14"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div>
                    <div>{chatCopy.chatInput?.hints?.speaking || chatPageStrings.assistantSpeaking || "Assistant is speaking..."}</div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '0.25rem' }}>
                      Voice: Vaani by Sun National Bank
                    </div>
                  </div>
                </div>
              )}

              <div className="chat-messages">
                {messages.map((message) => (
                  <ChatMessage 
                    key={message.id} 
                    message={message} 
                    userName={session.user.fullName}
                    language={language}
                    session={session}
                    onFeedback={(feedbackData) => {
                      console.log('Feedback received:', feedbackData);
                      // In production, send to backend API
                    }}
                    onAddAssistantMessage={addAssistantMessage}
                    onSendMessage={sendMessage}
                    onShowUPIPinModal={(show) => {
                      if (show) {
                        // Mark that modal was opened by user action
                        pinModalOpenedByUserRef.current = true;
                      }
                      setShowUPIPinModal(show);
                    }}
                    onSetUpiPaymentDetails={setUpiPaymentDetails}
                  />
                ))}
                {isTyping && <TypingIndicator language={language} />}
                <div ref={messagesEndRef} />
              </div>

              {/* QR Code Upload Button - Show when UPI mode is active */}
              {upiMode && (
                <div style={{ 
                  padding: '0.75rem 1rem', 
                  background: 'rgba(255, 154, 60, 0.1)', 
                  borderTop: '1px solid rgba(255, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}>
                  <label 
                    htmlFor="upi-qr-upload"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      cursor: 'pointer',
                      padding: '0.5rem 1rem',
                      background: 'white',
                      border: '1px solid rgba(255, 154, 60, 0.3)',
                      borderRadius: '8px',
                      fontSize: '0.875rem',
                      fontWeight: 500,
                      color: '#ff7a59',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = '#fff5f0';
                      e.currentTarget.style.borderColor = '#ff7a59';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'white';
                      e.currentTarget.style.borderColor = 'rgba(255, 154, 60, 0.3)';
                    }}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="3" width="5" height="5" rx="1" stroke="currentColor" strokeWidth="2"/>
                      <rect x="16" y="3" width="5" height="5" rx="1" stroke="currentColor" strokeWidth="2"/>
                      <rect x="3" y="16" width="5" height="5" rx="1" stroke="currentColor" strokeWidth="2"/>
                      <path d="M11 11H13V13H11V11Z" fill="currentColor"/>
                      <path d="M11 15H13V17H11V15Z" fill="currentColor"/>
                      <path d="M15 11H17V13H15V11Z" fill="currentColor"/>
                      <path d="M15 15H17V17H15V15Z" fill="currentColor"/>
                      <path d="M19 11H21V13H19V11Z" fill="currentColor"/>
                    </svg>
                    {chatPageStrings.uploadQRCode || (language === 'hi-IN' ? 'QR कोड अपलोड करें' : 'Upload QR Code')}
                  </label>
                  <input
                    id="upi-qr-upload"
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      
                      try {
                        // Convert file to base64 and process QR code
                        const reader = new FileReader();
                        reader.onload = async (event) => {
                          const imageBase64 = event.target.result;
                          
                          try {
                            // Try to process QR code using jsQR (client-side)
                            const jsQR = (await import('jsqr')).default;
                            
                            // Create image element to decode QR code
                            const img = new Image();
                            img.onload = async () => {
                              // Create canvas to get image data
                              const canvas = document.createElement('canvas');
                              const ctx = canvas.getContext('2d');
                              canvas.width = img.width;
                              canvas.height = img.height;
                              ctx.drawImage(img, 0, 0);
                              
                              const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                              const qrCode = jsQR(imageData.data, imageData.width, imageData.height);
                              
                              if (qrCode) {
                                // QR code decoded successfully
                                const qrData = qrCode.data;
                                
                                // Parse UPI QR code format
                                // UPI QR codes typically contain: upi://pay?pa=<upi_id>&pn=<name>&am=<amount>&cu=INR
                                let upiAddress = null;
                                let amount = null;
                                let merchantName = null;
                                
                                if (qrData.includes('upi://') || qrData.includes('UPI://')) {
                                  // Parse UPI QR code
                                  const url = new URL(qrData);
                                  const params = new URLSearchParams(url.search);
                                  
                                  upiAddress = params.get('pa');
                                  merchantName = params.get('pn');
                                  const amountStr = params.get('am');
                                  
                                  if (amountStr) {
                                    amount = parseFloat(amountStr);
                                  }
                                } else if (qrData.includes('@')) {
                                  // Try to extract UPI ID directly
                                  const upiMatch = qrData.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)/);
                                  if (upiMatch) {
                                    upiAddress = upiMatch[1];
                                  }
                                }
                                
                                if (upiAddress) {
                                  // QR code processed successfully
                                  const result = {
                                    success: true,
                                    upi_address: upiAddress,
                                    amount: amount,
                                    merchant_name: merchantName,
                                  };
                                  
                                  // Clear all pending cards/messages from current session
                                  // Keep only the initial greeting and user messages, remove all assistant cards
                                  setMessages((prev) => {
                                    return prev.map((msg) => {
                                      // Remove structured data cards from assistant messages
                                      if (msg.role === 'assistant' && msg.structuredData) {
                                        const { structuredData, ...rest } = msg;
                                        return rest;
                                      }
                                      return msg;
                                    });
                                  });
                                  
                                  // Add user message showing QR was scanned
                                  const qrScannedMessage = language === 'hi-IN'
                                    ? `QR कोड स्कैन किया गया`
                                    : `QR code scanned`;
                                  addUserMessage(qrScannedMessage, language);
                                  
                                  // Directly show UPI payment card with QR data pre-filled
                                  // Don't send message to backend - just show the card
                                  const qrResponseMessage = language === 'hi-IN'
                                    ? `QR कोड से UPI पता प्राप्त किया${result.amount ? `, राशि: ₹${result.amount}` : ''}। कृपया भुगतान जारी रखें।`
                                    : `UPI address extracted from QR code${result.amount ? `, Amount: ₹${result.amount}` : ''}. Please proceed with payment.`;
                                  
                                  addAssistantMessage(qrResponseMessage, null, {
                                    type: 'upi_payment_card',
                                    intent: 'upi_payment_request',
                                    message: qrScannedMessage,
                                    amount: result.amount || null,
                                    recipient_identifier: result.upi_address,
                                    remarks: result.merchant_name || null,
                                    source_account_id: null, // Let user select account
                                    source_account_number: null,
                                    accounts: null, // Will be loaded by UPIPaymentFlow component
                                  }, language);
                                } else {
                                  // Could not extract UPI address
                                  addAssistantMessage(
                                    language === 'hi-IN'
                                      ? 'QR कोड से UPI पता निकाला नहीं जा सका। कृपया पुनः प्रयास करें।'
                                      : 'Could not extract UPI address from QR code. Please try again.',
                                    null,
                                    null,
                                    language
                                  );
                                }
                              } else {
                                // QR code not found in image, try backend processing
                                try {
                                  const { processQRCode } = await import('../api/client.js');
                                  const result = await processQRCode({
                                    imageBase64,
                                    language,
                                  });
                                  
                                  if (result?.success && result?.upi_address) {
                                    // QR code processed successfully
                                    
                                    // Clear all pending cards/messages from current session
                                    // Keep only the initial greeting and user messages, remove all assistant cards
                                    setMessages((prev) => {
                                      return prev.map((msg) => {
                                        // Remove structured data cards from assistant messages
                                        if (msg.role === 'assistant' && msg.structuredData) {
                                          const { structuredData, ...rest } = msg;
                                          return rest;
                                        }
                                        return msg;
                                      });
                                    });
                                    
                                    // Add user message showing QR was scanned
                                    const qrScannedMessage = language === 'hi-IN'
                                      ? `QR कोड स्कैन किया गया`
                                      : `QR code scanned`;
                                    addUserMessage(qrScannedMessage, language);
                                    
                                    // Directly show UPI payment card with QR data pre-filled
                                    // Don't send message to backend - just show the card
                                    const qrResponseMessage = language === 'hi-IN'
                                      ? `QR कोड से UPI पता प्राप्त किया${result.amount ? `, राशि: ₹${result.amount}` : ''}। कृपया भुगतान जारी रखें।`
                                      : `UPI address extracted from QR code${result.amount ? `, Amount: ₹${result.amount}` : ''}. Please proceed with payment.`;
                                    
                                    addAssistantMessage(qrResponseMessage, null, {
                                      type: 'upi_payment_card',
                                      intent: 'upi_payment_request',
                                      message: qrScannedMessage,
                                      amount: result.amount || null,
                                      recipient_identifier: result.upi_address,
                                      remarks: result.merchant_name || null,
                                      source_account_id: null, // Let user select account
                                      source_account_number: null,
                                      accounts: null, // Will be loaded by UPIPaymentFlow component
                                    }, language);
                                  } else {
                                    // QR code processing failed
                                    addAssistantMessage(
                                      result?.message || (language === 'hi-IN'
                                        ? 'QR कोड से UPI पता निकाला नहीं जा सका। कृपया पुनः प्रयास करें।'
                                        : 'Could not extract UPI address from QR code. Please try again.'),
                                      null,
                                      null,
                                      language
                                    );
                                  }
                                } catch (backendError) {
                                  console.error('Backend QR processing error:', backendError);
                                  addAssistantMessage(
                                    language === 'hi-IN'
                                      ? 'QR कोड प्रसंस्करण में त्रुटि। कृपया पुनः प्रयास करें।'
                                      : 'Error processing QR code. Please try again.',
                                    null,
                                    null,
                                    language
                                  );
                                }
                              }
                            };
                            img.src = imageBase64;
                          } catch (error) {
                            console.error('QR code processing error:', error);
                            addAssistantMessage(
                              language === 'hi-IN'
                                ? 'QR कोड प्रसंस्करण में त्रुटि। कृपया पुनः प्रयास करें।'
                                : 'Error processing QR code. Please try again.',
                              null,
                              null,
                              language
                            );
                          }
                        };
                        
                        reader.onerror = () => {
                          addAssistantMessage(
                            language === 'hi-IN'
                              ? 'छवि पढ़ने में त्रुटि।'
                              : 'Error reading image.',
                            null,
                            null,
                            language
                          );
                        };
                        
                        reader.readAsDataURL(file);
                      } catch (error) {
                        console.error('QR code upload error:', error);
                        addAssistantMessage(
                          language === 'hi-IN'
                            ? 'QR कोड अपलोड करने में त्रुटि।'
                            : 'Error uploading QR code.'
                        );
                      }
                      
                      // Reset input
                      e.target.value = '';
                    }}
                  />
                </div>
              )}

              <ChatInput
                inputText={inputText}
                setInputText={setInputText}
                isTyping={isTyping}
                isListening={isListening}
                isSpeechSupported={isSpeechSupported}
                isLanguageComingSoon={isLanguageComingSoon}
                isSpeaking={isSpeaking}
                isVoiceModeEnabled={isVoiceModeEnabled}
                isVoiceSecured={isVoiceSecured}
                onSubmit={handleSendMessage}
                onVoiceClick={handleVoiceInput}
                onVoiceModeToggle={handleVoiceModeToggle}
                onVoiceEnrollmentClick={() => setIsVoiceEnrollmentModalOpen(true)}
                inputRef={inputRef}
                copy={chatCopy.chatInput}
              />
            </div>

            <ChatSidebar 
              isSpeechSupported={isSpeechSupported} 
              onQuickAction={handleQuickAction}
              copy={chatCopy}
              upiMode={upiMode}
              isVoiceModeEnabled={isVoiceModeEnabled}
              isVoiceSecured={isVoiceSecured}
              checkingVoiceBinding={checkingVoiceBinding}
              onUPIModeToggle={handleUPIModeToggle}
              onVoiceModeToggle={handleVoiceModeToggle}
              onVoiceEnrollmentClick={() => setIsVoiceEnrollmentModalOpen(true)}
              pageStrings={pageStrings}
              upiStrings={upiStrings}
            />
          </main>
        </div>
      </div>

      {/* UPI Consent Modal */}
      <UPIConsentModal
        isOpen={showUPIConsentModal}
        onClose={handleUPIConsentDecline}
        onAccept={handleUPIConsentAccept}
        strings={upiStrings}
        language={language}
      />

      {/* UPI PIN Modal */}
      <UPIPinModal
        isOpen={showUPIPinModal}
        onClose={() => {
          setShowUPIPinModal(false);
          setUpiPaymentDetails(null);
          pinModalOpenedByUserRef.current = false;
        }}
        onConfirm={handleUPIPinConfirm}
        paymentDetails={upiPaymentDetails}
        strings={upiStrings}
        language={language}
        onPaymentDetailsChange={(updatedDetails) => {
          setUpiPaymentDetails(updatedDetails);
        }}
      />

      {/* Voice Enrollment Modal */}
      <VoiceEnrollmentModal
        isOpen={isVoiceEnrollmentModalOpen}
        onClose={() => setIsVoiceEnrollmentModalOpen(false)}
        onConfirm={() => {
          setIsVoiceEnrollmentModalOpen(false);
          navigate("/device-binding");
        }}
        strings={{
          addVoiceToAccount: pageStrings.profile.addVoiceToAccount,
          addVoicePrompt: pageStrings.profile.addVoicePrompt,
          addVoicePromptDescription: pageStrings.profile.addVoicePromptDescription,
          cancel: pageStrings.profile.cancel,
          okay: pageStrings.profile.okay,
        }}
      />
    </div>
  );
};

Chat.propTypes = {
  session: PropTypes.shape({
    authenticated: PropTypes.bool.isRequired,
    user: PropTypes.shape({
      fullName: PropTypes.string.isRequired,
      branch: PropTypes.shape({
        name: PropTypes.string.isRequired,
        city: PropTypes.string.isRequired,
      }).isRequired,
    }),
    accessToken: PropTypes.string,
  }).isRequired,
  onSignOut: PropTypes.func.isRequired,
};

export default Chat;
