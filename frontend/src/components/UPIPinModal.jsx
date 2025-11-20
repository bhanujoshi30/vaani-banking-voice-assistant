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
  const pinInputRefs = useRef([]);

  useEffect(() => {
    if (isOpen) {
      setPin("");
      setError("");
      setIsEditing(false);
      setUpiIdError("");
      if (paymentDetails) {
        setEditedAmount(paymentDetails.amount?.toString() || "");
        setEditedRecipient(paymentDetails.recipient || "");
      }
    }
  }, [isOpen, paymentDetails]);

  // Validate UPI ID format
  const validateUPIId = (upiId) => {
    if (!upiId || !upiId.trim()) {
      return { valid: false, error: language === 'hi-IN' ? 'UPI ID आवश्यक है' : 'UPI ID is required' };
    }
    
    const trimmed = upiId.trim();
    
    // UPI ID format: username@payee (e.g., john@paytm, 9876543210@ybl)
    // Valid patterns:
    // - username@payee (username can contain letters, numbers, dots, hyphens, underscores)
    // - phone@payee (phone number with @payee)
    // Payee can be: paytm, ybl, phonepe, gpay, amazonpay, etc.
    
    const upiIdPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$/;
    
    if (!upiIdPattern.test(trimmed)) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'अमान्य UPI ID प्रारूप। सही प्रारूप: username@payee (उदाहरण: john@paytm, 9876543210@ybl)'
          : 'Invalid UPI ID format. Correct format: username@payee (e.g., john@paytm, 9876543210@ybl)'
      };
    }
    
    // Check length constraints
    if (trimmed.length < 5 || trimmed.length > 100) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'UPI ID 5-100 वर्णों के बीच होना चाहिए'
          : 'UPI ID must be between 5-100 characters'
      };
    }
    
    // Check for valid payee providers (common ones)
    const validPayees = ['paytm', 'ybl', 'phonepe', 'gpay', 'amazonpay', 'bhim', 'sunbank'];
    const payee = trimmed.split('@')[1]?.toLowerCase();
    
    if (payee && !validPayees.includes(payee) && !/^[a-zA-Z0-9]+$/.test(payee)) {
      // Allow other payees but warn if format seems wrong
      if (payee.length < 2 || payee.length > 20) {
        return { 
          valid: false, 
          error: language === 'hi-IN' 
            ? 'अमान्य UPI ID प्रदाता'
            : 'Invalid UPI ID provider'
        };
      }
    }
    
    return { valid: true, error: "" };
  };

  const handleAmountChange = (e) => {
    const value = e.target.value.replace(/[^\d.]/g, '');
    setEditedAmount(value);
    setError("");
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
    const amount = parseFloat(editedAmount);
    if (!editedAmount || isNaN(amount) || amount <= 0) {
      setError(language === 'hi-IN' ? 'कृपया वैध राशि दर्ज करें' : 'Please enter a valid amount');
      return;
    }
    
    // Validate recipient/UPI ID
    const validation = validateUPIId(editedRecipient);
    if (!validation.valid) {
      setUpiIdError(validation.error);
      return;
    }
    
    // Update payment details
    if (onPaymentDetailsChange) {
      onPaymentDetailsChange({
        ...paymentDetails,
        amount: amount,
        recipient: editedRecipient.trim(),
      });
    }
    
    setIsEditing(false);
    setError("");
    setUpiIdError("");
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
                      className="upi-pin-edit-input"
                    />
                  </label>
                </div>
                <div className="upi-pin-edit-field">
                  <label>
                    <strong>{strings.to || "To"} (UPI ID):</strong>
                    <input
                      type="text"
                      value={editedRecipient}
                      onChange={handleRecipientChange}
                      placeholder="username@payee"
                      className="upi-pin-edit-input"
                    />
                    {upiIdError && <span className="upi-pin-error-text">{upiIdError}</span>}
                  </label>
                </div>
                <div className="upi-pin-edit-actions">
                  <button 
                    type="button" 
                    className="secondary-btn" 
                    onClick={() => {
                      setIsEditing(false);
                      setUpiIdError("");
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
