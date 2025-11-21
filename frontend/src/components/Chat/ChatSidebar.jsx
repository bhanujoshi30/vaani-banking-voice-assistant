import PropTypes from "prop-types";
import { DEFAULT_LANGUAGE, getLanguageByCode } from "../../config/voiceConfig.js";
import { getChatCopy } from "../../config/chatCopy.js";
import QuickActionIcon from "./QuickActionIcon.jsx";

const FALLBACK_COPY = getChatCopy(DEFAULT_LANGUAGE);

/**
 * ChatSidebar component - Quick actions and voice status
 */
const ChatSidebar = ({ isSpeechSupported, selectedLanguage, onQuickAction, copy }) => {
  const currentLanguage = getLanguageByCode(selectedLanguage);
  const isComingSoon = currentLanguage?.comingSoon || false;
  const localizedCopy = copy || FALLBACK_COPY;
  const quickActions = localizedCopy.quickActions || [];
  const recentTopics = localizedCopy.recentTopics || [];
  const voiceFeatures = localizedCopy.voiceFeatures || FALLBACK_COPY.voiceFeatures;

  return (
    <aside className="chat-sidebar">
      <div className="chat-sidebar-card">
        <h3>{localizedCopy.quickActionsTitle}</h3>
        {localizedCopy.helperText && (
          <p className="chat-sidebar-hint">{localizedCopy.helperText}</p>
        )}
        <div className="chat-quick-actions">
          {quickActions.map((action) => (
            <button
              key={action.id}
              type="button"
              className="chat-quick-action"
              onClick={() => onQuickAction(action)}
            >
              <span className="chat-quick-action-icon">
                <QuickActionIcon actionId={action.id} />
              </span>
              <span className="chat-quick-action-label">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="chat-sidebar-card">
        <h3>{localizedCopy.recentTopicsTitle}</h3>
        <ul className="chat-recent-topics">
          {recentTopics.map((topic) => (
            <li key={topic}>{topic}</li>
          ))}
        </ul>
      </div>

      <div className="chat-sidebar-card chat-sidebar-card--accent">
        <h3>{voiceFeatures.title}</h3>
        <p>{voiceFeatures.description}</p>
        {!isSpeechSupported ? (
          <div className="voice-status">
            <span className="chat-badge chat-badge--warning">
              {voiceFeatures.badges?.notAvailable || "Not Available"}
            </span>
            <p className="chat-sidebar-hint">{voiceFeatures.notSupportedHint}</p>
          </div>
        ) : isComingSoon ? (
          <div className="voice-status">
            <span className="chat-badge chat-badge--info">
              {voiceFeatures.badges?.comingSoon || "🚧 Coming Soon"}
            </span>
            <p className="chat-sidebar-hint">
              {voiceFeatures.comingSoonHint} {currentLanguage?.flag} {currentLanguage?.nativeName}
            </p>
            <p className="chat-sidebar-hint chat-sidebar-hint--warning">
              {voiceFeatures.comingSoonWarning}
            </p>
          </div>
        ) : (
          <div className="voice-status">
            <span className="chat-badge chat-badge--success">
              {voiceFeatures.badges?.ready || "✓ Ready"}
            </span>
            <p className="chat-sidebar-hint">
              {voiceFeatures.readyHint} {currentLanguage?.flag} {currentLanguage?.nativeName} ({currentLanguage?.name})
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
  onQuickAction: PropTypes.func.isRequired,
  copy: PropTypes.shape({
    quickActionsTitle: PropTypes.string,
    quickActions: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string,
        icon: PropTypes.string,
        label: PropTypes.string,
        prompt: PropTypes.string,
        command: PropTypes.string,
      })
    ),
    recentTopicsTitle: PropTypes.string,
    recentTopics: PropTypes.arrayOf(PropTypes.string),
    helperText: PropTypes.string,
    voiceFeatures: PropTypes.shape({
      title: PropTypes.string,
      description: PropTypes.string,
      notSupportedHint: PropTypes.string,
      comingSoonHint: PropTypes.string,
      comingSoonWarning: PropTypes.string,
      readyHint: PropTypes.string,
      badges: PropTypes.object,
    }),
  }),
};

ChatSidebar.defaultProps = {
  copy: FALLBACK_COPY,
};

export default ChatSidebar;
