import PropTypes from "prop-types";
import { getLanguageByCode } from "../../config/voiceConfig.js";

/**
 * ChatSidebar component - Quick actions and voice status
 */
const ChatSidebar = ({ isSpeechSupported, selectedLanguage }) => {
  const currentLanguage = getLanguageByCode(selectedLanguage);
  const isComingSoon = currentLanguage?.comingSoon || false;

  return (
    <aside className="chat-sidebar">
      <div className="chat-sidebar-card">
        <h3>Quick Actions</h3>
        <div className="chat-quick-actions">
          <button type="button" className="chat-quick-action">
            💰 Check Balance
          </button>
          <button type="button" className="chat-quick-action">
            💸 Transfer Funds
          </button>
          <button type="button" className="chat-quick-action">
            📊 View Transactions
          </button>
          <button type="button" className="chat-quick-action">
            🔔 Set Reminder
          </button>
        </div>
      </div>

      <div className="chat-sidebar-card">
        <h3>Recent Topics</h3>
        <ul className="chat-recent-topics">
          <li>Account balance inquiry</li>
          <li>Transaction history</li>
          <li>Fund transfer</li>
        </ul>
      </div>

      <div className="chat-sidebar-card chat-sidebar-card--accent">
        <h3>🎤 Voice Features</h3>
        <p>Click the microphone icon to use voice commands.</p>
        {!isSpeechSupported ? (
          <div className="voice-status">
            <span className="chat-badge chat-badge--warning">Not Available</span>
            <p className="chat-sidebar-hint">Use Chrome, Edge, or Safari for voice input</p>
          </div>
        ) : isComingSoon ? (
          <div className="voice-status">
            <span className="chat-badge chat-badge--info">🚧 Coming Soon</span>
            <p className="chat-sidebar-hint">
              Currently selected: {currentLanguage?.flag} {currentLanguage?.nativeName}
            </p>
            <p className="chat-sidebar-hint chat-sidebar-hint--warning">
              This language is not ready yet. Please use English or Hindi.
            </p>
          </div>
        ) : (
          <div className="voice-status">
            <span className="chat-badge chat-badge--success">✓ Ready</span>
            <p className="chat-sidebar-hint">
              Currently using: {currentLanguage?.flag} {currentLanguage?.nativeName} ({currentLanguage?.name})
            </p>
          </div>
        )}
      </div>
    </aside>
  );
};

ChatSidebar.propTypes = {
  isSpeechSupported: PropTypes.bool.isRequired,
  selectedLanguage: PropTypes.string.isRequired,
};

export default ChatSidebar;
