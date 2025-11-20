/**
 * AI Backend API Client
 * Connects frontend to AI backend for chat and TTS
 */

const AI_BACKEND_URL = import.meta.env.VITE_AI_BACKEND_URL || 'http://localhost:8001';

/**
 * Send chat message to AI backend
 * @param {Object} params - Chat parameters
 * @param {string} params.message - User message
 * @param {number} params.userId - User ID
 * @param {string} params.sessionId - Session ID
 * @param {string} params.language - Language code (en-IN, hi-IN, te-IN)
 * @param {Object} params.userContext - User context (account_number, name)
 * @param {Array} params.messageHistory - Previous messages
 * @param {boolean} params.voiceMode - Whether in voice mode
 * @returns {Promise<Object>} - AI response
 */
export const sendChatMessage = async ({
  message,
  userId,
  sessionId,
  language = 'en-IN',
  userContext = {},
  messageHistory = [],
  voiceMode = false,
  upiMode = false,
}) => {
  try {
    const requestBody = {
      message,
      user_id: userId,
      session_id: sessionId,
      language,
      user_context: userContext,
      message_history: messageHistory,
      voice_mode: voiceMode,
      upi_mode: upiMode,
    };
    
    // DEBUG: Log what we're actually sending
    console.log('📤 API Request - UPI Mode:', {
      upi_mode_in_body: requestBody.upi_mode,
      upiMode_parameter: upiMode,
      upiMode_type: typeof upiMode,
      message: message?.substring(0, 50),
      timestamp: new Date().toISOString()
    });
    
    const response = await fetch(`${AI_BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get AI response');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('AI chat error:', error);
    throw error;
  }
};

/**
 * Stream chat response from AI backend
 * @param {Object} params - Chat parameters
 * @param {Function} onChunk - Callback for each chunk
 * @param {Function} onComplete - Callback when complete
 * @param {Function} onError - Callback on error
 * @returns {Function} - Cleanup function
 */
export const streamChatMessage = ({
  message,
  userId,
  sessionId,
  language = 'en-IN',
  userContext = {},
  messageHistory = [],
  voiceMode = false,
  onChunk,
  onComplete,
  onError,
}) => {
  const eventSource = new EventSource(
    `${AI_BACKEND_URL}/api/chat/stream?` +
      new URLSearchParams({
        message,
        user_id: userId,
        session_id: sessionId,
        language,
        user_context: JSON.stringify(userContext),
        message_history: JSON.stringify(messageHistory),
        voice_mode: voiceMode,
      })
  );

  eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
      eventSource.close();
      if (onComplete) onComplete();
    } else {
      if (onChunk) onChunk(event.data);
    }
  };

  eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    eventSource.close();
    if (onError) onError(error);
  };

  // Return cleanup function
  return () => eventSource.close();
};

/**
 * Get text-to-speech audio from Azure
 * @param {string} text - Text to synthesize
 * @param {string} language - Language code
 * @returns {Promise<Blob>} - Audio blob
 */
export const getTextToSpeech = async (text, language = 'en-IN') => {
  try {
    const response = await fetch(`${AI_BACKEND_URL}/api/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        language,
        use_azure: true,
      }),
    });

    if (!response.ok) {
      // Azure TTS not available, fall back to Web Speech API
      return null;
    }

    const audioBlob = await response.blob();
    return audioBlob;
  } catch (error) {
    console.error('TTS error:', error);
    return null;
  }
};

/**
 * Check AI backend health
 * @returns {Promise<Object>} - Health status
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${AI_BACKEND_URL}/health`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Health check error:', error);
    return { status: 'unavailable', error: error.message };
  }
};

/**
 * Play audio from blob
 * @param {Blob} audioBlob - Audio data
 */
export const playAudioBlob = (audioBlob) => {
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  
  audio.onended = () => {
    URL.revokeObjectURL(audioUrl);
  };
  
  audio.play();
  return audio;
};
