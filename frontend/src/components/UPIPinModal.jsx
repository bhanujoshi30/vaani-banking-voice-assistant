import { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";
import "./UPIPinModal.css";

const UPIPinModal = ({ isOpen, onClose, onConfirm, paymentDetails, strings, language, onPaymentDetailsChange }) => {
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [editedAmount, setEditedAmount] = useState("");
  const [editedRecipient, setEditedRecipient] = useState("");
  const [upiIdError, setUpiIdError] = useState("");
  const [amountError, setAmountError] = useState("");
  const pinInputRefs = useRef([]);

  useEffect(() => {
    if (isOpen) {
      setPin("");
      setError("");
      setIsEditing(false);
      setUpiIdError("");
      setAmountError("");
      if (paymentDetails) {
        setEditedAmount(paymentDetails.amount?.toString() || "");
        setEditedRecipient(paymentDetails.recipient || "");
      }
    }
  }, [isOpen, paymentDetails]);

  // Validate amount
  const validateAmount = (amountValue) => {
    if (!amountValue || amountValue.trim() === '') {
      return { valid: false, error: language === 'hi-IN' ? 'राशि आवश्यक है' : 'Amount is required' };
    }
    
    const numValue = parseFloat(amountValue);
    
    if (isNaN(numValue)) {
      return { valid: false, error: language === 'hi-IN' ? 'कृपया वैध संख्या दर्ज करें' : 'Please enter a valid number' };
    }
    
    if (numValue <= 0) {
      return { valid: false, error: language === 'hi-IN' ? 'राशि 0 से अधिक होनी चाहिए' : 'Amount must be greater than 0' };
    }
    
    if (numValue < 1) {
      return { valid: false, error: language === 'hi-IN' ? 'न्यूनतम राशि ₹1 है' : 'Minimum amount is ₹1' };
    }
    
    // Check for too many decimal places
    const decimalPlaces = (amountValue.toString().split('.')[1] || '').length;
    if (decimalPlaces > 2) {
      return { valid: false, error: language === 'hi-IN' ? 'राशि में अधिकतम 2 दशमलव स्थान हो सकते हैं' : 'Amount can have maximum 2 decimal places' };
    }
    
    return { valid: true, error: '' };
  };

  // Validate UPI ID format
  const validateUPIId = (upiId) => {
    if (!upiId || !upiId.trim()) {
      return { valid: false, error: language === 'hi-IN' ? 'UPI ID आवश्यक है' : 'UPI ID is required' };
    }
    
    const trimmed = upiId.trim();
    
    // Check basic format first
    if (!trimmed.includes('@')) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'अमान्य UPI ID प्रारूप'
          : 'Invalid UPI ID format'
      };
    }
    
    const parts = trimmed.split('@');
    if (parts.length !== 2) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'अमान्य UPI ID प्रारूप'
          : 'Invalid UPI ID format'
      };
    }
    
    const [username, payee] = parts;
    
    // Check length constraints
    if (trimmed.length < 5 || trimmed.length > 100) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'UPI ID 5-100 वर्णों के बीच होना चाहिए'
          : 'UPI ID must be between 5-100 characters'
      };
    }
    
    // Validate username
    if (username.length < 3 || username.length > 99) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'यूजरनेम 3-99 वर्णों के बीच होना चाहिए'
          : 'Username must be between 3-99 characters'
      };
    }
    
    if (!/^[a-zA-Z0-9._-]+$/.test(username)) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'यूजरनेम में केवल अक्षर, संख्या, बिंदु, हाइफन और अंडरस्कोर हो सकते हैं'
          : 'Username can only contain letters, numbers, dots, hyphens, and underscores'
      };
    }
    
    // Validate payee
    if (payee.length < 2 || payee.length > 20) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'Payee 2-20 वर्णों के बीच होना चाहिए'
          : 'Payee must be between 2-20 characters'
      };
    }
    
    if (!/^[a-zA-Z0-9]+$/.test(payee)) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'Payee में केवल अक्षर और संख्या हो सकते हैं'
          : 'Payee can only contain letters and numbers'
      };
    }
    
    return { valid: true, error: "" };
  };

  const handleAmountChange = (e) => {
    const value = e.target.value.replace(/[^\d.]/g, '');
    setEditedAmount(value);
    setError("");
    setAmountError("");
    
    // Validate amount in real-time
    if (value.trim() !== '') {
      const validation = validateAmount(value);
      if (!validation.valid) {
        setAmountError(validation.error);
      }
    }
  };

  const handleRecipientChange = (e) => {
    const value = e.target.value;
    setEditedRecipient(value);
    setUpiIdError("");
    
    // Validate UPI ID in real-time if it looks like a UPI ID
    if (value.includes('@')) {
      const validation = validateUPIId(value);
      if (!validation.valid) {
        setUpiIdError(validation.error);
      }
    }
  };

  const handleSaveEdit = () => {
    // Validate amount
    const amountValidation = validateAmount(editedAmount);
    if (!amountValidation.valid) {
      setAmountError(amountValidation.error);
      return;
    }
    
    // Validate recipient/UPI ID
    const upiValidation = validateUPIId(editedRecipient);
    if (!upiValidation.valid) {
      setUpiIdError(upiValidation.error);
      return;
    }
    
    // Update payment details
    if (onPaymentDetailsChange) {
      onPaymentDetailsChange({
        ...paymentDetails,
        amount: parseFloat(editedAmount),
        recipient: editedRecipient.trim(),
      });
    }
    
    setIsEditing(false);
    setError("");
    setUpiIdError("");
    setAmountError("");
  };

  const handlePinChange = (index, value) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) {
      return;
    }

    const newPin = pin.split("");
    newPin[index] = value;
    const updatedPin = newPin.join("").slice(0, 6);
    setPin(updatedPin);
    setError("");

    // Auto-focus next input
    if (value && index < 5 && pinInputRefs.current[index + 1]) {
      pinInputRefs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === "Backspace" && !pin[index] && index > 0) {
      pinInputRefs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (pastedData.length === 6) {
      setPin(pastedData);
      setError("");
      // Focus last input
      if (pinInputRefs.current[5]) {
        pinInputRefs.current[5].focus();
      }
    }
  };

  const handleSubmit = (pinValue = pin) => {
    console.log('UPIPinModal handleSubmit called with pin:', pinValue);
    console.log('Payment details:', paymentDetails);
    
    if (pinValue.length !== 6) {
      setError(strings.pinInvalid || "PIN must be 6 digits");
      return;
    }

    if (!/^\d{6}$/.test(pinValue)) {
      setError(strings.pinInvalid || "Invalid PIN format");
      return;
    }

    // Final validation before submitting (only for payment operations, not balance check)
    if (paymentDetails && paymentDetails.operation !== 'balance_check' && paymentDetails.recipient) {
      const validation = validateUPIId(paymentDetails.recipient);
      if (!validation.valid) {
        setUpiIdError(validation.error);
        return;
      }
    }

    console.log('Calling onConfirm with pin:', pinValue);
    onConfirm(pinValue);
  };

  if (!isOpen) return null;

  return (
    <div className="upi-pin-modal-overlay" onClick={onClose}>
      <div className="upi-pin-modal" onClick={(e) => e.stopPropagation()}>
        <h2>{strings.upiPinTitle || "Enter UPI PIN"}</h2>
        {paymentDetails && (
          <div className="upi-pin-payment-details">
            {paymentDetails.operation === 'balance_check' ? (
              // Balance check operation
              <p>
                <strong>{language === 'hi-IN' ? 'खाता' : 'Account'}:</strong> {paymentDetails.sourceAccount ? `...${paymentDetails.sourceAccount.slice(-4)}` : ''}
              </p>
            ) : isEditing ? (
              // Payment editing mode
              <>
                <div className="upi-pin-edit-field">
                  <label>
                    <strong>{strings.amount || "Amount"}:</strong>
                    <input
                      type="text"
                      value={editedAmount}
                      onChange={handleAmountChange}
                      placeholder="0.00"
                      className={`upi-pin-edit-input ${amountError ? 'upi-pin-edit-input--error' : ''}`}
                    />
                  </label>
                  {amountError && (
                    <div className="upi-pin-error-container">
                      <span className="upi-pin-error-text">{amountError}</span>
                    </div>
                  )}
                </div>
                <div className="upi-pin-edit-field">
                  <label>
                    <strong>{strings.to || "To"} (UPI ID):</strong>
                    <input
                      type="text"
                      value={editedRecipient}
                      onChange={handleRecipientChange}
                      placeholder="username@payee"
                      className={`upi-pin-edit-input ${upiIdError ? 'upi-pin-edit-input--error' : ''}`}
                    />
                  </label>
                  {upiIdError && (
                    <div className="upi-pin-error-container">
                      <span className="upi-pin-error-text">{upiIdError}</span>
                      <span className="upi-pin-error-hint">
                        {language === 'hi-IN' 
                          ? 'सही प्रारूप: username@payee (उदाहरण: john@paytm, 9876543210@ybl)'
                          : 'Correct format: username@payee (e.g., john@paytm, 9876543210@ybl)'}
                      </span>
                    </div>
                  )}
                </div>
                <div className="upi-pin-edit-actions">
                  <button 
                    type="button" 
                    className="secondary-btn" 
                    onClick={() => {
                      setIsEditing(false);
                      setUpiIdError("");
                      setAmountError("");
                      setError("");
                    }}
                  >
                    {strings.cancel || "Cancel"}
                  </button>
                  <button 
                    type="button" 
                    className="primary-btn" 
                    onClick={handleSaveEdit}
                  >
                    {strings.save || "Save"}
                  </button>
                </div>
              </>
            ) : (
              // Payment display mode
              <>
                <p>
                  <strong>{strings.amount || "Amount"}:</strong> ₹{paymentDetails.amount}
                </p>
                <p>
                  <strong>{strings.to || "To"}:</strong> {paymentDetails.recipient}
                </p>
                <button 
                  type="button" 
                  className="ghost-btn" 
                  onClick={() => setIsEditing(true)}
                  style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}
                >
                  {strings.edit || "Edit"}
                </button>
              </>
            )}
          </div>
        )}
        {!isEditing && (
          <>
            <p className="upi-pin-description">
              {strings.pinDescription || "Please enter your 6-digit UPI PIN to confirm the payment"}
            </p>
            <div className="upi-pin-input-container">
              {[0, 1, 2, 3, 4, 5].map((index) => (
                <input
                  key={index}
                  ref={(el) => (pinInputRefs.current[index] = el)}
                  type="password"
                  inputMode="numeric"
                  maxLength={1}
                  className="upi-pin-input"
                  value={pin[index] || ""}
                  onChange={(e) => handlePinChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={handlePaste}
                  autoComplete="off"
                />
              ))}
            </div>
            {error && <p className="upi-pin-error">{error}</p>}
            <div className="upi-pin-modal-actions">
              <button type="button" className="secondary-btn" onClick={onClose}>
                {strings.cancel || "Cancel"}
              </button>
              <button type="button" className="primary-btn" onClick={() => handleSubmit()}>
                {strings.confirm || "Confirm"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

UPIPinModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  paymentDetails: PropTypes.shape({
    amount: PropTypes.number.isRequired,
    recipient: PropTypes.string.isRequired,
  }),
  strings: PropTypes.object,
  language: PropTypes.string,
  onPaymentDetailsChange: PropTypes.func,
};

export default UPIPinModal;
