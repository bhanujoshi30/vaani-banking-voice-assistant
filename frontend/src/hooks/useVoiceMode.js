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
}) => {
  const lastMessageRef = useRef(null);

  // Track if user manually stopped (to prevent auto-restart) - ONLY for voice mode
  const manualStopRef = useRef(false);
  const lastListeningStateRef = useRef(isListening);
  
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
    
    // If we transitioned from listening to not listening, and it wasn't due to speaking/typing,
    // it might be a manual stop
    if (wasListening && !isNowListening && !isSpeaking && !isTyping) {
      // Check if this looks like a manual stop (user clicked mic button)
      // We'll use a short delay to detect this
      const checkManualStop = setTimeout(() => {
        if (!isListening && isVoiceModeEnabled && !isSpeaking && !isTyping) {
          // Still not listening after a moment - likely manual stop
          console.log('🛑 Voice mode: Detected manual stop - preventing auto-restart');
          manualStopRef.current = true;
        }
      }, 200);
      
      return () => clearTimeout(checkManualStop);
    }
    
    // Reset manual stop flag when we successfully start listening
    if (!wasListening && isNowListening) {
      manualStopRef.current = false;
    }
    
    lastListeningStateRef.current = isListening;
    
    // Auto-start logic - ONLY when voice mode is enabled
    if (!isLanguageComingSoon && !isSpeaking && !isTyping) {
      if (!isListening && !manualStopRef.current) {
        console.log('🎤 Voice mode: Auto-starting microphone');
        startListening();
      } else if (!isListening && manualStopRef.current) {
        console.log('⏸️ Voice mode: Skipping auto-start (manual stop detected)');
      }
    } else if (isSpeaking && isListening) {
      // Stop listening while speaking to prevent feedback
      console.log('🛑 Voice mode: Stopping microphone during speech');
      stopListening();
      manualStopRef.current = false; // Don't treat this as manual stop
    }
  }, [
    isVoiceModeEnabled,
    isSpeaking,
    isTyping,
    isListening,
    isLanguageComingSoon,
    startListening,
    stopListening,
  ]);

  // Voice Mode: Read assistant messages aloud
  useEffect(() => {
    if (isVoiceModeEnabled && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];

      // Check if this is a new assistant message
      if (lastMessage.role === 'assistant' && lastMessage.id !== lastMessageRef.current) {
        lastMessageRef.current = lastMessage.id;

        // Stop listening while speaking
        if (isListening) {
          stopListening();
        }

        // Clear any transcript that might have been picked up
        resetTranscript();
        setInputText('');

        console.log('🔊 Voice mode: Reading assistant message');
        speak(lastMessage.content, () => {
          console.log('✅ Voice mode: Finished reading, ready for next input');
          // Auto-restart listening (handled by useEffect above)
        });
      }
    }
  }, [messages, isVoiceModeEnabled, speak, isListening, stopListening, resetTranscript, setInputText]);

  // Voice Mode: Auto-send when transcript is complete
  useEffect(() => {
    if (isVoiceModeEnabled && fullTranscript && !isSpeaking && !isTyping) {
      // Wait a moment to see if user continues speaking
      const timer = setTimeout(() => {
        if (fullTranscript.trim() && !isSpeaking) {
          console.log('📤 Voice mode: Auto-sending message');
          onAutoSend(new Event('submit'));
        }
      }, 1500); // 1.5 second delay for natural conversation

      return () => clearTimeout(timer);
    }
  }, [fullTranscript, isVoiceModeEnabled, isSpeaking, isTyping, onAutoSend]);

  // Cleanup: Stop speech and listening when voice mode is disabled
  useEffect(() => {
    if (!isVoiceModeEnabled) {
      if (isListening) {
        stopListening();
      }
    }
  }, [isVoiceModeEnabled, isListening, stopListening]);
};
