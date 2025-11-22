import { useEffect, useRef, useCallback } from 'react';

/**
 * Hook for orchestrating voice mode behavior
 * Handles auto-listening, auto-reading responses, and auto-sending
 */
export const useVoiceMode = ({
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
  onAutoSend,
  upiMode = false, // UPI mode state
  showUPIConsentModal = false, // UPI consent modal state
  showUPIPinModal = false, // UPI PIN modal state
  clearManualStopFlags, // Function to clear manual stop flags in speech recognition
}) => {
  const lastMessageRef = useRef(null);

  // Track if user manually stopped (to prevent auto-restart) - ONLY for voice mode
  const manualStopRef = useRef(false);
  const lastListeningStateRef = useRef(isListening);
  
  // Track when user explicitly wants to start recording (prevents false manual stop detection)
  const userWantsToStartRef = useRef(false);
  
  // Track when speaking stops to prevent immediate auto-start
  // This prevents recording from starting too quickly after TTS stops
  const speakingJustStoppedRef = useRef(false);
  const speakingStopTimeoutRef = useRef(null);
  const lastSpeakingStateRef = useRef(isSpeaking);
  
  // Expose function to reset manual stop flag (for user override via mic button)
  const resetManualStop = useCallback(() => {
    // CRITICAL: Clear manual stop flags in speech recognition hook FIRST
    // This ensures isManuallyStoppedRef is cleared before we try to start
    if (clearManualStopFlags) {
      clearManualStopFlags();
    }
    
    // CRITICAL: Set flag to indicate user wants to start - this prevents false manual stop detection
    userWantsToStartRef.current = true;
    manualStopRef.current = false;
    // Also clear speaking stop delay if user wants to start immediately
    speakingJustStoppedRef.current = false;
    if (speakingStopTimeoutRef.current) {
      clearTimeout(speakingStopTimeoutRef.current);
      speakingStopTimeoutRef.current = null;
    }
    // Clear the flag after a short delay to allow startListening to complete
    setTimeout(() => {
      userWantsToStartRef.current = false;
    }, 500);
  }, [clearManualStopFlags]);
  
  // Voice Mode: Auto-start listening when enabled and not speaking
  // IMPORTANT: This effect ONLY runs when voice mode is enabled
  // Normal mode is completely isolated and independent
  useEffect(() => {
    // Early return if voice mode is not enabled - don't interfere with normal mode
    if (!isVoiceModeEnabled) {
      // Reset manual stop flag when voice mode is disabled
      manualStopRef.current = false;
      return;
    }
    
    // Detect if listening was manually stopped (transition from true to false)
    const wasListening = lastListeningStateRef.current;
    const isNowListening = isListening;
    
    // CRITICAL: If user explicitly wants to start, don't detect this as a manual stop
    // This prevents race condition where user clicks to start but system thinks it's a stop
    if (userWantsToStartRef.current) {
      // User is trying to start - don't interfere
      lastListeningStateRef.current = isListening;
      return;
    }
    
    // If we transitioned from listening to not listening, and it wasn't due to speaking/typing,
    // it might be a manual stop
    if (wasListening && !isNowListening && !isSpeaking && !isTyping) {
      // Check if this looks like a manual stop (user clicked mic button to stop)
      // We'll use a short delay to detect this
      const checkManualStop = setTimeout(() => {
        // Only set manual stop if user is NOT trying to start and still not listening
        if (!isListening && isVoiceModeEnabled && !isSpeaking && !isTyping && !userWantsToStartRef.current) {
          // Still not listening after a moment - likely manual stop
          manualStopRef.current = true;
        }
      }, 200);
      
      return () => clearTimeout(checkManualStop);
    }
    
    // Reset manual stop flag when we successfully start listening
    if (!wasListening && isNowListening) {
      manualStopRef.current = false;
      userWantsToStartRef.current = false; // Clear user intent flag when listening starts
    }
    
    lastListeningStateRef.current = isListening;
    
    // Track when speaking stops to prevent immediate auto-start
    const wasSpeaking = lastSpeakingStateRef.current;
    
    if (isSpeaking && !wasSpeaking) {
      // Speaking just started - clear any stop flags
      speakingJustStoppedRef.current = false;
      if (speakingStopTimeoutRef.current) {
        clearTimeout(speakingStopTimeoutRef.current);
        speakingStopTimeoutRef.current = null;
      }
    } else if (!isSpeaking && wasSpeaking) {
      // Speaking just stopped - set a flag and delay before allowing auto-start
      speakingJustStoppedRef.current = true;
      console.log('⏸️ Voice mode: TTS just stopped - waiting before auto-start');
      
      // Clear any existing timeout
      if (speakingStopTimeoutRef.current) {
        clearTimeout(speakingStopTimeoutRef.current);
      }
      
      // Wait 500ms after speaking stops before allowing auto-start
      // This ensures TTS is fully stopped and prevents recording AI's voice
      speakingStopTimeoutRef.current = setTimeout(() => {
        speakingJustStoppedRef.current = false;
        console.log('✅ Voice mode: TTS stop delay complete - ready for auto-start');
      }, 500);
    }
    
    // Update speaking state ref
    lastSpeakingStateRef.current = isSpeaking;
    
    // CRITICAL: Stop listening when AI is thinking (isTyping) or speaking (isSpeaking)
    // This prevents recording AI's voice or background processing sounds
    if (isTyping && isListening) {
      console.log('🛑 Voice mode: Stopping microphone during AI thinking (preventing recording)');
      stopListening();
      manualStopRef.current = false; // Don't treat this as manual stop
    }
    
    if (isSpeaking && isListening) {
      console.log('🛑 Voice mode: Stopping microphone during speech (preventing feedback)');
      stopListening();
      manualStopRef.current = false; // Don't treat this as manual stop
    }
    
    // CRITICAL: Stop listening if UPI modals are open - user needs to interact with modal first
    if ((showUPIConsentModal || showUPIPinModal) && isListening) {
      console.log('🛑 Voice mode: Stopping microphone - UPI modal is open (user interaction required)');
      stopListening();
      manualStopRef.current = true; // Prevent auto-restart while modal is open
      return; // Don't proceed with auto-start logic
    }

    // Auto-start logic - ONLY when voice mode is enabled
    // CRITICAL: Never start listening while AI is thinking, speaking, immediately after speaking stops, or when UPI modals are open
    if (!isLanguageComingSoon && !isSpeaking && !isTyping && !speakingJustStoppedRef.current && !showUPIConsentModal && !showUPIPinModal) {
      if (!isListening && !manualStopRef.current) {
        console.log('🎤 Voice mode: Auto-starting microphone');
        startListening();
      } else if (!isListening && manualStopRef.current) {
        console.log('⏸️ Voice mode: Skipping auto-start (manual stop detected)');
      }
    } else if (isTyping) {
      // Don't auto-start while AI is thinking
      console.log('⏸️ Voice mode: Waiting for AI to finish thinking before auto-starting');
    } else if (isSpeaking) {
      // Don't auto-start while speaking - wait for speaking to finish
      console.log('⏸️ Voice mode: Waiting for TTS to finish before auto-starting');
    } else if (speakingJustStoppedRef.current) {
      // Just stopped speaking - don't auto-start yet, wait for delay
      if (isListening) {
        console.log('🛑 Voice mode: Stopping microphone (TTS just stopped, waiting for delay)');
        stopListening();
      }
      console.log('⏸️ Voice mode: Waiting for TTS stop delay before auto-starting');
    } else if (showUPIConsentModal || showUPIPinModal) {
      // UPI modal is open - don't auto-start, user must interact first
      if (isListening) {
        console.log('🛑 Voice mode: Stopping microphone - UPI modal is open');
        stopListening();
      }
      console.log('⏸️ Voice mode: UPI modal open - waiting for user interaction');
    }
  }, [
    isVoiceModeEnabled,
    isSpeaking,
    isTyping,
    isListening,
    isLanguageComingSoon,
    startListening,
    stopListening,
    showUPIConsentModal,
    showUPIPinModal,
  ]);

  // Voice Mode: Read assistant messages aloud
  useEffect(() => {
    if (isVoiceModeEnabled && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];

      // Check if this is a new assistant message
      if (lastMessage.role === 'assistant' && lastMessage.id !== lastMessageRef.current) {
        lastMessageRef.current = lastMessage.id;

        // CRITICAL: Check if this is a UPI-related message that requires user interaction
        // UPI consent modals, PIN modals, or payment cards should NOT trigger auto-recording
        const isUPIInteractionMessage = lastMessage.structuredData && (
          lastMessage.structuredData.type === 'upi_mode_activation' ||
          lastMessage.structuredData.type === 'upi_payment_card' ||
          lastMessage.structuredData.type === 'upi_payment' ||
          lastMessage.structuredData.type === 'upi_balance_check'
        );

        // CRITICAL: Stop listening FIRST before clearing transcript
        // This prevents any AI speech from being captured
        if (isListening) {
          console.log('🛑 Voice mode: Stopping listening before AI speaks');
          stopListening();
        }

        // CRITICAL: Clear transcript IMMEDIATELY after stopping listening
        // This ensures no AI speech gets into the transcript
        resetTranscript();
        setInputText('');

        // Wait a moment to ensure listening is fully stopped before starting TTS
        // This prevents any audio feedback from being captured
        setTimeout(() => {
          console.log('🔊 Voice mode: Reading assistant message', { isUPIInteractionMessage });
          speak(lastMessage.content, () => {
            console.log('✅ Voice mode: Finished reading, ready for next input');
            // Clear transcript again after speaking to ensure no AI speech was captured
            resetTranscript();
            setInputText('');
            
            // CRITICAL: For UPI interaction messages, DO NOT auto-restart listening
            // BUT: Allow user to manually start recording by clicking mic button
            // The resetManualStop() function will clear the manual stop flag when user clicks
            if (isUPIInteractionMessage) {
              console.log('🛑 Voice mode: UPI interaction message - preventing auto-restart, but user can manually start');
              // Set manual stop flag to prevent auto-restart, but user can override by clicking mic button
              // The resetManualStop() function will clear this flag when called from handleVoiceInput
              manualStopRef.current = true;
              // Also set speaking just stopped to add extra delay
              speakingJustStoppedRef.current = true;
              // Clear the delay after a longer period (3 seconds) for UPI interactions
              if (speakingStopTimeoutRef.current) {
                clearTimeout(speakingStopTimeoutRef.current);
              }
              speakingStopTimeoutRef.current = setTimeout(() => {
                speakingJustStoppedRef.current = false;
                // Note: manual stop flag stays true until user manually clicks mic button
                // This prevents auto-restart but allows manual override
                console.log('⏸️ Voice mode: UPI interaction delay complete, manual stop remains (user can click mic to start)');
              }, 3000); // Longer delay for UPI interactions
            }
            // For non-UPI messages, auto-restart listening (handled by useEffect above)
          });
        }, 100); // Small delay to ensure listening is fully stopped
      }
    }
  }, [messages, isVoiceModeEnabled, speak, isListening, stopListening, resetTranscript, setInputText]);

  // Voice Mode: Auto-send when transcript is complete
  useEffect(() => {
    if (isVoiceModeEnabled && fullTranscript && !isSpeaking && !isTyping) {
      // CRITICAL: Check if transcript contains AI's own speech patterns
      // Common AI responses that should NOT be sent as user messages
      const aiSpeechPatterns = [
        "sure! i'll now speak in english",
        "how can i help you",
        "ठीक है! अब मैं हिंदी में बात करूंगी",
        "मैं आपकी कैसे मदद कर सकती हूं",
        "i'm vaani",
        "your banking copilot",
        "good evening",
        "good morning",
        "good afternoon",
        // UPI-related AI responses
        "upi mode",
        "upi payment",
        "upi consent",
        "upi pin",
        "enter upi pin",
        "upi id",
        "upi address",
        "upi मोड",
        "upi भुगतान",
        "upi पिन",
        "upi आईडी",
        "upi पता",
        "we have six options available",
        "please select based on your requirement",
        "वे हैव सिक्स ऑप्शंस अवेलेबल",
        "प्लीज सिलेक्ट बेस्ड ओं योररिक्वायरमेंट",
        "six options available",
        "select based on requirement"
      ];
      
      const transcriptLower = fullTranscript.toLowerCase().trim();
      const containsAISpeech = aiSpeechPatterns.some(pattern => 
        transcriptLower.includes(pattern.toLowerCase())
      );
      
      if (containsAISpeech) {
        console.log('🚫 Voice mode: Detected AI speech in transcript - ignoring');
        resetTranscript();
        setInputText('');
        return;
      }
      
      // Wait a moment to see if user continues speaking
      const timer = setTimeout(() => {
        if (fullTranscript.trim() && !isSpeaking && !isTyping) {
          // Double-check transcript doesn't contain AI speech
          const finalTranscriptLower = fullTranscript.toLowerCase().trim();
          const stillContainsAISpeech = aiSpeechPatterns.some(pattern => 
            finalTranscriptLower.includes(pattern.toLowerCase())
          );
          
          if (!stillContainsAISpeech) {
            console.log('📤 Voice mode: Auto-sending message');
            onAutoSend(new Event('submit'));
          } else {
            console.log('🚫 Voice mode: AI speech detected in final transcript - ignoring');
            resetTranscript();
            setInputText('');
          }
        }
      }, 1500); // 1.5 second delay for natural conversation

      return () => clearTimeout(timer);
    }
  }, [fullTranscript, isVoiceModeEnabled, isSpeaking, isTyping, onAutoSend, resetTranscript, setInputText]);

  // Cleanup: Stop speech and listening when voice mode is disabled
  useEffect(() => {
    if (!isVoiceModeEnabled) {
      if (isListening) {
        stopListening();
      }
      // Clear timeout on cleanup
      if (speakingStopTimeoutRef.current) {
        clearTimeout(speakingStopTimeoutRef.current);
        speakingStopTimeoutRef.current = null;
      }
      speakingJustStoppedRef.current = false;
    }
    
    // Cleanup timeout on unmount
    return () => {
      if (speakingStopTimeoutRef.current) {
        clearTimeout(speakingStopTimeoutRef.current);
      }
    };
  }, [isVoiceModeEnabled, isListening, stopListening]);
  
  // Return function to reset manual stop (for user override)
  return { resetManualStop };
};
