import AIAssistantLogo from "../AIAssistantLogo.jsx";
import PropTypes from "prop-types";

/**
 * TypingIndicator component - Shows when assistant is typing/thinking
 */
const TypingIndicator = ({ language = "en-IN" }) => {
  const thinkingText = language === "hi-IN" ? "वाणी सोच रही है..." : "Vaani is thinking...";
  
  return (
    <div className="chat-message chat-message--assistant">
      <div className="chat-message__avatar">
        <AIAssistantLogo size={40} />
      </div>
      <div className="chat-message__content">
        <div className="chat-typing-indicator">
          <span className="chat-typing-indicator__text">{thinkingText}</span>
          <div className="chat-typing-indicator__dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  );
};

TypingIndicator.propTypes = {
  language: PropTypes.string,
};

export default TypingIndicator;
