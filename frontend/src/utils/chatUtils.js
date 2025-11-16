/**
 * Chat utility functions
 */

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
 * @returns {Object} Message object
 */
export const createMessage = (role, content) => {
  return {
    id: generateMessageId(),
    role,
    content,
    timestamp: new Date(),
  };
};

/**
 * Simulate AI response (placeholder for backend integration)
 * @param {string} userMessage - The user's message
 * @returns {Promise<string>} AI response
 */
export const simulateAIResponse = async (userMessage) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Simple pattern matching for demo purposes
  const message = userMessage.toLowerCase();
  
  if (message.includes('balance') || message.includes('check')) {
    return "I can help you check your account balance. This feature will be fully functional once connected to the backend.";
  }
  
  if (message.includes('transfer') || message.includes('send')) {
    return "I can assist you with transferring funds. This feature will be available once backend integration is complete.";
  }
  
  if (message.includes('transaction') || message.includes('history')) {
    return "I can show you your transaction history. This will be connected to your actual transactions soon.";
  }
  
  if (message.includes('reminder')) {
    return "I can help you set up payment reminders. This feature will be enabled after backend integration.";
  }
  
  if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
    return "Hello! How can I assist you with your banking needs today?";
  }
  
  if (message.includes('help')) {
    return "I can help you with: checking balances, transferring funds, viewing transactions, and setting reminders. What would you like to do?";
  }
  
  return "I understand your request. This feature will be connected to the backend soon to process your banking queries.";
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
