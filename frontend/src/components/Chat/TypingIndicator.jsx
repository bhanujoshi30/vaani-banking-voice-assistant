/**
 * TypingIndicator component - Shows when assistant is typing
 */
const TypingIndicator = () => {
  return (
    <div className="chat-message chat-message--assistant">
      <div className="chat-message__avatar">
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="12" cy="12" r="10" fill="#FF8F42" />
          <path
            d="M8 14C8 14 9.5 16 12 16C14.5 16 16 14 16 14"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <circle cx="9" cy="9" r="1.5" fill="white" />
          <circle cx="15" cy="9" r="1.5" fill="white" />
        </svg>
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
