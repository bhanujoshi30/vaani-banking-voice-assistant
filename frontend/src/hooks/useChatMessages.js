import { useState, useRef, useEffect } from 'react';
import { createMessage, INITIAL_MESSAGE } from '../utils/chatUtils.js';

/**
 * Hook for managing chat messages and auto-scrolling
 */
const createInitialAssistantMessage = (messageText) => {
  const content = messageText || INITIAL_MESSAGE.content;
  return createMessage('assistant', content);
};

export const useChatMessages = ({ initialMessage } = {}) => {
  const [messages, setMessages] = useState(() => [createInitialAssistantMessage(initialMessage)]);
  const messagesEndRef = useRef(null);
  const isLanguageChangingRef = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!initialMessage) return;
    
    // Skip auto-update if we're in the middle of a language change
    if (isLanguageChangingRef.current) {
      // Reset the flag after a short delay to allow messages to be set
      setTimeout(() => {
        isLanguageChangingRef.current = false;
      }, 100);
      return;
    }

    setMessages((prev) => {
      // If messages array is empty, set the initial message
      if (prev.length === 0) {
        return [createInitialAssistantMessage(initialMessage)];
      }
      
      // If there's exactly 1 assistant message and content is different, update it
      if (
        prev.length === 1 &&
        prev[0].role === 'assistant' &&
        prev[0].content !== initialMessage
      ) {
        return [
          {
            ...prev[0],
            content: initialMessage,
            timestamp: new Date(),
          },
        ];
      }
      // If there are multiple messages, keep them as is - don't reset on language change
      // Language changes should preserve the conversation history
      // If there's 1 message but it's not an assistant message, reset
      if (prev.length === 1 && prev[0].role !== 'assistant') {
        return [createInitialAssistantMessage(initialMessage)];
      }
      return prev;
    });
  }, [initialMessage]);
  
  // Expose a function to mark language change in progress
  const markLanguageChanging = () => {
    isLanguageChangingRef.current = true;
  };

  const addMessage = (role, content, statementData = null, structuredData = null, language = null) => {
    const message = createMessage(role, content, language);
    if (statementData) {
      console.log('✅ Adding message with statementData:', { role, statementData });
      message.statementData = statementData;
    }
    if (structuredData) {
      console.log('✅ Adding message with structuredData:', { role, structuredData });
      message.structuredData = structuredData;
    }
    if (!statementData && !structuredData) {
      console.log('📝 Adding message without data:', { role, content: content.substring(0, 30) });
    }
    
    // If this is an assistant message with a card that requires input,
    // remove previous cards of the same type before adding the new one
    // This ensures only one card of each type exists at a time
    if (role === 'assistant' && structuredData) {
      const cardType = structuredData.type;
      const requiresInput = ['transfer', 'reminder_manager', 'statement_request'].includes(cardType);
      
      if (requiresInput) {
        setMessages((prev) => {
          // First, remove previous cards of the same type
          const cleanedMessages = prev.map((msg) => {
            if (msg.role === 'assistant' && 
                msg.structuredData && 
                msg.structuredData.type === cardType) {
              const { structuredData: oldStructuredData, ...rest } = msg;
              console.log('🗑️ Removing previous card of same type:', cardType);
              return rest;
            }
            return msg;
          });
          // Then add the new message
          return [...cleanedMessages, message];
        });
        return message;
      }
    }
    
    // For non-card messages or cards that don't require input, just add normally
    setMessages((prev) => [...prev, message]);
    return message;
  };

  /**
   * Remove structured data cards from previous messages when user moves to a new operation
   * Cards that require input: transfer, reminder_manager, statement_request
   * This ensures only the current card is visible, and old unused cards are removed
   */
  const clearUnusedCards = (newMessageText) => {
    const newMsgLower = newMessageText.toLowerCase().trim();
    
    // If message is empty or just whitespace, don't clear
    if (!newMessageText.trim()) return;
    
    // Check if new message is continuing a card operation
    // Look for keywords that indicate the user is continuing with a card operation
    const transferKeywords = ['transfer', 'ट्रांसफर', 'send', 'pay', 'भेजें', 'भुगतान'];
    const reminderKeywords = ['reminder', 'अनुस्मारक', 'remind', 'set reminder', 'view reminder'];
    const statementKeywords = ['statement', 'स्टेटमेंट', 'download', 'डाउनलोड', 'nikalna', 'nikal', 'export'];
    
    const isContinuingTransfer = transferKeywords.some(keyword => newMsgLower.includes(keyword));
    const isContinuingReminder = reminderKeywords.some(keyword => newMsgLower.includes(keyword));
    const isContinuingStatement = statementKeywords.some(keyword => newMsgLower.includes(keyword));
    
    const isContinuingCard = isContinuingTransfer || isContinuingReminder || isContinuingStatement;
    
    // If not continuing any card operation, clear all input-required cards from previous messages
    if (!isContinuingCard) {
      setMessages((prev) => 
        prev.map((msg) => {
          // Only clear cards from assistant messages that have input-required cards
          if (msg.role === 'assistant' && msg.structuredData) {
            const cardType = msg.structuredData.type;
            const requiresInput = ['transfer', 'reminder_manager', 'statement_request'].includes(cardType);
            
            if (requiresInput) {
              // Remove structuredData but keep the message text
              const { structuredData, ...rest } = msg;
              console.log('🗑️ Clearing unused card:', cardType, 'from message');
              return rest;
            }
          }
          return msg;
        })
      );
    } else {
      // If continuing a card operation, only clear cards of different types
      setMessages((prev) => 
        prev.map((msg) => {
          if (msg.role === 'assistant' && msg.structuredData) {
            const cardType = msg.structuredData.type;
            const requiresInput = ['transfer', 'reminder_manager', 'statement_request'].includes(cardType);
            
            if (requiresInput) {
              // Clear cards that don't match the current operation
              const shouldKeep = 
                (isContinuingTransfer && cardType === 'transfer') ||
                (isContinuingReminder && cardType === 'reminder_manager') ||
                (isContinuingStatement && cardType === 'statement_request');
              
              if (!shouldKeep) {
                const { structuredData, ...rest } = msg;
                console.log('🗑️ Clearing card of different type:', cardType);
                return rest;
              }
            }
          }
          return msg;
        })
      );
    }
  };

  const addUserMessage = (content, language = null) => addMessage('user', content, null, null, language);
  const addAssistantMessage = (content, statementData = null, structuredData = null, language = null) => 
    addMessage('assistant', content, statementData, structuredData, language);

  return {
    messages,
    setMessages,
    messagesEndRef,
    addUserMessage,
    addAssistantMessage,
    scrollToBottom,
    clearUnusedCards,
    markLanguageChanging,
  };
};
