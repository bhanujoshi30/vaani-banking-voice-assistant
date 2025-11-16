import { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";
import { Navigate, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import ChatMessage from "../components/Chat/ChatMessage.jsx";
import TypingIndicator from "../components/Chat/TypingIndicator.jsx";
import ChatInput from "../components/Chat/ChatInput.jsx";
import ChatSidebar from "../components/Chat/ChatSidebar.jsx";
import LanguageSelector from "../components/Chat/LanguageSelector.jsx";
import VoiceModeToggle from "../components/Chat/VoiceModeToggle.jsx";
import useSpeechRecognition from "../hooks/useSpeechRecognition.js";
import useTextToSpeech from "../hooks/useTextToSpeech.js";
import { createMessage, simulateAIResponse, INITIAL_MESSAGE } from "../utils/chatUtils.js";
import { DEFAULT_LANGUAGE, getLanguageByCode } from "../config/voiceConfig.js";
import "./Chat.css";
import "../components/Chat/VoiceModeToggle.css";

const Chat = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [language, setLanguage] = useState(DEFAULT_LANGUAGE);
  const [isVoiceModeEnabled, setIsVoiceModeEnabled] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const lastMessageRef = useRef(null);

  // Get current language info
  const currentLanguage = getLanguageByCode(language);
  const isLanguageComingSoon = currentLanguage?.comingSoon || false;

  // Use speech recognition hook with selected language
  const {
    isListening,
    isSpeechSupported,
    fullTranscript,
    transcript,
    interimTranscript,
    error: speechError,
    toggleListening,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition({
    lang: language,
    continuous: true,
    interimResults: true,
  });

  // Use text-to-speech hook
  const {
    isSpeaking,
    isTTSSupported,
    selectedVoice,
    speak,
    stop: stopSpeaking,
  } = useTextToSpeech({
    lang: language,
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0,
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update input text when speech transcript changes
  useEffect(() => {
    if (fullTranscript && !isSpeaking) {
      console.log('Updating input with transcript:', fullTranscript);
      setInputText(fullTranscript);
    }
  }, [fullTranscript, isSpeaking]);

  // Show speech errors
  useEffect(() => {
    if (speechError) {
      console.warn('Speech error:', speechError);
      alert(speechError); // Show error to user
    }
  }, [speechError]);

  // Voice Mode: Auto-start listening when enabled and not speaking
  useEffect(() => {
    if (isVoiceModeEnabled && !isLanguageComingSoon && !isSpeaking && !isTyping) {
      if (!isListening) {
        console.log('🎤 Voice mode: Auto-starting microphone');
        startListening();
      }
    } else if (isVoiceModeEnabled && isSpeaking && isListening) {
      // IMPORTANT: Stop listening while speaking to prevent feedback
      console.log('🛑 Voice mode: Stopping microphone during speech');
      stopListening();
    }
  }, [isVoiceModeEnabled, isSpeaking, isTyping, isListening, isLanguageComingSoon, startListening, stopListening]);

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
          // Auto-restart listening after speaking (handled by useEffect above)
        });
      }
    }
  }, [messages, isVoiceModeEnabled, speak, isListening, stopListening, resetTranscript]);

  // Voice Mode: Auto-send when transcript is complete
  useEffect(() => {
    if (isVoiceModeEnabled && fullTranscript && !isSpeaking && !isTyping) {
      // Wait a moment to see if user continues speaking
      const timer = setTimeout(() => {
        if (fullTranscript.trim() && !isSpeaking) {
          console.log('📤 Voice mode: Auto-sending message');
          handleSendMessage(new Event('submit'));
        }
      }, 1500); // 1.5 second delay for natural conversation

      return () => clearTimeout(timer);
    }
  }, [fullTranscript, isVoiceModeEnabled, isSpeaking, isTyping]);

  // Cleanup: Stop speech and listening when voice mode is disabled
  useEffect(() => {
    if (!isVoiceModeEnabled) {
      stopSpeaking();
      if (isListening) {
        stopListening();
      }
    }
  }, [isVoiceModeEnabled, stopSpeaking, isListening, stopListening]);

  if (!session.authenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim()) return;

    // Don't send if speaking in voice mode
    if (isVoiceModeEnabled && isSpeaking) {
      console.log('⚠️ Cannot send while speaking');
      return;
    }

    // Stop listening if currently recording (only in manual mode)
    if (!isVoiceModeEnabled && isListening) {
      toggleListening();
    }

    const messageContent = inputText.trim();

    // Add user message
    const userMessage = createMessage("user", messageContent);
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    resetTranscript(); // Clear the speech transcript
    setIsTyping(true);

    // Get AI response
    try {
      const response = await simulateAIResponse(messageContent);
      const assistantMessage = createMessage("assistant", response);
      setMessages((prev) => [...prev, assistantMessage]);
      
      // In voice mode, the message will be spoken by useEffect
    } catch (error) {
      console.error("Error getting AI response:", error);
      const errorMessage = createMessage(
        "assistant",
        "I'm sorry, I encountered an error. Please try again."
      );
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleVoiceInput = () => {
    // In voice mode, microphone is always on, so this just toggles manually
    if (isVoiceModeEnabled) {
      return; // Do nothing in voice mode - mic is auto-managed
    }

    if (!isSpeechSupported) {
      alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isLanguageComingSoon) {
      alert('Voice input for this language is coming soon. Please use English or Hindi.');
      return;
    }

    // Toggle listening state in manual mode
    toggleListening();
  };

  const handleVoiceModeToggle = () => {
    if (!isSpeechSupported || !isTTSSupported) {
      alert('Voice mode requires browser support for both speech recognition and text-to-speech. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isLanguageComingSoon) {
      alert('Voice mode is not available for this language yet. Please use English or Hindi.');
      return;
    }

    setIsVoiceModeEnabled((prev) => !prev);
  };

  return (
    <div className="app-shell">
      <div className="app-content app-content--fullwidth">
        <div className="app-gradient app-gradient--fullwidth">
          <SunHeader
            subtitle={`${session.user.branch.name} · ${session.user.branch.city}`}
            actionSlot={
              <div className="chat-header-actions">
                <VoiceModeToggle
                  isEnabled={isVoiceModeEnabled}
                  onToggle={handleVoiceModeToggle}
                  disabled={!isSpeechSupported || !isTTSSupported || isLanguageComingSoon}
                />
                <LanguageSelector 
                  selectedLanguage={language}
                  onLanguageChange={setLanguage}
                  disabled={isListening || isVoiceModeEnabled}
                />
                <button
                  type="button"
                  className="ghost-btn ghost-btn--compact"
                  onClick={() => navigate("/profile")}
                >
                  ← Back to Profile
                </button>
                <button type="button" className="ghost-btn ghost-btn--compact" onClick={onSignOut}>
                  Log out
                </button>
              </div>
            }
          />
          <main className={`chat-container ${isVoiceModeEnabled ? 'chat-container--voice-mode' : ''}`}>
            <div className="chat-main">
              {/* Speaking indicator */}
              {isSpeaking && (
                <div className="chat-speaking-indicator">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z"
                      fill="currentColor"
                      opacity="0.2"
                    />
                    <path
                      d="M12 6V12L16 14"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div>
                    <div>Assistant is speaking...</div>
                    {selectedVoice && (
                      <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '0.25rem' }}>
                        Voice: {selectedVoice.name.split(' ')[0]}
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="chat-messages">
                {messages.map((message) => (
                  <ChatMessage 
                    key={message.id} 
                    message={message} 
                    userName={session.user.fullName}
                  />
                ))}
                {isTyping && <TypingIndicator />}
                <div ref={messagesEndRef} />
              </div>

              <ChatInput
                inputText={inputText}
                setInputText={setInputText}
                isTyping={isTyping}
                isListening={isListening}
                isSpeechSupported={isSpeechSupported}
                isLanguageComingSoon={isLanguageComingSoon}
                isSpeaking={isSpeaking}
                isVoiceModeEnabled={isVoiceModeEnabled}
                onSubmit={handleSendMessage}
                onVoiceClick={handleVoiceInput}
                inputRef={inputRef}
              />

              {/* Debug panel - remove in production */}
              {process.env.NODE_ENV === 'development' && isListening && (
                <div style={{ 
                  padding: '1rem', 
                  background: '#f0f0f0', 
                  fontSize: '0.85rem',
                  borderTop: '1px solid #ddd'
                }}>
                  <strong>🐛 Debug Info:</strong><br/>
                  Listening: {isListening ? '✅' : '❌'}<br/>
                  Transcript: "{transcript}"<br/>
                  Interim: "{interimTranscript}"<br/>
                  Full: "{fullTranscript}"<br/>
                  Input Text: "{inputText}"<br/>
                  {speechError && <span style={{color: 'red'}}>Error: {speechError}</span>}
                </div>
              )}
            </div>

            <ChatSidebar 
              isSpeechSupported={isSpeechSupported} 
              selectedLanguage={language}
            />
          </main>
        </div>
      </div>
    </div>
  );
};

Chat.propTypes = {
  session: PropTypes.shape({
    authenticated: PropTypes.bool.isRequired,
    user: PropTypes.shape({
      fullName: PropTypes.string.isRequired,
      branch: PropTypes.shape({
        name: PropTypes.string.isRequired,
        city: PropTypes.string.isRequired,
      }).isRequired,
    }),
    accessToken: PropTypes.string,
  }).isRequired,
  onSignOut: PropTypes.func.isRequired,
};

export default Chat;
