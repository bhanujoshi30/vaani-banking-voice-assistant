import { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";
import { Navigate, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import ChatMessage from "../components/Chat/ChatMessage.jsx";
import TypingIndicator from "../components/Chat/TypingIndicator.jsx";
import ChatInput from "../components/Chat/ChatInput.jsx";
import ChatSidebar from "../components/Chat/ChatSidebar.jsx";
import LanguageSelector from "../components/Chat/LanguageSelector.jsx";
import useSpeechRecognition from "../hooks/useSpeechRecognition.js";
import { createMessage, simulateAIResponse, INITIAL_MESSAGE } from "../utils/chatUtils.js";
import { DEFAULT_LANGUAGE, getLanguageByCode } from "../config/voiceConfig.js";
import "./Chat.css";

const Chat = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [language, setLanguage] = useState(DEFAULT_LANGUAGE);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

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
    resetTranscript,
  } = useSpeechRecognition({
    lang: language,
    continuous: true,
    interimResults: true,
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update input text when speech transcript changes
  useEffect(() => {
    if (fullTranscript) {
      console.log('Updating input with transcript:', fullTranscript);
      setInputText(fullTranscript);
    }
  }, [fullTranscript]);

  // Show speech errors
  useEffect(() => {
    if (speechError) {
      console.warn('Speech error:', speechError);
      alert(speechError); // Show error to user
    }
  }, [speechError]);

  if (!session.authenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim()) return;

    // Stop listening if currently recording
    if (isListening) {
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
    if (!isSpeechSupported) {
      alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isLanguageComingSoon) {
      alert('Voice input for this language is coming soon. Please use English or Hindi.');
      return;
    }

    // Toggle listening state
    toggleListening();
  };

  return (
    <div className="app-shell">
      <div className="app-content app-content--fullwidth">
        <div className="app-gradient app-gradient--fullwidth">
          <SunHeader
            subtitle={`${session.user.branch.name} · ${session.user.branch.city}`}
            actionSlot={
              <div className="chat-header-actions">
                <LanguageSelector 
                  selectedLanguage={language}
                  onLanguageChange={setLanguage}
                  disabled={isListening}
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
          <main className="chat-container">
            <div className="chat-main">
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
