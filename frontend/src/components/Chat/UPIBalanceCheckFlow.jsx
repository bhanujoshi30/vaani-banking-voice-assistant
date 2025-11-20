import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './TransferFlow.css'; // Reuse TransferFlow styles

/**
 * UPIBalanceCheckFlow component - Handles UPI balance check with account selection
 * Simple flow: Select account → Show PIN modal directly (no message sent)
 */
const UPIBalanceCheckFlow = ({ session, language = 'en-IN', balanceData, onAccountSelected }) => {
  const [selectedAccount, setSelectedAccount] = useState(null);
  const accounts = balanceData?.accounts || [];

  const handleAccountSelect = (account) => {
    setSelectedAccount(account);
    
    // Directly trigger PIN modal - no message sent to backend
    if (onAccountSelected) {
      const accountNumber = account.accountNumber || account.account_number;
      onAccountSelected({
        source_account_id: account.id || account.accountId,
        source_account_number: accountNumber,
        account: account
      });
    }
  };

  // Auto-select single account and trigger PIN modal
  useEffect(() => {
    if (accounts.length === 1 && !selectedAccount && onAccountSelected) {
      const account = accounts[0];
      setSelectedAccount(account);
      const accountNumber = account.accountNumber || account.account_number;
      onAccountSelected({
        source_account_id: account.id || account.accountId,
        source_account_number: accountNumber,
        account: account
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accounts.length, onAccountSelected]); // Only run when accounts change

  // Show account selection if multiple accounts
  if (accounts.length > 1 && !selectedAccount) {
    return (
      <div className="transfer-flow">
        <div className="transfer-flow__header">
          <h3 className="transfer-flow__title">
            {language === 'hi-IN' ? 'UPI बैलेंस जांच के लिए खाता चुनें' : 'Select Account for UPI Balance Check'}
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
                  key={account.id || account.accountId || account.accountNumber || account.account_number}
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

  // If account selected or single account, PIN modal is shown by parent
  // Don't render anything - just show account selection cards if needed
  if (selectedAccount || accounts.length === 1) {
    return null; // PIN modal will be shown by parent component
  }

  // Show account selection cards for multiple accounts
  return null; // This case is handled above in the accounts.length > 1 check
};

UPIBalanceCheckFlow.propTypes = {
  session: PropTypes.object.isRequired,
  language: PropTypes.string,
  balanceData: PropTypes.shape({
    accounts: PropTypes.arrayOf(PropTypes.object),
    pending_account_selection: PropTypes.bool,
  }),
  onAccountSelected: PropTypes.func, // (accountData) => void - Directly triggers PIN modal
};

export default UPIBalanceCheckFlow;

