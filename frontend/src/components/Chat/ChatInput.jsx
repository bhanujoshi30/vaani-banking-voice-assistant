import PropTypes from "prop-types";

/**
 * ChatInput component - Message input with voice and send controls
 */
const ChatInput = ({
  inputText,
  setInputText,
  isTyping,
  isListening,
  isSpeechSupported,
  isLanguageComingSoon,
  onSubmit,
  onVoiceClick,
  inputRef,
}) => {
  const isVoiceDisabled = !isSpeechSupported || isLanguageComingSoon;

  return (
    <form className="chat-input-container" onSubmit={onSubmit}>
      <div className="chat-input-wrapper">
        <button
          type="button"
          className={`chat-input-icon ${isListening ? 'chat-input-icon--listening' : ''} ${isVoiceDisabled ? 'chat-input-icon--disabled' : ''}`}
          onClick={onVoiceClick}
          title={
            !isSpeechSupported
              ? "Voice input not supported in this browser"
              : isLanguageComingSoon
              ? "This language is coming soon. Please use English or Hindi."
              : isListening
              ? "Stop listening"
              : "Start voice input"
          }
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
          placeholder={
            isLanguageComingSoon
              ? "Voice input not available for this language yet. Type your message or switch to English/Hindi."
              : isListening
              ? "Listening... speak now"
              : "Type your message or use voice input..."
          }
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isTyping}
        />
        <button
          type="submit"
          className="chat-send-button"
          disabled={!inputText.trim() || isTyping}
          title="Send message"
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
        {isLanguageComingSoon && (
          <span className="chat-hint chat-hint--warning">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="12" cy="12" r="10" fill="#f39c12" />
              <path d="M12 8V12" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <circle cx="12" cy="16" r="1" fill="white" />
            </svg>
            Voice input coming soon for this language. Please use English or Hindi.
          </span>
        )}
        {!isLanguageComingSoon && isListening && (
          <span className="chat-hint chat-hint--listening">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="12" cy="12" r="10" fill="#2ecc71" />
            </svg>
            Listening... Speak clearly
          </span>
        )}
        {!isLanguageComingSoon && !isListening && (
          <span className="chat-hint">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Try: "Check my account balance" or "Show recent transactions"
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
  onSubmit: PropTypes.func.isRequired,
  onVoiceClick: PropTypes.func.isRequired,
  inputRef: PropTypes.object,
};

export default ChatInput;
