import { sendChatMessage as sendChatMessageAPI } from '../api/aiClient.js';
import { simulateAIResponse } from '../utils/chatUtils.js';

/**
 * Service for handling AI chat messages
 */

/**
 * Send a message to the AI backend and get response
 * @param {Object} params - Message parameters
 * @returns {Promise<Object>} - AI response object with text and optional data
 */
export const sendChatMessage = async ({
  message,
  userId,
  sessionId,
  language,
  userContext,
  messageHistory,
  voiceMode,
}) => {
  try {
    const aiResponse = await sendChatMessageAPI({
      message,
      userId,
      sessionId,
      language,
      userContext,
      messageHistory,
      voiceMode,
    });

    console.log('📥 AI Response from backend:', {
      hasResponse: !!aiResponse.response,
      hasStatementData: !!aiResponse.statement_data,
      hasStructuredData: !!aiResponse.structured_data,
      statementData: aiResponse.statement_data,
      structuredData: aiResponse.structured_data,
    });

    // Return full response object with text and any additional data
    return {
      text: aiResponse.response,
      statementData: aiResponse.statement_data || null,
      structuredData: aiResponse.structured_data || null,
    };
  } catch (error) {
    console.error('Error getting AI response:', error);
    console.log('Falling back to mock response');
    
    // Fallback to mock response if AI backend unavailable
    const mockText = await simulateAIResponse(message);
    return {
      text: mockText,
      statementData: null,
    };
  }
};

/**
 * Build user context from session
 * @param {Object} session - User session object
 * @returns {Object} - User context for AI
 */
export const buildUserContext = (session) => {
  return {
    account_number:
      session.user?.accountSummary?.[0]?.accountNumber ||
      session.user?.account?.account_number,
    name: session.user?.fullName || session.user?.name,
  };
};

/**
 * Build session ID from user
 * @param {Object} session - User session object
 * @returns {string} - Session ID
 */
export const buildSessionId = (session) => {
  return `session-${session.user?.id || Date.now()}`;
};

/**
 * Format message history for AI
 * @param {Array} messages - Chat messages
 * @param {number} limit - Max messages to include
 * @returns {Array} - Formatted message history
 */
export const formatMessageHistory = (messages, limit = 10) => {
  return messages.slice(-limit).map((msg) => ({
    role: msg.role,
    content: msg.content,
  }));
};
