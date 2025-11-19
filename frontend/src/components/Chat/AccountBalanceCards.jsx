import PropTypes from 'prop-types';
import './AccountBalanceCards.css';

/**
 * AccountBalanceCards component - Displays account balances in card format
 */
const AccountBalanceCards = ({ accounts, language = 'en-IN' }) => {
  if (!accounts || accounts.length === 0) {
    return (
      <div className="balance-cards-empty">
        {language === 'hi-IN' ? 'कोई खाता नहीं मिला' : 'No accounts found'}
      </div>
    );
  }

  const formatAmount = (amount, currency = 'INR') => {
    const num = Number(amount) || 0;
    const symbol = currency === 'INR' ? '₹' : currency;
    return `${symbol}${num.toLocaleString('en-IN', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  const getAccountTypeLabel = (type) => {
    const cleanType = (type || '').replace('AccountType.', '').replace(/_/g, ' ');
    
    if (language === 'hi-IN') {
      const typeMap = {
        'savings': 'बचत खाता',
        'current': 'चालू खाता',
        'salary': 'वेतन खाता',
        'fixed deposit': 'सावधि जमा',
        'recurring deposit': 'आवर्ती जमा',
      };
      
      for (const [key, value] of Object.entries(typeMap)) {
        if (cleanType.toLowerCase().includes(key)) {
          return value;
        }
      }
      
      return cleanType;
    }
    
    // English labels
    return cleanType
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  const getAccountIcon = (type) => {
    const lowerType = (type || '').toLowerCase();
    if (lowerType.includes('savings')) return '💰';
    if (lowerType.includes('current')) return '💳';
    if (lowerType.includes('salary')) return '💼';
    if (lowerType.includes('fixed')) return '📊';
    return '🏦';
  };

  // Calculate total balance
  const totalBalance = accounts.reduce((sum, acc) => {
    return sum + (Number(acc.balance) || 0);
  }, 0);

  return (
    <div className="balance-cards-container">
      {accounts.length > 1 && (
        <div className="balance-cards-total">
          <div className="balance-cards-total__label">
            {language === 'hi-IN' ? 'कुल बैलेंस' : 'Total Balance'}
          </div>
          <div className="balance-cards-total__amount">
            {formatAmount(totalBalance)}
          </div>
        </div>
      )}
      
      <div className="balance-cards-grid">
        {accounts.map((account, index) => (
          <div key={index} className="balance-card">
            <div className="balance-card__header">
              <div className="balance-card__icon">{getAccountIcon(account.account_type)}</div>
              <div className="balance-card__info">
                <div className="balance-card__type">{getAccountTypeLabel(account.account_type)}</div>
                <div className="balance-card__number">
                  {account.account_number || account.accountNumber || '—'}
                </div>
              </div>
            </div>
            
            <div className="balance-card__balance">
              <div className="balance-card__balance-label">
                {language === 'hi-IN' ? 'उपलब्ध बैलेंस' : 'Available Balance'}
              </div>
              <div className="balance-card__balance-amount">
                {formatAmount(account.balance, account.currency || 'INR')}
              </div>
            </div>
            
            {account.status && (
              <div className="balance-card__status">
                <span className={`balance-card__status-badge balance-card__status-badge--${(account.status || 'active').toLowerCase()}`}>
                  {account.status}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

AccountBalanceCards.propTypes = {
  accounts: PropTypes.arrayOf(
    PropTypes.shape({
      account_type: PropTypes.string,
      account_number: PropTypes.string,
      accountNumber: PropTypes.string,
      balance: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      currency: PropTypes.string,
      status: PropTypes.string,
    })
  ).isRequired,
  language: PropTypes.string,
};

export default AccountBalanceCards;

