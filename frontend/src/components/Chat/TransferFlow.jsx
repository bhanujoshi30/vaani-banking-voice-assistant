import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { fetchBeneficiaries, createInternalTransfer, fetchAccounts } from '../../api/client.js';
import './TransferFlow.css';

/**
 * TransferFlow component - Handles money transfer with beneficiary management
 */
const TransferFlow = ({ session, language = 'en-IN', onTransferInitiated, transferData }) => {
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState(null);
  const [selectedSourceAccount, setSelectedSourceAccount] = useState(null);
  const [amount, setAmount] = useState('');
  const [remarks, setRemarks] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [transferring, setTransferring] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [otp, setOtp] = useState('');
  const [showOtp, setShowOtp] = useState(false);
  const [showAccountSelection, setShowAccountSelection] = useState(false);
  const FIXED_OTP = '12345';

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    // Auto-fill from transfer data if available
    if (transferData) {
      if (transferData.amount) {
        setAmount(transferData.amount.toString());
      }
      if (transferData.remarks) {
        setRemarks(transferData.remarks);
      }
    }
  }, [transferData]);

  useEffect(() => {
    // Auto-select beneficiary based on selector
    if (transferData?.beneficiary_selector && beneficiaries.length > 0) {
      const selector = transferData.beneficiary_selector.toLowerCase();
      let beneficiary = null;
      
      if (selector === 'first') {
        beneficiary = beneficiaries[0];
      } else if (selector === 'last') {
        beneficiary = beneficiaries[beneficiaries.length - 1];
      } else if (selector.startsWith('name:')) {
        const name = selector.replace('name:', '').trim();
        beneficiary = beneficiaries.find(b => 
          b.name.toLowerCase().includes(name.toLowerCase())
        );
      } else if (selector.startsWith('account:')) {
        const accountNum = selector.replace('account:', '').trim();
        beneficiary = beneficiaries.find(b => 
          b.accountNumber.includes(accountNum)
        );
      }
      
      if (beneficiary) {
        setSelectedBeneficiary(beneficiary);
      }
    }
  }, [beneficiaries, transferData]);

  useEffect(() => {
    // Only set account after accounts are loaded
    if (loading) return;
    
    // Always use accounts from API - don't use session fallback
    if (accounts.length === 0) {
      // No accounts found - this is an error state
      console.error('No accounts found from API');
      return;
    }
    
    // First, check if source account is pre-filled from transferData
    if (transferData?.source_account_id || transferData?.source_account_number) {
      const matchedAccount = accounts.find(acc => {
        const accId = acc.id || acc.accountId;
        const accNumber = acc.accountNumber || acc.account_number;
        return (
          (transferData.source_account_id && accId === transferData.source_account_id) ||
          (transferData.source_account_number && accNumber === transferData.source_account_number)
        );
      });
      
      if (matchedAccount && !selectedSourceAccount) {
        setSelectedSourceAccount(matchedAccount);
        setShowAccountSelection(false); // Don't show selection if account is pre-filled
        return;
      }
    }
    
    // If no pre-filled account, check if account selection is needed
    if (accounts.length > 1 && !selectedSourceAccount) {
      setShowAccountSelection(true);
    } else if (accounts.length === 1 && !selectedSourceAccount) {
      setSelectedSourceAccount(accounts[0]);
    }
  }, [accounts, loading, selectedSourceAccount, transferData]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [beneficiariesData, accountsData] = await Promise.all([
        fetchBeneficiaries({ accessToken: session.accessToken }),
        fetchAccounts({ accessToken: session.accessToken }).catch(() => [])
      ]);
      setBeneficiaries(beneficiariesData || []);
      setAccounts(accountsData || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAccountSelect = (account) => {
    // Ensure account has accountNumber
    const accountToSet = {
      ...account,
      accountNumber: account.accountNumber || account.account_number || account.id
    };
    setSelectedSourceAccount(accountToSet);
    setShowAccountSelection(false);
  };

  const handleTransferClick = () => {
    if (!selectedBeneficiary || !amount || !selectedSourceAccount) {
      return;
    }
    setShowConfirmation(true);
  };

  const handleConfirmTransfer = () => {
    setShowConfirmation(false);
    setShowOtp(true);
  };

  const handleOtpSubmit = async () => {
    if (otp !== FIXED_OTP) {
      alert(language === 'hi-IN' ? 'गलत OTP' : 'Invalid OTP');
      return;
    }

    try {
      setTransferring(true);
      if (!selectedSourceAccount) {
        alert(language === 'hi-IN' ? 'कृपया खाता चुनें' : 'Please select source account');
        return;
      }

      // Use account ID if available (UUID), otherwise use account number
      // The backend can handle both
      const sourceAccountId = selectedSourceAccount.id || 
                              selectedSourceAccount.accountNumber || 
                              selectedSourceAccount.account_number;
      
      if (!sourceAccountId) {
        alert(language === 'hi-IN' ? 'खाता संख्या नहीं मिली' : 'Account number not found');
        setTransferring(false);
        return;
      }

      console.log('Transfer request:', {
        sourceAccountId,
        destinationAccountNumber: selectedBeneficiary.accountNumber,
        amount: parseFloat(amount),
        selectedSourceAccount: {
          id: selectedSourceAccount.id,
          accountNumber: selectedSourceAccount.accountNumber || selectedSourceAccount.account_number,
          ...selectedSourceAccount
        }
      });

      const result = await createInternalTransfer({
        accessToken: session.accessToken,
        payload: {
          sourceAccountId: sourceAccountId,
          destinationAccountNumber: selectedBeneficiary.accountNumber,
          amount: parseFloat(amount),
          currency: 'INR',
          remarks: remarks || `Transfer to ${selectedBeneficiary.name}`,
        },
      });

      console.log('Transfer API result (raw):', result);
      console.log('Result keys:', result ? Object.keys(result) : 'null');

      // Prepare receipt data - handle both camelCase and snake_case from API
      // The API returns the receipt object directly (from json?.data)
      // Use current timestamp if API doesn't provide one
      const currentTimestamp = new Date().toISOString();
      
      const receiptData = {
        amount: result?.amount,
        currency: result?.currency,
        sourceAccountNumber: result?.sourceAccountNumber || result?.source_account_number || selectedSourceAccount?.accountNumber || selectedSourceAccount?.account_number,
        destinationAccountNumber: result?.destinationAccountNumber || result?.destination_account_number || selectedBeneficiary?.accountNumber,
        beneficiaryName: result?.beneficiaryName || result?.beneficiary_name || selectedBeneficiary?.name || 'N/A',
        timestamp: result?.timestamp || currentTimestamp, // Use current time if not provided
        referenceId: result?.referenceId || result?.reference_id || 'N/A',
        description: result?.description || remarks || `Transfer to ${selectedBeneficiary.name}`,
      };
      
      console.log('Transfer API result (raw):', result);
      console.log('Final receipt data:', receiptData);

      if (onTransferInitiated) {
        onTransferInitiated(result, receiptData);
      }
      
      // Reset form
      setSelectedBeneficiary(null);
      setAmount('');
      setRemarks('');
      setOtp('');
      setShowOtp(false);
      setShowConfirmation(false);
      setShowOtp(false);
    } catch (error) {
      console.error('Error initiating transfer:', error);
      alert(error.message || (language === 'hi-IN' ? 'ट्रांसफर में त्रुटि' : 'Error initiating transfer'));
    } finally {
      setTransferring(false);
    }
  };

  const handleCancel = () => {
    setShowConfirmation(false);
    setShowOtp(false);
    setOtp('');
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
                  key={account.id || account.accountNumber}
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

  if (beneficiaries.length === 0) {
    return (
      <div className="transfer-flow-empty">
        <div className="transfer-flow-empty__icon">👤</div>
        <div className="transfer-flow-empty__title">
          {language === 'hi-IN' ? 'कोई लाभार्थी नहीं' : 'No Beneficiaries'}
        </div>
        <div className="transfer-flow-empty__message">
          {language === 'hi-IN' 
            ? 'ट्रांसफर करने के लिए, कृपया पहले एक लाभार्थी बनाएं।' 
            : 'To make a transfer, please create a beneficiary first.'}
        </div>
        <button
          type="button"
          className="transfer-flow-empty__button"
          onClick={() => window.location.href = '/beneficiaries'}
        >
          {language === 'hi-IN' ? 'लाभार्थी बनाएं' : 'Create Beneficiary'}
        </button>
      </div>
    );
  }

  return (
    <div className="transfer-flow">
      <div className="transfer-flow__header">
        <h3 className="transfer-flow__title">
          {language === 'hi-IN' ? 'धन हस्तांतरण' : 'Money Transfer'}
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
          <label className="transfer-flow__label">
            {language === 'hi-IN' ? 'लाभार्थी चुनें' : 'Select Beneficiary'}
          </label>
          <div className="transfer-flow__beneficiaries">
            {beneficiaries.map((beneficiary) => (
              <button
                key={beneficiary.id}
                type="button"
                className={`transfer-flow__beneficiary ${selectedBeneficiary?.id === beneficiary.id ? 'transfer-flow__beneficiary--selected' : ''}`}
                onClick={() => setSelectedBeneficiary(beneficiary)}
              >
                <div className="transfer-flow__beneficiary-name">{beneficiary.name}</div>
                <div className="transfer-flow__beneficiary-account">{beneficiary.accountNumber}</div>
                <div className="transfer-flow__beneficiary-bank">{beneficiary.bankName || 'Sun National Bank'}</div>
              </button>
            ))}
          </div>
        </div>

        {selectedBeneficiary && (
          <>
            <div className="transfer-flow__section">
              <label className="transfer-flow__label" htmlFor="transfer-amount">
                {language === 'hi-IN' ? 'राशि (₹)' : 'Amount (₹)'}
              </label>
              <input
                id="transfer-amount"
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
              <label className="transfer-flow__label" htmlFor="transfer-remarks">
                {language === 'hi-IN' ? 'विवरण (वैकल्पिक)' : 'Remarks (Optional)'}
              </label>
              <input
                id="transfer-remarks"
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
              onClick={handleTransferClick}
              disabled={!amount || transferring}
            >
              {language === 'hi-IN' ? 'हस्तांतरण करें' : 'Transfer Money'}
            </button>
          </>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="transfer-flow__modal">
          <div className="transfer-flow__modal-content">
            <h3 className="transfer-flow__modal-title">
              {language === 'hi-IN' ? 'ट्रांसफर की पुष्टि करें' : 'Confirm Transfer'}
            </h3>
            <div className="transfer-flow__modal-details">
              <div className="transfer-flow__modal-row">
                <span>{language === 'hi-IN' ? 'स्रोत खाता:' : 'From Account:'}</span>
                <strong>{selectedSourceAccount?.accountNumber || selectedSourceAccount?.account_number || selectedSourceAccount?.id || '—'}</strong>
              </div>
              <div className="transfer-flow__modal-row">
                <span>{language === 'hi-IN' ? 'लाभार्थी:' : 'Beneficiary:'}</span>
                <strong>{selectedBeneficiary.name}</strong>
              </div>
              <div className="transfer-flow__modal-row">
                <span>{language === 'hi-IN' ? 'लाभार्थी खाता संख्या:' : 'Beneficiary Account:'}</span>
                <strong>{selectedBeneficiary.accountNumber}</strong>
              </div>
              <div className="transfer-flow__modal-row">
                <span>{language === 'hi-IN' ? 'राशि:' : 'Amount:'}</span>
                <strong>₹{parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
              </div>
              {remarks && (
                <div className="transfer-flow__modal-row">
                  <span>{language === 'hi-IN' ? 'विवरण:' : 'Remarks:'}</span>
                  <strong>{remarks}</strong>
                </div>
              )}
            </div>
            <div className="transfer-flow__modal-actions">
              <button
                type="button"
                className="transfer-flow__modal-cancel"
                onClick={handleCancel}
              >
                {language === 'hi-IN' ? 'रद्द करें' : 'Cancel'}
              </button>
              <button
                type="button"
                className="transfer-flow__modal-confirm"
                onClick={handleConfirmTransfer}
              >
                {language === 'hi-IN' ? 'पुष्टि करें' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* OTP Modal */}
      {showOtp && (
        <div className="transfer-flow__modal">
          <div className="transfer-flow__modal-content">
            <h3 className="transfer-flow__modal-title">
              {language === 'hi-IN' ? 'OTP दर्ज करें' : 'Enter OTP'}
            </h3>
            <p className="transfer-flow__modal-message">
              {language === 'hi-IN' 
                ? 'कृपया अपना OTP दर्ज करें' 
                : 'Please enter your OTP to complete the transfer'}
            </p>
            <input
              type="text"
              className="transfer-flow__otp-input"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              placeholder={language === 'hi-IN' ? 'OTP दर्ज करें' : 'Enter OTP'}
              maxLength="5"
            />
            <div className="transfer-flow__modal-actions">
              <button
                type="button"
                className="transfer-flow__modal-cancel"
                onClick={handleCancel}
              >
                {language === 'hi-IN' ? 'रद्द करें' : 'Cancel'}
              </button>
              <button
                type="button"
                className="transfer-flow__modal-confirm"
                onClick={handleOtpSubmit}
                disabled={!otp || transferring}
              >
                {transferring 
                  ? (language === 'hi-IN' ? 'हस्तांतरण हो रहा है...' : 'Transferring...')
                  : (language === 'hi-IN' ? 'सबमिट करें' : 'Submit')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

TransferFlow.propTypes = {
  session: PropTypes.shape({
    accessToken: PropTypes.string,
    user: PropTypes.shape({
      accountSummary: PropTypes.array,
    }),
  }).isRequired,
  language: PropTypes.string,
  onTransferInitiated: PropTypes.func,
  transferData: PropTypes.shape({
    amount: PropTypes.number,
    beneficiary_selector: PropTypes.string,
    remarks: PropTypes.string,
  }),
};

export default TransferFlow;

