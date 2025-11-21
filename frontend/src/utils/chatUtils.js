/**
 * Chat utility functions
 */
import { getChatCopy } from "../config/chatCopy.js";
import { DEFAULT_LANGUAGE } from "../config/voiceConfig.js";

/**
 * Format a timestamp for chat messages
 * @param {Date} date - The date to format
 * @returns {string} Formatted time string
 */
export const formatTime = (date) => {
  return date.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

/**
 * Generate a unique message ID
 * @returns {number} Unique ID based on timestamp
 */
export const generateMessageId = () => {
  return Date.now();
};

/**
 * Create a message object
 * @param {string} role - 'user' or 'assistant'
 * @param {string} content - Message content
 * @param {string} language - Language code (optional, stored for cards to preserve their language)
 * @returns {Object} Message object
 */
export const createMessage = (role, content, language = null) => {
  const message = {
    id: generateMessageId(),
    role,
    content,
    timestamp: new Date(),
  };
  
  // Store language if provided (important for cards to preserve their original language)
  if (language) {
    message.language = language;
  }
  
  return message;
};

/**
 * Simulate AI response (placeholder for backend integration)
 * @param {string} userMessage - The user's message
 * @param {string} language - Preferred language code
 * @returns {Promise<string>} AI response
 */
export const simulateAIResponse = async (userMessage, language = DEFAULT_LANGUAGE) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Simple pattern matching for demo purposes
  const message = (userMessage || "").toLowerCase();
  const copy = getChatCopy(language);
  const fallback = copy?.fallbackResponses || getChatCopy(DEFAULT_LANGUAGE).fallbackResponses;

  const includesAny = (phrases) => phrases.some((phrase) => message.includes(phrase));

  if (includesAny(['balance', 'check', 'बैलेंस', 'खाता बैलेंस'])) {
    return fallback.balance;
  }

  if (includesAny(['transfer', 'send', 'ट्रांसफर', 'राशि ट्रांसफर', 'भेज'])) {
    return fallback.transfer;
  }

  if (includesAny(['transaction', 'history', 'लेनदेन', 'इतिहास'])) {
    return fallback.transactions;
  }

  if (includesAny(['reminder', 'रिमाइंडर', 'याद दिल'])) {
    return fallback.reminder;
  }

  if (includesAny(['hello', 'hi', 'hey', 'नमस्ते', 'हैलो'])) {
    return fallback.greeting;
  }

  if (includesAny(['help', 'मदद', 'सहायता'])) {
    return fallback.help;
  }

  return fallback.generic;
};

/**
 * Quick action templates
 */
export const QUICK_ACTIONS = [
  {
    id: 'balance',
    icon: '💰',
    label: 'Check Balance',
    message: 'What is my account balance?',
  },
  {
    id: 'transfer',
    icon: '💸',
    label: 'Transfer Funds',
    message: 'I want to transfer funds',
  },
  {
    id: 'transactions',
    icon: '📊',
    label: 'View Transactions',
    message: 'Show me my recent transactions',
  },
  {
    id: 'reminder',
    icon: '🔔',
    label: 'Set Reminder',
    message: 'I want to set a payment reminder',
  },
];

/**
 * Initial assistant message
 */
export const INITIAL_MESSAGE = {
  id: 1,
  role: "assistant",
  content: "Hello! I'm Vaani, your voice banking assistant. How can I help you today?",
  timestamp: new Date(),
};
