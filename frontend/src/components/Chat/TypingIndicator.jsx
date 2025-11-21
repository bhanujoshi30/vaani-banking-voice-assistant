import AIAssistantLogo from "../AIAssistantLogo.jsx";

/**
 * TypingIndicator component - Shows when assistant is typing
 */
const TypingIndicator = () => {
  return (
    <div className="chat-message chat-message--assistant">
      <div className="chat-message__avatar">
        <AIAssistantLogo size={40} />
      </div>
      <div className="chat-message__content">
        <div className="chat-typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
