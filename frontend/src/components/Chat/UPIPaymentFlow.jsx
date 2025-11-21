import { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { fetchAccounts, processQRCode } from '../../api/client.js';
import './TransferFlow.css'; // Reuse TransferFlow styles

/**
 * UPIPaymentFlow component - Handles UPI payment with UPI ID and amount entry
 */
const UPIPaymentFlow = ({ session, language = 'en-IN', onPaymentReady, paymentData }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSourceAccount, setSelectedSourceAccount] = useState(null);
  const [amount, setAmount] = useState('');
  const [upiId, setUpiId] = useState('');
  const [remarks, setRemarks] = useState('');
  const [showAccountSelection, setShowAccountSelection] = useState(false);
  const [upiIdError, setUpiIdError] = useState('');
  const [amountError, setAmountError] = useState('');
  const [isScanningQR, setIsScanningQR] = useState(false);
  const qrFileInputRef = useRef(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    // Auto-fill from payment data if available
    if (paymentData) {
      if (paymentData.amount) {
        setAmount(paymentData.amount.toString());
      }
      if (paymentData.recipient_identifier) {
        setUpiId(paymentData.recipient_identifier);
      }
      if (paymentData.remarks) {
        setRemarks(paymentData.remarks);
      }
    }
  }, [paymentData]);

  useEffect(() => {
    // Only set account after accounts are loaded
    if (loading) return;
    
    if (accounts.length === 0) {
      console.error('No accounts found from API');
      return;
    }
    
    // First, check if source account is pre-filled from paymentData
    if (paymentData?.source_account_id || paymentData?.source_account_number) {
      const matchedAccount = accounts.find(acc => {
        const accId = acc.id || acc.accountId;
        const accNumber = acc.accountNumber || acc.account_number;
        return (
          (paymentData.source_account_id && accId === paymentData.source_account_id) ||
          (paymentData.source_account_number && accNumber === paymentData.source_account_number)
        );
      });
      
      if (matchedAccount && !selectedSourceAccount) {
        setSelectedSourceAccount(matchedAccount);
        setShowAccountSelection(false);
        return;
      }
    }
    
    // If no pre-filled account, check if account selection is needed
    if (accounts.length > 1 && !selectedSourceAccount) {
      setShowAccountSelection(true);
    } else if (accounts.length === 1 && !selectedSourceAccount) {
      setSelectedSourceAccount(accounts[0]);
    }
  }, [accounts, loading, selectedSourceAccount, paymentData]);

  const loadData = async () => {
    try {
      setLoading(true);
      const accountsData = await fetchAccounts({ accessToken: session.accessToken }).catch(() => []);
      setAccounts(accountsData || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAccountSelect = (account) => {
    const accountToSet = {
      ...account,
      accountNumber: account.accountNumber || account.account_number || account.id
    };
    setSelectedSourceAccount(accountToSet);
    setShowAccountSelection(false);
  };

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
  const validateUPIId = (upiIdValue) => {
    if (!upiIdValue || !upiIdValue.trim()) {
      return { valid: false, error: language === 'hi-IN' ? 'UPI ID आवश्यक है' : 'UPI ID is required' };
    }
    
    const trimmed = upiIdValue.trim();
    
    // Check basic format first
    if (!trimmed.includes('@')) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'अमान्य UPI ID प्रारूप। सही प्रारूप: username@payee'
          : 'Invalid UPI ID format. Correct format: username@payee'
      };
    }
    
    const parts = trimmed.split('@');
    if (parts.length !== 2) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'अमान्य UPI ID प्रारूप। सही प्रारूप: username@payee'
          : 'Invalid UPI ID format. Correct format: username@payee'
      };
    }
    
    const [username, payee] = parts;
    
    if (trimmed.length < 5 || trimmed.length > 100) {
      return { 
        valid: false, 
        error: language === 'hi-IN' 
          ? 'UPI ID 5-100 वर्णों के बीच होना चाहिए'
          : 'UPI ID must be between 5-100 characters'
      };
    }
    
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
    
    return { valid: true, error: '' };
  };

  const handleAmountChange = (e) => {
    const value = e.target.value;
    setAmount(value);
    setAmountError('');
    
    // Validate amount in real-time
    if (value.trim() !== '') {
      const validation = validateAmount(value);
      if (!validation.valid) {
        setAmountError(validation.error);
      }
    }
  };

  const handleUpiIdChange = (e) => {
    const value = e.target.value;
    setUpiId(value);
    setUpiIdError('');
    
    // Validate UPI ID in real-time if it looks like a UPI ID
    if (value.trim() !== '') {
      const validation = validateUPIId(value);
      if (!validation.valid) {
        setUpiIdError(validation.error);
      }
    }
  };

  const handleScanQR = () => {
    // Trigger file input click
    qrFileInputRef.current?.click();
  };

  const handleQRFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setIsScanningQR(true);
    setUpiIdError('');
    
    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async (event) => {
        const imageBase64 = event.target.result;
        
        try {
          // Try client-side QR code scanning first
          const jsQR = (await import('jsqr')).default;
          
          const img = new Image();
          img.onload = async () => {
            try {
              // Create canvas to get image data
              const canvas = document.createElement('canvas');
              const ctx = canvas.getContext('2d');
              canvas.width = img.width;
              canvas.height = img.height;
              ctx.drawImage(img, 0, 0);
              
              const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
              const qrCode = jsQR(imageData.data, imageData.width, imageData.height);
              
              if (qrCode) {
                // QR code decoded successfully
                const qrData = qrCode.data;
                
                // Parse UPI QR code format
                let upiAddress = null;
                let amount = null;
                
                if (qrData.includes('upi://') || qrData.includes('UPI://')) {
                  // Parse UPI QR code
                  const url = new URL(qrData);
                  const params = new URLSearchParams(url.search);
                  
                  upiAddress = params.get('pa');
                  const amountStr = params.get('am');
                  
                  if (amountStr) {
                    amount = parseFloat(amountStr);
                  }
                } else if (qrData.includes('@')) {
                  // Try to extract UPI ID directly
                  const upiMatch = qrData.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)/);
                  if (upiMatch) {
                    upiAddress = upiMatch[1];
                  }
                }
                
                if (upiAddress) {
                  // Populate UPI ID field
                  setUpiId(upiAddress);
                  
                  // Populate amount if available
                  if (amount && amount > 0) {
                    setAmount(amount.toString());
                  }
                  
                  // Validate the extracted UPI ID
                  const validation = validateUPIId(upiAddress);
                  if (!validation.valid) {
                    setUpiIdError(validation.error);
                  }
                  
                  setIsScanningQR(false);
                  return;
                }
              }
              
              // If client-side scanning failed, try backend processing
              try {
                const result = await processQRCode({
                  imageBase64,
                  language,
                });
                
                if (result?.success && result?.upi_address) {
                  // Populate UPI ID field
                  setUpiId(result.upi_address);
                  
                  // Populate amount if available
                  if (result.amount && result.amount > 0) {
                    setAmount(result.amount.toString());
                  }
                  
                  // Validate the extracted UPI ID
                  const validation = validateUPIId(result.upi_address);
                  if (!validation.valid) {
                    setUpiIdError(validation.error);
                  }
                } else {
                  setUpiIdError(
                    language === 'hi-IN'
                      ? 'QR कोड से UPI पता निकाला नहीं जा सका'
                      : 'Could not extract UPI address from QR code'
                  );
                }
              } catch (backendError) {
                console.error('Backend QR processing error:', backendError);
                setUpiIdError(
                  language === 'hi-IN'
                    ? 'QR कोड प्रसंस्करण में त्रुटि'
                    : 'Error processing QR code'
                );
              }
            } catch (error) {
              console.error('QR code processing error:', error);
              setUpiIdError(
                language === 'hi-IN'
                  ? 'QR कोड प्रसंस्करण में त्रुटि'
                  : 'Error processing QR code'
              );
            } finally {
              setIsScanningQR(false);
            }
          };
          
          img.onerror = () => {
            setUpiIdError(
              language === 'hi-IN'
                ? 'छवि लोड करने में त्रुटि'
                : 'Error loading image'
            );
            setIsScanningQR(false);
          };
          
          img.src = imageBase64;
        } catch (error) {
          console.error('QR code scanning error:', error);
          setUpiIdError(
            language === 'hi-IN'
              ? 'QR कोड स्कैन करने में त्रुटि'
              : 'Error scanning QR code'
          );
          setIsScanningQR(false);
        }
      };
      
      reader.onerror = () => {
        setUpiIdError(
          language === 'hi-IN'
            ? 'छवि पढ़ने में त्रुटि'
            : 'Error reading image'
        );
        setIsScanningQR(false);
      };
      
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('QR code upload error:', error);
      setUpiIdError(
        language === 'hi-IN'
          ? 'QR कोड अपलोड करने में त्रुटि'
          : 'Error uploading QR code'
      );
      setIsScanningQR(false);
    }
    
    // Reset input
    e.target.value = '';
  };

  const handleProceed = async () => {
    // Validate all fields
    if (!selectedSourceAccount) {
      alert(language === 'hi-IN' ? 'कृपया खाता चुनें' : 'Please select source account');
      return;
    }
    
    // Validate amount
    const amountValidation = validateAmount(amount);
    if (!amountValidation.valid) {
      setAmountError(amountValidation.error);
      return;
    }
    
    // Validate UPI ID format
    const upiValidation = validateUPIId(upiId);
    if (!upiValidation.valid) {
      setUpiIdError(upiValidation.error);
      return;
    }
    
    // Additional validation: If it's a UPI ID format (contains @), ensure it's properly formatted
    // and warn if it looks suspicious (e.g., contains numbers that might be mistaken for phone)
    const trimmedUpiId = upiId.trim();
    if (trimmedUpiId.includes('@')) {
      const [username, payee] = trimmedUpiId.split('@');
      // Check if username looks like it might be a phone number but has extra characters
      // This helps catch cases like "321819600sss1@sunbank" which is invalid
      if (/^\d+[a-zA-Z]/.test(username) || /[a-zA-Z]\d+$/.test(username)) {
        // Username starts with digits but has letters mixed in - might be invalid
        // Allow it but the backend will validate
      }
    }
    
    // All validations passed - notify parent to proceed with payment
    // The backend will validate if the UPI ID exists in the system
    if (onPaymentReady) {
      onPaymentReady({
        source_account_id: selectedSourceAccount.id || selectedSourceAccount.accountId,
        source_account_number: selectedSourceAccount.accountNumber || selectedSourceAccount.account_number,
        amount: parseFloat(amount),
        recipient_identifier: upiId.trim(),
        remarks: remarks || '',
      });
    }
  };

  if (loading) {
    return (
      <div className="transfer-flow-loading">
        {language === 'hi-IN' ? 'लोड हो रहा है...' : 'Loading...'}
      </div>
    );
  }

  // Show account selection if multiple accounts
  if (showAccountSelection && accounts.length > 1) {
    return (
      <div className="transfer-flow">
        <div className="transfer-flow__header">
          <h3 className="transfer-flow__title">
            {language === 'hi-IN' ? 'स्रोत खाता चुनें' : 'Select Source Account'}
          </h3>
        </div>
        <div className="transfer-flow__content">
          <div className="transfer-flow__section">
            <label className="transfer-flow__label">
              {language === 'hi-IN' ? 'खाता चुनें' : 'Select Account'}
            </label>
            <div className="transfer-flow__accounts">
              {accounts.map((account) => (
                <button
                  key={account.id || account.accountId}
                  type="button"
                  className="transfer-flow__account-card"
                  onClick={() => handleAccountSelect(account)}
                >
                  <div className="transfer-flow__account-number">
                    {account.accountNumber || account.account_number || account.id}
                  </div>
                  <div className="transfer-flow__account-balance">
                    {account.currency || 'INR'} {parseFloat(account.balance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="transfer-flow">
      <div className="transfer-flow__header">
        <h3 className="transfer-flow__title">
          {language === 'hi-IN' ? 'UPI भुगतान' : 'UPI Payment'}
        </h3>
      </div>

      <div className="transfer-flow__content">
        {/* Always show account selection - required field */}
        <div className="transfer-flow__section">
          <label className="transfer-flow__label">
            {language === 'hi-IN' ? 'स्रोत खाता' : 'Source Account'}
          </label>
          {selectedSourceAccount ? (
            <div className="transfer-flow__selected-account">
              <span>{selectedSourceAccount.accountNumber || selectedSourceAccount.account_number || selectedSourceAccount.id}</span>
              {accounts.length > 1 && (
                <button
                  type="button"
                  className="transfer-flow__change-account"
                  onClick={() => setShowAccountSelection(true)}
                >
                  {language === 'hi-IN' ? 'बदलें' : 'Change'}
                </button>
              )}
            </div>
          ) : (
            <div className="transfer-flow__accounts">
              {accounts.map((account) => (
                <button
                  key={account.id || account.accountId}
                  type="button"
                  className="transfer-flow__account-card"
                  onClick={() => handleAccountSelect(account)}
                >
                  <div className="transfer-flow__account-number">
                    {account.accountNumber || account.account_number || account.id}
                  </div>
                  <div className="transfer-flow__account-balance">
                    {account.currency || 'INR'} {parseFloat(account.balance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="transfer-flow__section">
          <label className="transfer-flow__label" htmlFor="upi-amount">
            {language === 'hi-IN' ? 'राशि (₹)' : 'Amount (₹)'}
          </label>
          <input
            id="upi-amount"
            type="number"
            className={`transfer-flow__input ${amountError ? 'transfer-flow__input--error' : ''}`}
            value={amount}
            onChange={handleAmountChange}
            placeholder={language === 'hi-IN' ? 'राशि दर्ज करें' : 'Enter amount'}
            min="1"
            step="0.01"
          />
          {amountError && (
            <div className="transfer-flow__error-container">
              <span className="transfer-flow__error">{amountError}</span>
            </div>
          )}
        </div>

        <div className="transfer-flow__section">
          <label className="transfer-flow__label" htmlFor="upi-id">
            {language === 'hi-IN' ? 'UPI ID' : 'UPI ID'}
          </label>
          <div className="transfer-flow__input-group">
            <input
              id="upi-id"
              type="text"
              className={`transfer-flow__input ${upiIdError ? 'transfer-flow__input--error' : ''}`}
              value={upiId}
              onChange={handleUpiIdChange}
              placeholder={language === 'hi-IN' ? 'username@payee' : 'username@payee'}
            />
            <button
              type="button"
              className="transfer-flow__scan-qr-btn"
              onClick={handleScanQR}
              disabled={isScanningQR}
              title={language === 'hi-IN' ? 'QR कोड स्कैन करें' : 'Scan QR code'}
            >
              {isScanningQR ? (
                <>
                  <span className="transfer-flow__scan-qr-icon">⏳</span>
                  <span className="transfer-flow__scan-qr-text">
                    {language === 'hi-IN' ? 'स्कैन हो रहा है...' : 'Scanning...'}
                  </span>
                </>
              ) : (
                <>
                  <span className="transfer-flow__scan-qr-icon">📷</span>
                  <span className="transfer-flow__scan-qr-text">
                    {language === 'hi-IN' ? 'QR स्कैन करें' : 'Scan QR'}
                  </span>
                </>
              )}
            </button>
            <input
              ref={qrFileInputRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleQRFileChange}
            />
          </div>
          {upiIdError && (
            <div className="transfer-flow__error-container">
              <span className="transfer-flow__error">{upiIdError}</span>
              <span className="transfer-flow__error-hint">
                {language === 'hi-IN' 
                  ? 'सही प्रारूप: username@payee (उदाहरण: john@paytm, 9876543210@ybl)'
                  : 'Correct format: username@payee (e.g., john@paytm, 9876543210@ybl)'}
              </span>
            </div>
          )}
        </div>

        <div className="transfer-flow__section">
          <label className="transfer-flow__label" htmlFor="upi-remarks">
            {language === 'hi-IN' ? 'विवरण (वैकल्पिक)' : 'Remarks (Optional)'}
          </label>
          <input
            id="upi-remarks"
            type="text"
            className="transfer-flow__input"
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
            placeholder={language === 'hi-IN' ? 'विवरण दर्ज करें' : 'Enter remarks'}
          />
        </div>

        <button
          type="button"
          className="transfer-flow__submit"
          onClick={handleProceed}
          disabled={!amount || !upiId || !!upiIdError || !!amountError}
        >
          {language === 'hi-IN' ? 'आगे बढ़ें' : 'Proceed'}
        </button>
      </div>
    </div>
  );
};

UPIPaymentFlow.propTypes = {
  session: PropTypes.shape({
    accessToken: PropTypes.string,
  }).isRequired,
  language: PropTypes.string,
  onPaymentReady: PropTypes.func, // (paymentData) => void
  paymentData: PropTypes.shape({
    amount: PropTypes.number,
    recipient_identifier: PropTypes.string,
    remarks: PropTypes.string,
    source_account_id: PropTypes.string,
    source_account_number: PropTypes.string,
  }),
};

export default UPIPaymentFlow;

