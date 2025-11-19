import { useState, useRef, useEffect } from 'react';
import { createMessage, INITIAL_MESSAGE } from '../utils/chatUtils.js';

/**
 * Hook for managing chat messages and auto-scrolling
 */
export const useChatMessages = () => {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (role, content, statementData = null, structuredData = null) => {
    const message = createMessage(role, content);
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

  const addUserMessage = (content) => addMessage('user', content);
  const addAssistantMessage = (content, statementData = null, structuredData = null) => 
    addMessage('assistant', content, statementData, structuredData);

  return {
    messages,
    setMessages,
    messagesEndRef,
    addUserMessage,
    addAssistantMessage,
    scrollToBottom,
    clearUnusedCards,
  };
};
