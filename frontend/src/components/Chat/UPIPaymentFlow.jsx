import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { fetchAccounts } from '../../api/client.js';
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

  // Validate UPI ID format
  const validateUPIId = (upiIdValue) => {
    if (!upiIdValue || !upiIdValue.trim()) {
      return { valid: false, error: language === 'hi-IN' ? 'UPI ID आवश्यक है' : 'UPI ID is required' };
    }
    
    const trimmed = upiIdValue.trim();
    
    if (trimmed.length < 5 || trimmed.length > 100) {
      return { valid: false, error: language === 'hi-IN' ? 'UPI ID 5-100 अक्षरों का होना चाहिए' : 'UPI ID must be 5-100 characters' };
    }
    
    if (!trimmed.includes('@')) {
      return { valid: false, error: language === 'hi-IN' ? 'UPI ID में @ प्रतीक होना चाहिए' : 'UPI ID must contain @ symbol' };
    }
    
    const parts = trimmed.split('@');
    if (parts.length !== 2) {
      return { valid: false, error: language === 'hi-IN' ? 'UPI ID में केवल एक @ प्रतीक होना चाहिए' : 'UPI ID must have exactly one @ symbol' };
    }
    
    const [username, payee] = parts;
    
    if (username.length < 3 || username.length > 99) {
      return { valid: false, error: language === 'hi-IN' ? 'यूजरनेम 3-99 अक्षरों का होना चाहिए' : 'Username must be 3-99 characters' };
    }
    
    if (!/^[a-zA-Z0-9._-]+$/.test(username)) {
      return { valid: false, error: language === 'hi-IN' ? 'यूजरनेम में केवल अक्षर, संख्या, बिंदु, हाइफन और अंडरस्कोर हो सकते हैं' : 'Username can only contain letters, numbers, dots, hyphens, and underscores' };
    }
    
    if (payee.length < 2 || payee.length > 20) {
      return { valid: false, error: language === 'hi-IN' ? 'Payee 2-20 अक्षरों का होना चाहिए' : 'Payee must be 2-20 characters' };
    }
    
    if (!/^[a-zA-Z0-9]+$/.test(payee)) {
      return { valid: false, error: language === 'hi-IN' ? 'Payee में केवल अक्षर और संख्या हो सकते हैं' : 'Payee can only contain letters and numbers' };
    }
    
    return { valid: true, error: '' };
  };

  const handleUpiIdChange = (e) => {
    const value = e.target.value;
    setUpiId(value);
    setUpiIdError('');
    
    // Validate UPI ID in real-time if it looks like a UPI ID
    if (value.includes('@')) {
      const validation = validateUPIId(value);
      if (!validation.valid) {
        setUpiIdError(validation.error);
      }
    }
  };

  const handleProceed = () => {
    // Validate all fields
    if (!selectedSourceAccount) {
      alert(language === 'hi-IN' ? 'कृपया खाता चुनें' : 'Please select source account');
      return;
    }
    
    if (!amount || parseFloat(amount) <= 0) {
      alert(language === 'hi-IN' ? 'कृपया वैध राशि दर्ज करें' : 'Please enter a valid amount');
      return;
    }
    
    const validation = validateUPIId(upiId);
    if (!validation.valid) {
      setUpiIdError(validation.error);
      return;
    }
    
    // All validations passed - notify parent to proceed with payment
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
        {accounts.length > 1 && selectedSourceAccount && (
          <div className="transfer-flow__section">
            <label className="transfer-flow__label">
              {language === 'hi-IN' ? 'स्रोत खाता' : 'Source Account'}
            </label>
            <div className="transfer-flow__selected-account">
              <span>{selectedSourceAccount.accountNumber || selectedSourceAccount.account_number || selectedSourceAccount.id}</span>
              <button
                type="button"
                className="transfer-flow__change-account"
                onClick={() => setShowAccountSelection(true)}
              >
                {language === 'hi-IN' ? 'बदलें' : 'Change'}
              </button>
            </div>
          </div>
        )}

        <div className="transfer-flow__section">
          <label className="transfer-flow__label" htmlFor="upi-amount">
            {language === 'hi-IN' ? 'राशि (₹)' : 'Amount (₹)'}
          </label>
          <input
            id="upi-amount"
            type="number"
            className="transfer-flow__input"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder={language === 'hi-IN' ? 'राशि दर्ज करें' : 'Enter amount'}
            min="1"
            step="0.01"
          />
        </div>

        <div className="transfer-flow__section">
          <label className="transfer-flow__label" htmlFor="upi-id">
            {language === 'hi-IN' ? 'UPI ID' : 'UPI ID'}
          </label>
          <input
            id="upi-id"
            type="text"
            className="transfer-flow__input"
            value={upiId}
            onChange={handleUpiIdChange}
            placeholder={language === 'hi-IN' ? 'username@payee' : 'username@payee'}
          />
          {upiIdError && (
            <span className="transfer-flow__error" style={{ color: 'red', fontSize: '0.875rem', marginTop: '0.25rem', display: 'block' }}>
              {upiIdError}
            </span>
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
          disabled={!amount || !upiId || !!upiIdError}
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

