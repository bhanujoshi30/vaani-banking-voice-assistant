import PropTypes from "prop-types";

/**
 * VoiceModeToggle component - Toggle for hands-free voice conversation mode
 */
const VoiceModeToggle = ({ isEnabled, onToggle, disabled }) => {
  return (
    <div className="voice-mode-toggle">
      <button
        type="button"
        className={`voice-mode-button ${isEnabled ? 'voice-mode-button--active' : ''}`}
        onClick={onToggle}
        disabled={disabled}
        title={
          disabled
            ? "Voice mode not available"
            : isEnabled
            ? "Disable voice mode"
            : "Enable hands-free voice conversation"
        }
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Microphone icon */}
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
          
          {/* Speaker waves when enabled */}
          {isEnabled && (
            <>
              <path
                d="M17 8C18.5 9.5 18.5 11.5 17 13"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                opacity="0.7"
              />
              <path
                d="M19 6C21.5 8.5 21.5 12.5 19 15"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                opacity="0.5"
              />
            </>
          )}
        </svg>
        <span className="voice-mode-label">
          {isEnabled ? 'Voice Mode On' : 'Voice Mode'}
        </span>
      </button>
      
      {isEnabled && (
        <div className="voice-mode-indicator">
          <span className="voice-mode-pulse"></span>
          <span className="voice-mode-status">Hands-free enabled</span>
        </div>
      )}
    </div>
  );
};

VoiceModeToggle.propTypes = {
  isEnabled: PropTypes.bool.isRequired,
  onToggle: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

export default VoiceModeToggle;
