import { useState } from 'react';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import './TransactionTable.css';

/**
 * TransactionTable component - Displays transactions in an expandable table format
 */
const TransactionTable = ({
  transactions,
  language = 'en-IN',
  accountNumber,
  accounts,
  accountTransactions = {},
  totalCount,
}) => {
  const navigate = useNavigate();
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedAccount, setSelectedAccount] = useState(accountNumber || 'all');

  const getTransactionsForAccount = (accountId) => {
    if (!accountId || accountId === 'all') {
      return transactions || [];
    }
    if (accountTransactions && accountTransactions[accountId]) {
      return accountTransactions[accountId];
    }
    return (transactions || []).filter((txn) => txn.account_number === accountId);
  };

  const baseTransactions = getTransactionsForAccount(selectedAccount);

  if (!baseTransactions || baseTransactions.length === 0) {
    return (
      <div className="transaction-table-empty">
        {language === 'hi-IN'
          ? 'इस खाते के लिए हाल के लेनदेन उपलब्ध नहीं हैं।'
          : 'No recent transactions found for this selection.'}
      </div>
    );
  }

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString(language === 'hi-IN' ? 'hi-IN' : 'en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const formatTime = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleTimeString(language === 'hi-IN' ? 'hi-IN' : 'en-IN', {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  };

  const formatAmount = (amount) => {
    const num = Number(amount) || 0;
    return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const isDebit = (type) => {
    const lowerType = (type || '').toLowerCase();
    return ['withdraw', 'debit', 'payment', 'transfer_out', 'upi', 'bill'].some(
      (token) => lowerType.includes(token)
    );
  };

  const getTransactionTypeLabel = (type) => {
    const lowerType = (type || '').toLowerCase();
    if (lowerType.includes('transfer_out')) return language === 'hi-IN' ? 'ट्रांसफर आउट' : 'Transfer Out';
    if (lowerType.includes('transfer_in')) return language === 'hi-IN' ? 'ट्रांसफर इन' : 'Transfer In';
    if (lowerType.includes('payment')) return language === 'hi-IN' ? 'भुगतान' : 'Payment';
    if (lowerType.includes('withdraw')) return language === 'hi-IN' ? 'निकासी' : 'Withdrawal';
    if (lowerType.includes('deposit')) return language === 'hi-IN' ? 'जमा' : 'Deposit';
    return type || '—';
  };

  // Sort transactions
  const sortedTransactions = [...baseTransactions].sort((a, b) => {
    let aVal, bVal;
    
    if (sortBy === 'date') {
      aVal = new Date(a.date || a.occurred_at || a.occurredAt || 0).getTime();
      bVal = new Date(b.date || b.occurred_at || b.occurredAt || 0).getTime();
    } else if (sortBy === 'amount') {
      aVal = Number(a.amount || 0);
      bVal = Number(b.amount || 0);
    } else {
      return 0;
    }
    
    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
  });

  // Always show only top 5 transactions
  const displayedTransactions = sortedTransactions.slice(0, 5);

  const handleViewAll = () => {
    navigate('/transactions', {
      state: {
        accountNumber: selectedAccount !== 'all' ? selectedAccount : null,
      },
    });
  };

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  return (
    <div className="transaction-table-container">
      <div className="transaction-table-header">
        <h3 className="transaction-table-title">
          {language === 'hi-IN' ? 'लेनदेन सारांश' : 'Transaction Summary'}
        </h3>
        <div className="transaction-table-stats">
          {accounts && accounts.length > 1 && (
            <select
              className="transaction-table__account-select"
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
            >
              <option value="all">{language === 'hi-IN' ? 'सभी खाते' : 'All Accounts'}</option>
              {accounts.map((acc) => {
                const accountType = acc.account_type?.replace('AccountType.', '') || 'Account';
                const accountNumber = acc.account_number || '';
                const lastFour = accountNumber.length >= 4 ? accountNumber.slice(-4) : accountNumber;
                const displayText = lastFour ? `${accountType} • ${lastFour}` : accountType;
                return (
                  <option key={acc.account_number} value={acc.account_number}>
                    {displayText}
                  </option>
                );
              })}
            </select>
          )}
          <span className="transaction-count">
            {selectedAccount === 'all'
              ? (totalCount ?? baseTransactions.length)
              : (
                accounts?.find((acc) => acc.account_number === selectedAccount)?.transaction_count ??
                baseTransactions.length
              )}{' '}
            {language === 'hi-IN' ? 'लेनदेन' : 'transactions'}
          </span>
        </div>
      </div>

      <div className="transaction-table-wrapper">
        <table className="transaction-table">
          <thead>
            <tr>
              <th 
                className="transaction-table__col-date"
                onClick={() => handleSort('date')}
              >
                {language === 'hi-IN' ? 'तारीख' : 'Date'}
                {sortBy === 'date' && (
                  <span className="sort-indicator">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
              <th className="transaction-table__col-type">
                {language === 'hi-IN' ? 'प्रकार' : 'Type'}
              </th>
              <th className="transaction-table__col-description">
                {language === 'hi-IN' ? 'विवरण' : 'Description'}
              </th>
              <th 
                className="transaction-table__col-amount"
                onClick={() => handleSort('amount')}
              >
                {language === 'hi-IN' ? 'राशि' : 'Amount'}
                {sortBy === 'amount' && (
                  <span className="sort-indicator">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
              <th className="transaction-table__col-status">
                {language === 'hi-IN' ? 'स्थिति' : 'Status'}
              </th>
            </tr>
          </thead>
          <tbody>
            {displayedTransactions.map((txn, index) => {
              const debit = isDebit(txn.type || txn.transaction_type);
              const amount = Number(txn.amount || 0);
              
              return (
                <tr key={index} className="transaction-table__row">
                  <td className="transaction-table__col-date">
                    <div className="transaction-date">
                      <span className="transaction-date__day">
                        {formatDate(txn.date || txn.occurred_at || txn.occurredAt)}
                      </span>
                      <span className="transaction-date__time">
                        {formatTime(txn.date || txn.occurred_at || txn.occurredAt)}
                      </span>
                    </div>
                  </td>
                  <td className="transaction-table__col-type">
                    <span className={`transaction-type transaction-type--${debit ? 'debit' : 'credit'}`}>
                      {getTransactionTypeLabel(txn.type || txn.transaction_type)}
                    </span>
                  </td>
                  <td className="transaction-table__col-description">
                    <div className="transaction-description">
                      <span className="transaction-description__text">
                        {txn.description || txn.counterparty || '—'}
                      </span>
                      {txn.counterparty && (
                        <span className="transaction-description__counterparty">
                          {txn.counterparty}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="transaction-table__col-amount">
                    <span className={`transaction-amount transaction-amount--${debit ? 'debit' : 'credit'}`}>
                      {debit ? '-' : '+'}{formatAmount(amount)}
                    </span>
                  </td>
                  <td className="transaction-table__col-status">
                    <span className={`transaction-status transaction-status--${(txn.status || 'completed').toLowerCase()}`}>
                      {txn.status || 'Completed'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="transaction-table-footer">
        <button
          type="button"
          className="transaction-table__view-all-btn"
          onClick={handleViewAll}
        >
          <span>{language === 'hi-IN' ? 'सभी लेनदेन देखें' : 'View All Transactions'}</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

TransactionTable.propTypes = {
  transactions: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string,
      occurred_at: PropTypes.string,
      occurredAt: PropTypes.string,
      type: PropTypes.string,
      transaction_type: PropTypes.string,
      amount: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      description: PropTypes.string,
      counterparty: PropTypes.string,
      status: PropTypes.string,
      account_number: PropTypes.string,
    })
  ).isRequired,
  language: PropTypes.string,
  accountNumber: PropTypes.string,
  accounts: PropTypes.arrayOf(
    PropTypes.shape({
      account_number: PropTypes.string,
      account_type: PropTypes.string,
      transaction_count: PropTypes.number,
    })
  ),
  accountTransactions: PropTypes.object,
  totalCount: PropTypes.number,
};

export default TransactionTable;

