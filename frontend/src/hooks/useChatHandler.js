import { useState, useCallback } from 'react';
import {
  sendChatMessage,
  buildUserContext,
  buildSessionId,
  formatMessageHistory,
} from '../services/chatService.js';
import { getChatCopy } from '../config/chatCopy.js';

/**
 * Hook for handling chat message sending and AI responses
 */
export const useChatHandler = ({
  session,
  language,
  isVoiceModeEnabled,
  messages,
  addUserMessage,
  addAssistantMessage,
  resetTranscript,
  setInputText,
  isListening,
  isSpeaking,
  stopListening,
  toggleListening,
  stopSpeaking,
  clearUnusedCards,
  upiConsentGiven,
  setPendingUPIMessage,
  upiMode = false,
}) => {
  const [isTyping, setIsTyping] = useState(false);
  
  // Note: Removed excessive logging - upiMode prop is received correctly

  /**
   * Send a message and get AI response
   * @param {string} messageText - The message to send
   * @param {boolean} clearInput - Whether to clear input after sending
   */
  const sendMessage = useCallback(async (messageText, options = {}) => {
    // SIMPLE: Read upiMode directly from prop
    // Since upiMode is in useCallback dependencies, this callback is recreated
    // whenever upiMode changes, so it always has the latest value
    const currentUpiMode = upiMode;
    
    // Note: Removed excessive logging - only log errors or important state changes
    const config =
      typeof options === 'boolean'
        ? { clearInput: options }
        : { clearInput: true, displayMessage: null, ...options };

    const userFacingText = config.displayMessage || messageText;

    if (!messageText?.trim() && !userFacingText?.trim()) {
      return;
    }

    // Stop speaking immediately when user sends a message, but don't block the action
    if (isSpeaking && stopSpeaking) {
      console.log('🛑 Stopping TTS - user sent message');
      stopSpeaking();
      // Continue with the action - don't return here
    }

    // Stop listening if currently recording
    if (isListening) {
      if (isVoiceModeEnabled) {
        stopListening();
      } else {
        toggleListening();
      }
    }

    // Clear unused cards from previous messages before adding new user message
    // This ensures old cards don't remain when user moves to a different operation
    if (clearUnusedCards && messages && messages.length > 0) {
      clearUnusedCards(userFacingText);
    }

    // Add user message with current language
    addUserMessage(userFacingText, language);
    
    if (config.clearInput) {
      setInputText('');
      resetTranscript();
    }
    
    setIsTyping(true);

    try {
      // SIMPLE: Pass upiMode directly to API call
      // currentUpiMode is already the latest value from the prop (via useCallback dependency)
      console.log('🚀 Calling API with upiMode:', currentUpiMode);
      
      const response = await sendChatMessage({
        message: messageText || userFacingText,
        userId: session.user?.id,
        sessionId: buildSessionId(session),
        language,
        userContext: buildUserContext(session),
        messageHistory: formatMessageHistory(messages),
        voiceMode: isVoiceModeEnabled,
        upiMode: currentUpiMode, // Simple: pass the value directly
      });

      // Determine assistant text, falling back to localized card intro when needed
      let assistantText = (response.text || '').trim();
      const cardType = response.structuredData?.type;
      if (!assistantText && cardType) {
        const cardIntro = getChatCopy(language)?.cardIntros?.[cardType];
        if (cardIntro) {
          assistantText = cardIntro;
        }
      }

      // Check if this is a UPI-related message that requires consent
      const isUPIMessage = cardType === 'upi_mode_activation' || cardType === 'upi_payment' || cardType === 'upi_balance_check' || cardType === 'upi_payment_card';
      
      // If UPI message and consent not given, store as pending and don't add to chat yet
      if (isUPIMessage && !upiConsentGiven && setPendingUPIMessage) {
        console.log('⏸️ UPI message requires consent - storing as pending', { 
          cardType, 
          assistantText,
          structuredData: response.structuredData,
          upiConsentGiven 
        });
        setPendingUPIMessage({
          text: assistantText,
          content: assistantText, // Also store as content for compatibility
          statementData: response.statementData,
          structuredData: response.structuredData,
          id: Date.now().toString(), // Add ID for React keys
          role: 'assistant',
          timestamp: new Date(),
        });
        // Don't add message to chat - wait for consent
        return;
      }

      // Add assistant message with optional statement data and structured data
      // Store language so cards preserve their original language even if language changes later
      addAssistantMessage(assistantText, response.statementData, response.structuredData, language);
    } catch (error) {
      console.error('Error in chat handler:', error);
      addAssistantMessage('Sorry, I encountered an error. Please try again.', null, null, language);
    } finally {
      setIsTyping(false);
    }
  }, [
    // CRITICAL: Include upiMode in dependencies so callback has latest value
    // This ensures sendMessage always has access to the current upiMode
    upiMode, // Include this so the callback is recreated when upiMode changes
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
    stopSpeaking,
    upiConsentGiven,
    setPendingUPIMessage
  ]);

  /**
   * Handle form submit for sending messages
   */
  const handleSendMessage = async (e) => {
    e.preventDefault();
    // inputText should come from parent component state
    // This will be called with the current inputText value
  };

  /**
   * Handle quick action button clicks
   */
  const handleQuickAction = async (action) => {
    if (!action) return;

    // Stop speaking if currently speaking, but continue with action
    if (isSpeaking && stopSpeaking) {
      console.log('🛑 Stopping TTS - quick action clicked');
      stopSpeaking();
      // Continue with the action - don't return here
    }

    const displayMessage = action.prompt || action.label || '';
    const backendMessage = action.command || displayMessage;

    await sendMessage(backendMessage, {
      clearInput: false,
      displayMessage,
    });
  };

  return {
    isTyping,
    sendMessage,
    handleSendMessage,
    handleQuickAction,
  };
};
