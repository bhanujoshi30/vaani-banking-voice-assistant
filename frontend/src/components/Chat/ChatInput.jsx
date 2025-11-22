import PropTypes from "prop-types";

const FALLBACK_COPY = {
  placeholders: {
    default: "Type your message or use voice input...",
    listening: "Listening... speak now",
    voiceMode: "Voice mode active - speak your message...",
    speaking: "Assistant is speaking... please wait",
    thinking: "Vaani is thinking...",
    comingSoon:
      "Voice input not available for this language yet. Type your message or switch to English/Hindi.",
  },
  micTooltip: {
    unsupported: "Voice input not supported in this browser",
    comingSoon: "This language is coming soon. Please use English or Hindi.",
    voiceMode: "Voice mode enabled - microphone is always on",
    stop: "Stop listening",
    start: "Start voice input",
  },
  hints: {
    speaking: "Assistant is speaking...",
    comingSoon: "Voice input coming soon for this language. Please use English or Hindi.",
    voiceMode: "Voice mode active - Speak naturally, your message will be sent automatically",
    listening: "Listening... Speak clearly",
    idle: "Try: \"Check my account balance\" or \"Show recent transactions\"",
  },
  sendButtonTitle: {
    default: "Send message",
    disabled: "Please wait while assistant is speaking",
  },
};

/**
 * ChatInput component - Message input with voice and send controls
 */
const ChatInput = ({
  inputText,
  setInputText,
  isTyping,
  isListening,
  isSpeechSupported,
  isLanguageComingSoon = false,
  isSpeaking = false,
  isVoiceModeEnabled = false,
  isVoiceSecured = false,
  onSubmit,
  onVoiceClick,
  onVoiceModeToggle = null,
  onVoiceEnrollmentClick = null,
  inputRef = null,
  copy = FALLBACK_COPY,
}) => {
  const resolvedCopy = copy || FALLBACK_COPY;
  const placeholders = {
    ...FALLBACK_COPY.placeholders,
    ...(resolvedCopy.placeholders || {}),
  };
  const micTooltip = {
    ...FALLBACK_COPY.micTooltip,
    ...(resolvedCopy.micTooltip || {}),
  };
  const hints = {
    ...FALLBACK_COPY.hints,
    ...(resolvedCopy.hints || {}),
  };
  const sendButtonTitle = {
    ...FALLBACK_COPY.sendButtonTitle,
    ...(resolvedCopy.sendButtonTitle || {}),
  };

  // Disable voice button if: speech not supported OR language coming soon
  // Note: We DON'T disable when voice mode is off - we want it clickable to activate voice mode
  const isVoiceDisabled = !isSpeechSupported || isLanguageComingSoon;
  const isInputDisabled = isTyping || isSpeaking || isListening;
  
  // Handle voice button click - if voice mode is disabled, check voice security first
  const handleVoiceButtonClick = () => {
    if (!isVoiceModeEnabled) {
      // Voice mode is disabled - check if user has trusted voice device
      if (isVoiceSecured && onVoiceModeToggle) {
        // User has trusted voice device - can activate voice mode directly
        onVoiceModeToggle();
      } else if (onVoiceEnrollmentClick) {
        // User doesn't have trusted voice device - show enrollment modal
        onVoiceEnrollmentClick();
      } else if (onVoiceModeToggle) {
        // Fallback: try to toggle (will show error if not supported)
        onVoiceModeToggle();
      }
    } else {
      // Voice mode is enabled - use normal voice input handler
      onVoiceClick();
    }
  };

  const placeholderText = isTyping
    ? placeholders.thinking
    : isSpeaking
    ? placeholders.speaking
    : isLanguageComingSoon
    ? placeholders.comingSoon
    : isVoiceModeEnabled
    ? placeholders.voiceMode
    : isListening
    ? placeholders.listening
    : placeholders.default;

  const micTitle = !isSpeechSupported
    ? micTooltip.unsupported
    : isLanguageComingSoon
    ? micTooltip.comingSoon
    : !isVoiceModeEnabled
    ? (micTooltip.activateVoiceMode || "Activate voice mode to enable microphone")
    : isSpeaking
    ? "Click to stop assistant and start speaking"
    : isListening
    ? micTooltip.stop
    : micTooltip.start;

  const sendTitle = isSpeaking ? sendButtonTitle.disabled : sendButtonTitle.default;

  return (
    <form className="chat-input-container" onSubmit={onSubmit}>
      <div className="chat-input-wrapper">
        <button
          type="button"
          className={`chat-input-icon ${isListening ? "chat-input-icon--listening" : ""} ${
            isVoiceDisabled ? "chat-input-icon--disabled" : ""
          } ${isSpeaking ? "chat-input-icon--interrupt" : ""} ${
            !isVoiceModeEnabled && !isVoiceDisabled ? "chat-input-icon--voice-mode-disabled" : ""
          }`}
          onClick={handleVoiceButtonClick}
          title={micTitle}
          disabled={isVoiceDisabled}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 15C13.66 15 15 13.66 15 12V6C15 4.34 13.66 3 12 3C10.34 3 9 4.34 9 6V12C9 13.66 10.34 15 12 15Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M19 12C19 15.31 16.31 18 13 18H11C7.69 18 5 15.31 5 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M12 18V22"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M8 22H16"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
        <input
          ref={inputRef}
          type="text"
          className="chat-input"
          placeholder={placeholderText}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isInputDisabled}
        />
        <button
          type="submit"
          className="chat-send-button"
          disabled={!inputText.trim() || isTyping || isSpeaking}
          title={sendTitle}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M22 2L11 13"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M22 2L15 22L11 13L2 9L22 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <div className="chat-input-hints">
        {isSpeaking && (
          <span className="chat-hint chat-hint--warning">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="#f39c12" />
              <path d="M12 6V12L16 14" stroke="white" strokeWidth="2" strokeLinecap="round" />
            </svg>
            {hints.speaking}
            <span style={{ marginLeft: '8px', fontSize: '0.85em', opacity: 0.9 }}>
              (Click microphone to interrupt)
            </span>
          </span>
        )}
        {!isSpeaking && isLanguageComingSoon && (
          <span className="chat-hint chat-hint--warning">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="#f39c12" />
              <path d="M12 8V12" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <circle cx="12" cy="16" r="1" fill="white" />
            </svg>
            {hints.comingSoon}
          </span>
        )}
        {!isSpeaking && !isLanguageComingSoon && isVoiceModeEnabled && isListening && (
          <span className="chat-hint chat-hint--listening">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="#7cb5ff" />
            </svg>
            {hints.voiceMode}
          </span>
        )}
        {!isSpeaking && !isLanguageComingSoon && isVoiceModeEnabled && !isListening && (
          <span className="chat-hint chat-hint--click-to-record">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="chat-hint__mic-icon">
              <path
                d="M12 15C13.66 15 15 13.66 15 12V6C15 4.34 13.66 3 12 3C10.34 3 9 4.34 9 6V12C9 13.66 10.34 15 12 15Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M19 12C19 15.31 16.31 18 13 18H11C7.69 18 5 15.31 5 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="chat-hint__arrow">←</span>
            {hints.clickToRecord || "Click microphone to record again"}
          </span>
        )}
        {!isSpeaking && !isLanguageComingSoon && !isVoiceModeEnabled && isListening && (
          <span className="chat-hint chat-hint--listening">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="#2ecc71" />
            </svg>
            {hints.listening}
          </span>
        )}
        {!isSpeaking && !isLanguageComingSoon && !isVoiceModeEnabled && !isListening && (
          <span className="chat-hint chat-hint--voice-mode-disabled">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            {hints.activateVoiceMode || "Activate voice mode to enable microphone button"}
          </span>
        )}
      </div>
    </form>
  );
};

ChatInput.propTypes = {
  inputText: PropTypes.string.isRequired,
  setInputText: PropTypes.func.isRequired,
  isTyping: PropTypes.bool.isRequired,
  isListening: PropTypes.bool.isRequired,
  isSpeechSupported: PropTypes.bool.isRequired,
  isLanguageComingSoon: PropTypes.bool,
  isSpeaking: PropTypes.bool,
  isVoiceModeEnabled: PropTypes.bool,
  isVoiceSecured: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  onVoiceClick: PropTypes.func.isRequired,
  onVoiceModeToggle: PropTypes.func,
  onVoiceEnrollmentClick: PropTypes.func,
  inputRef: PropTypes.object,
  copy: PropTypes.shape({
    placeholders: PropTypes.object,
    micTooltip: PropTypes.object,
    hints: PropTypes.object,
    sendButtonTitle: PropTypes.object,
  }),
};

ChatInput.defaultProps = {
  isLanguageComingSoon: false,
  isSpeaking: false,
  isVoiceModeEnabled: false,
  inputRef: null,
  copy: FALLBACK_COPY,
};

export default ChatInput;
