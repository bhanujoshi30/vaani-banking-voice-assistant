import { useEffect, useRef } from 'react';

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

  // Voice Mode: Auto-start listening when enabled and not speaking
  useEffect(() => {
    if (isVoiceModeEnabled && !isLanguageComingSoon && !isSpeaking && !isTyping) {
      if (!isListening) {
        console.log('🎤 Voice mode: Auto-starting microphone');
        startListening();
      }
    } else if (isVoiceModeEnabled && isSpeaking && isListening) {
      // Stop listening while speaking to prevent feedback
      console.log('🛑 Voice mode: Stopping microphone during speech');
      stopListening();
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
