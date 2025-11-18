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

  const addMessage = (role, content, statementData = null) => {
    const message = createMessage(role, content);
    if (statementData) {
      console.log('✅ Adding message with statementData:', { role, statementData });
      message.statementData = statementData;
    } else {
      console.log('📝 Adding message without statementData:', { role, content: content.substring(0, 30) });
    }
    setMessages((prev) => [...prev, message]);
    return message;
  };

  const addUserMessage = (content) => addMessage('user', content);
  const addAssistantMessage = (content, statementData = null) => addMessage('assistant', content, statementData);

  return {
    messages,
    setMessages,
    messagesEndRef,
    addUserMessage,
    addAssistantMessage,
    scrollToBottom,
  };
};
