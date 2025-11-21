import PropTypes from "prop-types";
import { DEFAULT_LANGUAGE } from "../../config/voiceConfig.js";
import { getChatCopy } from "../../config/chatCopy.js";
import QuickActionIcon from "./QuickActionIcon.jsx";

const FALLBACK_COPY = getChatCopy(DEFAULT_LANGUAGE);

/**
 * ChatSidebar component - Quick actions and mode toggles
 */
const ChatSidebar = ({ 
  isSpeechSupported, 
  onQuickAction, 
  copy,
  upiMode,
  isVoiceModeEnabled,
  isVoiceSecured,
  checkingVoiceBinding,
  onVoiceModeToggle,
  onVoiceEnrollmentClick,
  onUPIModeToggle,
  pageStrings,
  upiStrings,
}) => {
  const localizedCopy = copy || FALLBACK_COPY;
  const quickActions = localizedCopy.quickActions || [];

  return (
    <aside className="chat-sidebar">
      {/* Mode Toggle Pills */}
      <div className="chat-sidebar-mode-buttons">
        {/* Voice Mode Pill */}
        {!checkingVoiceBinding && (
          isVoiceModeEnabled ? (
            // Voice mode active - show green secured pill
            <div
              className="profile-pill profile-pill--secured"
              onClick={(e) => {
                e.stopPropagation();
                onVoiceModeToggle();
              }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  e.stopPropagation();
                  onVoiceModeToggle();
                }
              }}
            >
              <span className="status-dot status-dot--online" />
              {pageStrings?.profile?.voiceMode || "Voice Mode"}
            </div>
          ) : isVoiceSecured ? (
            // Voice mode off but secured - show orange pill that activates voice mode on click
            <div
              className="profile-pill profile-pill--orange"
              onClick={(e) => {
                e.stopPropagation();
                onVoiceModeToggle();
              }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  e.stopPropagation();
                  onVoiceModeToggle();
                }
              }}
            >
              <span className="status-dot status-dot--orange" />
              {pageStrings?.profile?.voiceMode || "Voice Mode"}
            </div>
          ) : (
            // Voice mode off and unsecured - show tag that prompts to secure
            <div
              className="profile-pill profile-pill--unsecured"
              onClick={(e) => {
                e.stopPropagation();
                onVoiceEnrollmentClick();
              }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  e.stopPropagation();
                  onVoiceEnrollmentClick();
                }
              }}
            >
              <span className="status-dot status-dot--warning" />
              {pageStrings?.profile?.voiceSessionUnsecured || "Voice session unsecured"}
            </div>
          )
        )}
        
        {/* UPI Mode Pill */}
        <div 
          className={`profile-pill ${upiMode ? 'profile-pill--secured' : 'profile-pill--unsecured'}`} 
          onClick={(e) => {
            e.stopPropagation();
            onUPIModeToggle();
          }}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              e.stopPropagation();
              onUPIModeToggle();
            }
          }}
        >
          <span className={`status-dot ${upiMode ? 'status-dot--online' : 'status-dot--warning'}`} />
          {upiMode ? (upiStrings?.upiModeActive || "UPI Mode Active") : (upiStrings?.upiModeInactive || "UPI Mode Inactive")}
        </div>
      </div>

      {/* Quick Actions */}
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
    </aside>
  );
};

ChatSidebar.propTypes = {
  isSpeechSupported: PropTypes.bool.isRequired,
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
  }),
  upiMode: PropTypes.bool.isRequired,
  isVoiceModeEnabled: PropTypes.bool.isRequired,
  isVoiceSecured: PropTypes.bool.isRequired,
  checkingVoiceBinding: PropTypes.bool.isRequired,
  onUPIModeToggle: PropTypes.func.isRequired,
  onVoiceModeToggle: PropTypes.func.isRequired,
  onVoiceEnrollmentClick: PropTypes.func.isRequired,
  pageStrings: PropTypes.object,
  upiStrings: PropTypes.object,
};

ChatSidebar.defaultProps = {
  copy: FALLBACK_COPY,
};

export default ChatSidebar;
