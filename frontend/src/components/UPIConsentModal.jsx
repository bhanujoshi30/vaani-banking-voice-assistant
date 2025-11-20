import PropTypes from "prop-types";
import "./UPIConsentModal.css";

const UPIConsentModal = ({ isOpen, onClose, onAccept, strings, language }) => {
  if (!isOpen) return null;

  return (
    <div className="upi-consent-modal-overlay" onClick={onClose}>
      <div className="upi-consent-modal" onClick={(e) => e.stopPropagation()}>
        <h2>{strings.consentTitle || "Hello UPI - Terms & Conditions"}</h2>
        <div className="upi-consent-content">
          <p className="upi-consent-intro">
            {strings.consentIntro || "To use Hello UPI voice-assisted payments, please review and accept the following:"}
          </p>
          <ul className="upi-consent-list">
            <li>
              {strings.consentPoint1 || "I understand that UPI PIN must be entered manually and cannot be spoken"}
            </li>
            <li>
              {strings.consentPoint2 || "I agree to use Hello UPI in compliance with RBI guidelines"}
            </li>
            <li>
              {strings.consentPoint3 || "I acknowledge that all transactions are subject to verification"}
            </li>
            <li>
              {strings.consentPoint4 || "I will keep my UPI PIN confidential and not share it with anyone"}
            </li>
          </ul>
          <p className="upi-consent-note">
            {strings.consentNote || "By proceeding, you agree to the terms and conditions of Hello UPI service."}
          </p>
        </div>
        <div className="upi-consent-modal-actions">
          <button type="button" className="secondary-btn" onClick={onClose}>
            {strings.decline || "Decline"}
          </button>
          <button type="button" className="primary-btn" onClick={onAccept}>
            {strings.accept || "Accept & Continue"}
          </button>
        </div>
      </div>
    </div>
  );
};

UPIConsentModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onAccept: PropTypes.func.isRequired,
  strings: PropTypes.object,
  language: PropTypes.string,
};

export default UPIConsentModal;

