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
import { useChatMessages } from "../hooks/useChatMessages.js";
import { useVoiceMode } from "../hooks/useVoiceMode.js";
import { useChatHandler } from "../hooks/useChatHandler.js";
import { DEFAULT_LANGUAGE, getLanguageByCode } from "../config/voiceConfig.js";
import "./Chat.css";
import "../components/Chat/VoiceModeToggle.css";

const Chat = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState("");
  const [language, setLanguage] = useState(DEFAULT_LANGUAGE);
  const [isVoiceModeEnabled, setIsVoiceModeEnabled] = useState(false);
  const inputRef = useRef(null);

  // Get current language info
  const currentLanguage = getLanguageByCode(language);
  const isLanguageComingSoon = currentLanguage?.comingSoon || false;

  // Chat messages management
  const {
    messages,
    messagesEndRef,
    addUserMessage,
    addAssistantMessage,
    clearUnusedCards,
  } = useChatMessages();

  // Use speech recognition hook with selected language
  // In normal mode, use non-continuous (stops after each utterance)
  // In voice mode, use continuous (keeps listening)
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
    continuous: isVoiceModeEnabled, // Only continuous in voice mode
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

  // Chat message handling
  const {
    isTyping,
    sendMessage,
    handleQuickAction,
  } = useChatHandler({
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
  });

  // Handle sending message from input
  const handleSendMessage = async (e) => {
    e.preventDefault();
    await sendMessage(inputText);
  };

  // Voice mode orchestration
  useVoiceMode({
    isVoiceModeEnabled,
    isLanguageComingSoon,
    isSpeaking,
    isTyping,
    isListening,
    fullTranscript,
    messages,
    startListening,
    stopListening,
    speak,
    resetTranscript,
    setInputText,
    onAutoSend: handleSendMessage,
  });

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

  // Cleanup: Stop speech when voice mode is disabled
  useEffect(() => {
    if (!isVoiceModeEnabled) {
      stopSpeaking();
    }
  }, [isVoiceModeEnabled, stopSpeaking]);

  if (!session.authenticated) {
    return <Navigate to="/" replace />;
  }

  const handleVoiceInput = () => {
    if (!isSpeechSupported) {
      alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isLanguageComingSoon) {
      alert('Voice input for this language is coming soon. Please use English or Hindi.');
      return;
    }

    // NORMAL MODE: Simple toggle - completely independent of voice mode
    if (!isVoiceModeEnabled) {
      if (isListening) {
        console.log('🛑 Normal mode: Stopping recording');
        stopListening();
      } else {
        console.log('🎤 Normal mode: Starting recording');
        startListening();
      }
      return;
    }

    // VOICE MODE: Handle stop/start differently
    if (isListening) {
      console.log('🛑 Voice mode: User manually stopping recording');
      stopListening();
      return;
    }

    // In voice mode, if user clicks to start, reset and start
    console.log('🎤 Voice mode: User manually starting recording');
    startListening();
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
                {isVoiceModeEnabled && (
                  <LanguageSelector 
                    selectedLanguage={language}
                    onLanguageChange={setLanguage}
                  />
                )}
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
                    language={language}
                    session={session}
                    onFeedback={(feedbackData) => {
                      console.log('Feedback received:', feedbackData);
                      // In production, send to backend API
                    }}
                    onAddAssistantMessage={addAssistantMessage}
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
              onQuickAction={handleQuickAction}
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
